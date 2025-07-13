import random
import time
import os
from moneySmartz.models import Player, BankAccount, Card, Loan, Asset
from moneySmartz.screens.life_event_screens import HousingScreen, FamilyPlanningScreen
from moneySmartz.screens.base_screens import EndGameScreen

class Game:
    """
    Main game class that manages the game state and logic.
    """
    def __init__(self):
        self.player = None
        self.current_month = 1
        self.current_year = 0
        self.game_over = False
        self.events = self.initialize_events()
        self.gui_manager = None  # Will be set by the main script

    def initialize_events(self):
        """Initialize the random events that can occur during gameplay."""
        # Define possible random events
        events = {
            "positive": [
                {"name": "Tax Refund", "description": "You received a tax refund!", "cash_effect": lambda: random.randint(100, 1000)},
                {"name": "Birthday Gift", "description": "You received money as a birthday gift!", "cash_effect": lambda: random.randint(20, 200)},
                {"name": "Found Money", "description": "You found money on the ground!", "cash_effect": lambda: random.randint(5, 50)},
                {"name": "Bonus", "description": "You received a bonus at work!", "cash_effect": lambda: int(self.player.salary * random.uniform(0.01, 0.1)) if self.player.salary > 0 else 0},
            ],
            "negative": [
                {"name": "Car Repair", "description": "Your car needs repairs.", "cash_effect": lambda: -random.randint(100, 2000) if any(a.asset_type == "Car" for a in self.player.assets) else 0},
                {"name": "Medical Bill", "description": "You have unexpected medical expenses.", "cash_effect": lambda: -random.randint(50, 5000)},
                {"name": "Lost Wallet", "description": "You lost your wallet!", "cash_effect": lambda: -min(50, self.player.cash)},
                {"name": "Phone Repair", "description": "Your phone screen cracked.", "cash_effect": lambda: -random.randint(50, 300)},
            ]
        }
        return events

    def start_game(self):
        """Start a new game in text mode (legacy)."""
        self.clear_screen()
        print("=" * 60)
        print("WELCOME TO MONEY SMARTZ: THE FINANCIAL LIFE SIMULATOR")
        print("=" * 60)
        print("\nInspired by the classic Oregon Trail, this game will take you")
        print("through the financial journey of life, from your first bank account")
        print("to retirement, with all the ups and downs along the way.")
        print("\nMake wise financial decisions and see how they affect your life!")
        print("\n" + "=" * 60)

        name = input("\nEnter your name: ")
        self.player = Player(name)

        print(f"\nWelcome, {self.player.name}! You're a 16-year-old high school student.")
        print("Your parents suggest that you should open your first bank account.")

        choice = self.get_choice("Do you want to open a bank account?", ["Yes", "No"])
        if choice == "Yes":
            self.player.bank_account = BankAccount()
            self.player.bank_account.deposit(50)  # Parents give you $50 to start
            print("\nCongratulations! You've opened your first checking account.")
            print("Your parents deposited $50 to get you started.")

            choice = self.get_choice("Would you like a debit card with your account?", ["Yes", "No"])
            if choice == "Yes":
                self.player.debit_card = Card("Debit")
                print("\nYou now have a debit card linked to your checking account.")
        else:
            print("\nYou decided not to open a bank account yet. You can do this later.")

        input("\nPress Enter to begin your financial journey...")
        self.game_loop()

    def game_loop(self):
        """Main game loop for text mode (legacy)."""
        while not self.game_over:
            self.current_month += 1
            if self.current_month > 12:
                self.current_month = 1
                self.current_year += 1
                self.player.age += 1

                # Apply interest to savings
                if self.player.bank_account and self.player.bank_account.account_type == "Savings":
                    self.player.bank_account.apply_interest()

                # Age assets
                for asset in self.player.assets:
                    asset.age_asset()

            # Process monthly income and expenses
            self.process_monthly_finances()

            # Random events
            if random.random() < 0.3:  # 30% chance of an event each month
                self.trigger_random_event()

            # Life stage events based on age
            self.check_life_stage_events()

            # Display status and get player action
            self.display_status()
            self.get_player_action()

            # Check game over conditions
            if self.player.age >= 65:  # Retirement age
                self.end_game("retirement")

    def process_monthly_finances(self):
        """Process monthly income and expenses."""
        # Process income
        if self.player.job:
            monthly_income = self.player.salary / 12
            self.player.cash += monthly_income

            # Auto deposit to bank if account exists
            if self.player.bank_account:
                deposit_amount = monthly_income * 0.8  # 80% of income goes to bank
                self.player.bank_account.deposit(deposit_amount)
                self.player.cash -= deposit_amount

        # Process loan payments
        for loan in self.player.loans:
            if self.player.cash >= loan.monthly_payment:
                self.player.cash -= loan.monthly_payment
                loan.make_payment(loan.monthly_payment)
            elif self.player.bank_account and self.player.bank_account.balance >= loan.monthly_payment:
                self.player.bank_account.withdraw(loan.monthly_payment)
                loan.make_payment(loan.monthly_payment)
            elif self.player.credit_card and (self.player.credit_card.balance + loan.monthly_payment) <= self.player.credit_card.limit:
                self.player.credit_card.charge(loan.monthly_payment)
                loan.make_payment(loan.monthly_payment)
            else:
                # Missed payment - credit score impact
                self.player.credit_score -= 30
                print(f"You missed a payment on your {loan.loan_type} loan. Your credit score has been affected.")

        # Process credit card minimum payments (5% of balance)
        if self.player.credit_card and self.player.credit_card.balance > 0:
            min_payment = max(25, self.player.credit_card.balance * 0.05)  # Minimum $25 or 5% of balance

            if self.player.cash >= min_payment:
                self.player.cash -= min_payment
                self.player.credit_card.pay(min_payment)
            elif self.player.bank_account and self.player.bank_account.balance >= min_payment:
                self.player.bank_account.withdraw(min_payment)
                self.player.credit_card.pay(min_payment)
            else:
                # Missed payment - credit score impact
                self.player.credit_score -= 50
                print("You missed your credit card payment. Your credit score has been severely affected.")

        # Process living expenses
        living_expenses = 1000  # Base living expenses

        if any(a.asset_type == "House" for a in self.player.assets):
            living_expenses += 500  # Additional expenses for homeowners

        if any(a.asset_type == "Car" for a in self.player.assets):
            living_expenses += 200  # Car maintenance and gas

        if self.player.family:
            living_expenses += 500 * len(self.player.family)  # Additional expenses per family member

        # Adjust for inflation over time (2% per year)
        inflation_factor = (1.02) ** self.current_year
        living_expenses *= inflation_factor

        # Pay living expenses
        if self.player.cash >= living_expenses:
            self.player.cash -= living_expenses
        elif self.player.bank_account and self.player.bank_account.balance >= living_expenses:
            self.player.bank_account.withdraw(living_expenses)
        elif self.player.credit_card and (self.player.credit_card.balance + living_expenses) <= self.player.credit_card.limit:
            self.player.credit_card.charge(living_expenses)
        else:
            # Couldn't pay living expenses - game over?
            print("You couldn't afford your living expenses this month!")
            # For now, just reduce credit score
            self.player.credit_score -= 20

    def trigger_random_event(self):
        """Trigger a random financial event."""
        # Decide if it's a positive or negative event
        event_type = "positive" if random.random() < 0.5 else "negative"
        event = random.choice(self.events[event_type])

        cash_effect = event["cash_effect"]()

        # Only show events that have an effect
        if cash_effect != 0:
            # Use GUI screen if GUI manager is available, otherwise use console
            if hasattr(self, 'gui_manager') and self.gui_manager:
                from moneySmartz.screens.random_event_screens import RandomEventScreen
                self.gui_manager.set_screen(RandomEventScreen(self, event, cash_effect))
            else:
                # Fallback to console version for text-based gameplay
                self.clear_screen()
                print("\n" + "!" * 60)
                print(f"LIFE EVENT: {event['name']}")
                print(event["description"])

                if cash_effect > 0:
                    print(f"You received ${cash_effect}!")
                    self.player.cash += cash_effect
                else:
                    print(f"This costs you ${abs(cash_effect)}.")

                    # Handle payment
                    if self.player.cash >= abs(cash_effect):
                        self.player.cash -= abs(cash_effect)
                        print("You paid in cash.")
                    elif self.player.bank_account and self.player.bank_account.balance >= abs(cash_effect):
                        self.player.bank_account.withdraw(abs(cash_effect))
                        print("You paid using your bank account.")
                    elif self.player.credit_card and (self.player.credit_card.balance + abs(cash_effect)) <= self.player.credit_card.limit:
                        self.player.credit_card.charge(abs(cash_effect))
                        print("You paid using your credit card.")
                    else:
                        print("You couldn't afford this expense! Your credit score has been affected.")
                        self.player.credit_score -= 15

                print("!" * 60)
                input("\nPress Enter to continue...")

    def check_life_stage_events(self):
        """Check for and trigger life stage events based on player age."""
        # High school graduation
        if self.player.age == 18 and self.player.education == "High School":
            self.high_school_graduation_event()

        # College graduation (if went to college)
        if self.player.age == 22 and self.player.education == "College (In Progress)":
            self.college_graduation_event()

        # First full-time job opportunity
        if self.player.age == 22 and not self.player.job and self.player.education != "College (In Progress)":
            self.job_opportunity_event()

        # Car purchase opportunity
        if self.player.age == 20 and not any(a.asset_type == "Car" for a in self.player.assets):
            self.car_purchase_opportunity()

        # House purchase opportunity
        if self.player.age == 30 and not any(a.asset_type == "House" for a in self.player.assets) and self.player.job:
            self.house_purchase_opportunity()

        # Family planning opportunity
        if self.player.age >= 28 and not self.player.family and self.player.job:
            if random.random() < 0.1:  # 10% chance each year after 28
                self.family_planning_opportunity()

    def high_school_graduation_event(self):
        """Handle the high school graduation event."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("LIFE EVENT: HIGH SCHOOL GRADUATION")
        print("=" * 60)
        print("\nCongratulations! You've graduated from high school.")
        print("It's time to make some important decisions about your future.")

        choices = ["Go to college (costs $20,000/year for 4 years)",
                  "Go to trade school (costs $10,000 for 2 years)",
                  "Start working full-time"]

        choice = self.get_choice("What would you like to do?", choices)

        if choice == choices[0]:  # College
            print("\nYou've decided to go to college. This is a significant investment")
            print("in your future that could lead to higher-paying jobs.")

            # Check if player can afford college
            annual_cost = 20000
            if self.player.cash >= annual_cost:
                print(f"\nYou pay the first year's tuition of ${annual_cost} in cash.")
                self.player.cash -= annual_cost
            elif self.player.bank_account and self.player.bank_account.balance >= annual_cost:
                print(f"\nYou pay the first year's tuition of ${annual_cost} from your bank account.")
                self.player.bank_account.withdraw(annual_cost)
            else:
                # Need a student loan
                print("\nYou don't have enough money to pay for college upfront.")
                print("You'll need to take out student loans.")

                loan_amount = 80000  # 4 years of college
                loan = Loan("Student", loan_amount, 0.05, 20)  # 5% interest, 20-year term
                self.player.loans.append(loan)

                print(f"\nYou've taken out a student loan for ${loan_amount}.")
                print(f"Your monthly payment will be ${loan.monthly_payment:.2f} for 20 years.")

            self.player.education = "College (In Progress)"
            print("\nYou're now a college student! Your education will take 4 years.")

        elif choice == choices[1]:  # Trade school
            print("\nYou've decided to go to trade school. This is a practical choice")
            print("that will give you specific skills for certain careers.")

            # Check if player can afford trade school
            cost = 10000
            if self.player.cash >= cost:
                print(f"\nYou pay the trade school tuition of ${cost} in cash.")
                self.player.cash -= cost
            elif self.player.bank_account and self.player.bank_account.balance >= cost:
                print(f"\nYou pay the trade school tuition of ${cost} from your bank account.")
                self.player.bank_account.withdraw(cost)
            else:
                # Need a student loan
                print("\nYou don't have enough money to pay for trade school upfront.")
                print("You'll need to take out a student loan.")

                loan = Loan("Student", cost, 0.05, 10)  # 5% interest, 10-year term
                self.player.loans.append(loan)

                print(f"\nYou've taken out a student loan for ${cost}.")
                print(f"Your monthly payment will be ${loan.monthly_payment:.2f} for 10 years.")

            self.player.education = "Trade School"
            print("\nYou're now a trade school student! Your education will take 2 years.")

        else:  # Start working
            print("\nYou've decided to start working full-time without further education.")
            print("You'll start with entry-level positions, but can work your way up.")

            self.player.education = "High School Graduate"
            self.job_opportunity_event()

        input("\nPress Enter to continue...")

    def college_graduation_event(self):
        """Handle the college graduation event."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("LIFE EVENT: COLLEGE GRADUATION")
        print("=" * 60)
        print("\nCongratulations! You've graduated from college with a bachelor's degree.")
        print("Your education will open up better job opportunities.")

        self.player.education = "College Graduate"
        self.player.credit_score += 20  # Education boosts credit score

        print("\nYour credit score has increased due to your educational achievement.")
        print(f"Your credit score is now {self.player.credit_score}.")

        # Offer job opportunities
        print("\nWith your new degree, you have access to better job opportunities.")
        self.job_opportunity_event()

        input("\nPress Enter to continue...")

    def job_opportunity_event(self):
        """Handle job opportunities."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("LIFE EVENT: JOB OPPORTUNITY")
        print("=" * 60)

        # Generate job options based on education
        job_options = []

        if self.player.education == "High School Graduate":
            job_options = [
                {"title": "Retail Associate", "salary": 25000},
                {"title": "Food Service Worker", "salary": 22000},
                {"title": "Warehouse Worker", "salary": 28000},
            ]
        elif self.player.education == "Trade School":
            job_options = [
                {"title": "Electrician Apprentice", "salary": 35000},
                {"title": "Plumber Assistant", "salary": 32000},
                {"title": "HVAC Technician", "salary": 38000},
            ]
        elif self.player.education == "College Graduate":
            job_options = [
                {"title": "Entry-Level Accountant", "salary": 50000},
                {"title": "Marketing Coordinator", "salary": 45000},
                {"title": "Software Developer", "salary": 65000},
            ]

        # Display job options
        print("\nThe following job opportunities are available to you:")
        for i, job in enumerate(job_options):
            print(f"{i+1}. {job['title']} - ${job['salary']}/year")

        # Get player choice
        choice = 0
        while choice < 1 or choice > len(job_options):
            try:
                choice = int(input(f"\nWhich job would you like to take? (1-{len(job_options)}): "))
            except ValueError:
                print("Please enter a valid number.")

        # Apply job
        selected_job = job_options[choice-1]
        self.player.job = selected_job["title"]
        self.player.salary = selected_job["salary"]

        print(f"\nCongratulations! You are now a {self.player.job} earning ${self.player.salary}/year.")
        print(f"Your monthly income is ${self.player.salary/12:.2f}.")

        input("\nPress Enter to continue...")

    def car_purchase_opportunity(self):
        """Handle car purchase opportunity."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("LIFE EVENT: CAR PURCHASE OPPORTUNITY")
        print("=" * 60)
        print("\nYou're now at an age where having your own car could be beneficial.")
        print("Would you like to look at some car options?")

        choice = self.get_choice("Do you want to buy a car?", ["Yes", "No"])

        if choice == "Yes":
            # Car options
            car_options = [
                {"name": "Used Economy Car", "value": 5000},
                {"name": "New Economy Car", "value": 18000},
                {"name": "Used Luxury Car", "value": 15000},
                {"name": "New Luxury Car", "value": 35000},
            ]

            print("\nHere are your car options:")
            for i, car in enumerate(car_options):
                print(f"{i+1}. {car['name']} - ${car['value']}")

            # Get player choice
            car_choice = 0
            while car_choice < 1 or car_choice > len(car_options):
                try:
                    car_choice = int(input(f"\nWhich car would you like to buy? (1-{len(car_options)}): "))
                except ValueError:
                    print("Please enter a valid number.")

            selected_car = car_options[car_choice-1]

            # Payment options
            print(f"\nYou've selected the {selected_car['name']} for ${selected_car['value']}.")
            print("How would you like to pay?")

            payment_options = ["Cash"]
            if self.player.bank_account and self.player.bank_account.balance >= selected_car['value']:
                payment_options.append("Bank Account")
            payment_options.append("Auto Loan")

            payment_choice = self.get_choice("Select payment method:", payment_options)

            if payment_choice == "Cash" and self.player.cash >= selected_car['value']:
                self.player.cash -= selected_car['value']
                print(f"\nYou paid ${selected_car['value']} in cash for your new car.")
            elif payment_choice == "Bank Account":
                self.player.bank_account.withdraw(selected_car['value'])
                print(f"\nYou paid ${selected_car['value']} from your bank account for your new car.")
            else:  # Auto Loan
                # Determine loan terms based on credit score
                if self.player.credit_score >= 700:
                    interest_rate = 0.03  # 3%
                elif self.player.credit_score >= 650:
                    interest_rate = 0.05  # 5%
                else:
                    interest_rate = 0.08  # 8%

                loan = Loan("Auto", selected_car['value'], interest_rate, 5)  # 5-year auto loan
                self.player.loans.append(loan)

                print(f"\nYou've taken out an auto loan for ${selected_car['value']}.")
                print(f"Your interest rate is {interest_rate*100:.1f}% based on your credit score of {self.player.credit_score}.")
                print(f"Your monthly payment will be ${loan.monthly_payment:.2f} for 5 years.")

            # Add car to assets
            self.player.assets.append(Asset("Car", selected_car['name'], selected_car['value']))
            print(f"\nCongratulations on your new {selected_car['name']}!")

        else:
            print("\nYou've decided not to buy a car at this time.")

        input("\nPress Enter to continue...")

    def house_purchase_opportunity(self):
        """Handle house purchase opportunity."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("LIFE EVENT: HOUSE PURCHASE OPPORTUNITY")
        print("=" * 60)
        print("\nYou're now at a stage in life where buying a house could be a good investment.")
        print("Would you like to look at some housing options?")

        choice = self.get_choice("Do you want to buy a house?", ["Yes", "No"])

        if choice == "Yes":
            # House options
            house_options = [
                {"name": "Small Starter Home", "value": 150000},
                {"name": "Mid-size Family Home", "value": 250000},
                {"name": "Large Luxury Home", "value": 500000},
                {"name": "Urban Condo", "value": 200000},
            ]

            print("\nHere are your housing options:")
            for i, house in enumerate(house_options):
                print(f"{i+1}. {house['name']} - ${house['value']}")

            # Get player choice
            house_choice = 0
            while house_choice < 1 or house_choice > len(house_options):
                try:
                    house_choice = int(input(f"\nWhich house would you like to buy? (1-{len(house_options)}): "))
                except ValueError:
                    print("Please enter a valid number.")

            selected_house = house_options[house_choice-1]

            # Calculate down payment (20% is standard)
            down_payment = selected_house['value'] * 0.2
            loan_amount = selected_house['value'] - down_payment

            print(f"\nYou've selected the {selected_house['name']} for ${selected_house['value']}.")
            print(f"A standard mortgage requires a 20% down payment of ${down_payment}.")

            # Check if player can afford down payment
            if self.player.cash < down_payment and (not self.player.bank_account or self.player.bank_account.balance < down_payment):
                print("\nYou don't have enough money for the down payment.")
                print("You'll need to save up more money before buying a house.")
                input("\nPress Enter to continue...")
                return

            # Down payment options
            payment_options = []
            if self.player.cash >= down_payment:
                payment_options.append("Cash")
            if self.player.bank_account and self.player.bank_account.balance >= down_payment:
                payment_options.append("Bank Account")

            payment_choice = self.get_choice("How would you like to pay the down payment?", payment_options)

            if payment_choice == "Cash":
                self.player.cash -= down_payment
                print(f"\nYou paid ${down_payment} in cash for your down payment.")
            else:  # Bank Account
                self.player.bank_account.withdraw(down_payment)
                print(f"\nYou paid ${down_payment} from your bank account for your down payment.")

            # Determine mortgage terms based on credit score
            if self.player.credit_score >= 750:
                interest_rate = 0.035  # 3.5%
            elif self.player.credit_score >= 700:
                interest_rate = 0.04   # 4.0%
            elif self.player.credit_score >= 650:
                interest_rate = 0.045  # 4.5%
            else:
                interest_rate = 0.055  # 5.5%

            loan = Loan("Mortgage", loan_amount, interest_rate, 30)  # 30-year mortgage
            self.player.loans.append(loan)

            print(f"\nYou've taken out a mortgage for ${loan_amount}.")
            print(f"Your interest rate is {interest_rate*100:.1f}% based on your credit score of {self.player.credit_score}.")
            print(f"Your monthly payment will be ${loan.monthly_payment:.2f} for 30 years.")

            # Add house to assets
            self.player.assets.append(Asset("House", selected_house['name'], selected_house['value']))
            print(f"\nCongratulations on your new {selected_house['name']}!")

        else:
            print("\nYou've decided not to buy a house at this time.")

        input("\nPress Enter to continue...")

    def family_planning_opportunity(self):
        """Handle family planning opportunity."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("LIFE EVENT: FAMILY PLANNING")
        print("=" * 60)
        print("\nYou've reached a stage in life where starting a family might be a consideration.")
        print("Starting a family will increase your monthly expenses but can bring joy to your life.")

        choice = self.get_choice("Would you like to start a family?", ["Yes", "No"])

        if choice == "Yes":
            # Add a spouse
            spouse_age = self.player.age - random.randint(-3, 3)  # Spouse age is close to player age
            self.player.family.append({"relation": "Spouse", "age": spouse_age})

            print("\nCongratulations! You've gotten married.")
            print(f"Your spouse is {spouse_age} years old.")

            # Chance for dual income
            if random.random() < 0.7:  # 70% chance of spouse having a job
                spouse_income = int(self.player.salary * random.uniform(0.5, 1.5))  # Spouse income relative to player
                self.player.salary += spouse_income  # Add spouse income to family income
                print(f"Your spouse has a job that adds ${spouse_income}/year to your family income.")
                print(f"Your combined family income is now ${self.player.salary}/year.")
            else:
                print("Your spouse doesn't currently have a job.")

            # Ask about children
            child_choice = self.get_choice("Would you like to have children?", ["Yes", "No"])

            if child_choice == "Yes":
                num_children = random.randint(1, 3)  # Random number of children

                for i in range(num_children):
                    child_name = f"Child {i+1}"  # Placeholder name
                    child_age = 0  # Newborn
                    self.player.family.append({"relation": "Child", "name": child_name, "age": child_age})

                print(f"\nCongratulations! You now have {num_children} {'child' if num_children == 1 else 'children'}.")
                print("Having children will increase your monthly expenses.")

                # Adjust expenses for children
                print("\nYour monthly expenses have increased to account for your growing family.")

        else:
            print("\nYou've decided not to start a family at this time.")

        input("\nPress Enter to continue...")

    def display_status(self):
        """Display the player's current status (text mode)."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print(f"MONTH: {self.current_month}/YEAR: {self.current_year + 2023}")
        print(f"AGE: {self.player.age}")
        print("=" * 60)

        print(f"\nName: {self.player.name}")
        print(f"Education: {self.player.education}")
        print(f"Job: {self.player.job if self.player.job else 'Unemployed'}")
        if self.player.job:
            print(f"Salary: ${self.player.salary}/year (${self.player.salary/12:.2f}/month)")

        print(f"\nCash: ${self.player.cash:.2f}")

        if self.player.bank_account:
            print(f"Bank Account ({self.player.bank_account.account_type}): ${self.player.bank_account.balance:.2f}")

        if self.player.credit_card:
            print(f"Credit Card: ${self.player.credit_card.balance:.2f}/{self.player.credit_card.limit:.2f}")

        print(f"Credit Score: {self.player.credit_score}")

        if self.player.loans:
            print("\n--- LOANS ---")
            for loan in self.player.loans:
                print(f"{loan.loan_type}: ${loan.current_balance:.2f} remaining (${loan.monthly_payment:.2f}/month)")

        if self.player.assets:
            print("\n--- ASSETS ---")
            for asset in self.player.assets:
                print(f"{asset.name}: ${asset.current_value:.2f} ({asset.condition} condition)")

        if self.player.family:
            print("\n--- FAMILY ---")
            for member in self.player.family:
                if member["relation"] == "Spouse":
                    print(f"Spouse: Age {member['age'] + self.current_year}")
                else:
                    print(f"{member['relation']}: {member['name']}, Age {member['age'] + self.current_year}")

        # Calculate and display net worth
        cash = self.player.cash
        bank_balance = self.player.bank_account.balance if self.player.bank_account else 0
        credit_card_debt = self.player.credit_card.balance if self.player.credit_card else 0

        loan_debt = 0
        for loan in self.player.loans:
            loan_debt += loan.current_balance

        asset_value = 0
        for asset in self.player.assets:
            asset_value += asset.current_value

        net_worth = cash + bank_balance - credit_card_debt - loan_debt + asset_value

        print(f"\nNET WORTH: ${net_worth:.2f}")

        print("\n" + "=" * 60)

    def get_player_action(self):
        """Get the player's next action (text mode)."""
        actions = ["Continue to next month"]

        # Banking actions
        if not self.player.bank_account:
            actions.append("Open a bank account")
        else:
            actions.append("View bank account")
            actions.append("Deposit to bank")
            actions.append("Withdraw from bank")

            if not self.player.debit_card:
                actions.append("Get a debit card")

        # Credit actions
        if not self.player.credit_card and self.player.age >= 18:
            actions.append("Apply for a credit card")
        elif self.player.credit_card:
            actions.append("View credit card")
            if self.player.credit_card.balance > 0:
                actions.append("Pay credit card")

        # Loan actions
        if self.player.loans:
            actions.append("View loans")
            actions.append("Make extra loan payment")

        # Asset actions
        if self.player.assets:
            actions.append("View assets")

        # Job actions
        if not self.player.job and self.player.age >= 16:
            actions.append("Look for a job")
        elif self.player.job and random.random() < 0.1:  # 10% chance of job opportunity each month
            actions.append("Look for a better job")

        # Display actions
        print("\nWhat would you like to do?")
        for i, action in enumerate(actions):
            print(f"{i+1}. {action}")

        # Get player choice
        choice = 0
        while choice < 1 or choice > len(actions):
            try:
                choice = int(input(f"\nEnter your choice (1-{len(actions)}): "))
            except ValueError:
                print("Please enter a valid number.")

        action = actions[choice-1]

        # Process action
        if action == "Continue to next month":
            return
        elif action == "Open a bank account":
            self.open_bank_account()
        elif action == "View bank account":
            self.view_bank_account()
        elif action == "Deposit to bank":
            self.deposit_to_bank()
        elif action == "Withdraw from bank":
            self.withdraw_from_bank()
        elif action == "Get a debit card":
            self.get_debit_card()
        elif action == "Apply for a credit card":
            self.apply_for_credit_card()
        elif action == "View credit card":
            self.view_credit_card()
        elif action == "Pay credit card":
            self.pay_credit_card()
        elif action == "View loans":
            self.view_loans()
        elif action == "Make extra loan payment":
            self.make_extra_loan_payment()
        elif action == "View assets":
            self.view_assets()
        elif action == "Look for a job" or action == "Look for a better job":
            self.look_for_job()

        # After action, show status again and get another action
        self.display_status()
        self.get_player_action()

    def open_bank_account(self):
        """Open a bank account."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("OPEN A BANK ACCOUNT")
        print("=" * 60)

        print("\nYou can open a checking account for everyday transactions")
        print("or a savings account that earns interest.")

        account_type = self.get_choice("What type of account would you like to open?", ["Checking", "Savings"])

        self.player.bank_account = BankAccount(account_type)

        print(f"\nCongratulations! You've opened a {account_type} account.")

        if account_type == "Savings":
            print(f"Your account will earn {self.player.bank_account.interest_rate*100:.1f}% interest annually.")

        # Initial deposit
        deposit = 0
        while deposit <= 0:
            try:
                deposit = float(input("\nHow much would you like to deposit initially? $"))
                if deposit <= 0:
                    print("Please enter a positive amount.")
                elif deposit > self.player.cash:
                    print("You don't have that much cash.")
                    deposit = 0
            except ValueError:
                print("Please enter a valid number.")

        self.player.cash -= deposit
        self.player.bank_account.deposit(deposit)

        print(f"\nYou've deposited ${deposit:.2f} into your new account.")
        print(f"Your account balance is ${self.player.bank_account.balance:.2f}.")

        # Offer debit card
        if account_type == "Checking":
            choice = self.get_choice("Would you like a debit card with your account?", ["Yes", "No"])
            if choice == "Yes":
                self.player.debit_card = Card("Debit")
                print("\nYou now have a debit card linked to your checking account.")

        input("\nPress Enter to continue...")

    def view_bank_account(self):
        """View bank account details."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("BANK ACCOUNT DETAILS")
        print("=" * 60)

        print(f"\nAccount Type: {self.player.bank_account.account_type}")
        print(f"Current Balance: ${self.player.bank_account.balance:.2f}")

        if self.player.bank_account.account_type == "Savings":
            print(f"Interest Rate: {self.player.bank_account.interest_rate*100:.1f}% annually")
            annual_interest = self.player.bank_account.balance * self.player.bank_account.interest_rate
            print(f"Projected Annual Interest: ${annual_interest:.2f}")

        if self.player.debit_card:
            print("\nYou have a debit card linked to this account.")

        # Show recent transactions
        if self.player.bank_account.transaction_history:
            print("\nRecent Transactions:")
            for i, transaction in enumerate(reversed(self.player.bank_account.transaction_history[-5:])):
                if transaction["type"] == "deposit":
                    print(f"  Deposit: +${transaction['amount']:.2f}")
                elif transaction["type"] == "withdrawal":
                    print(f"  Withdrawal: -${transaction['amount']:.2f}")
                elif transaction["type"] == "interest":
                    print(f"  Interest: +${transaction['amount']:.2f}")

        input("\nPress Enter to continue...")

    def deposit_to_bank(self):
        """Deposit money to bank account."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("DEPOSIT TO BANK")
        print("=" * 60)

        print(f"\nYour current cash: ${self.player.cash:.2f}")
        print(f"Your current bank balance: ${self.player.bank_account.balance:.2f}")

        deposit = 0
        while deposit <= 0:
            try:
                deposit = float(input("\nHow much would you like to deposit? $"))
                if deposit <= 0:
                    print("Please enter a positive amount.")
                elif deposit > self.player.cash:
                    print("You don't have that much cash.")
                    deposit = 0
            except ValueError:
                print("Please enter a valid number.")

        self.player.cash -= deposit
        self.player.bank_account.deposit(deposit)

        print(f"\nYou've deposited ${deposit:.2f} into your account.")
        print(f"Your new account balance is ${self.player.bank_account.balance:.2f}.")
        print(f"Your remaining cash is ${self.player.cash:.2f}.")

        input("\nPress Enter to continue...")

    def withdraw_from_bank(self):
        """Withdraw money from bank account."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("WITHDRAW FROM BANK")
        print("=" * 60)

        print(f"\nYour current cash: ${self.player.cash:.2f}")
        print(f"Your current bank balance: ${self.player.bank_account.balance:.2f}")

        withdrawal = 0
        while withdrawal <= 0:
            try:
                withdrawal = float(input("\nHow much would you like to withdraw? $"))
                if withdrawal <= 0:
                    print("Please enter a positive amount.")
                elif withdrawal > self.player.bank_account.balance:
                    print("You don't have that much in your account.")
                    withdrawal = 0
            except ValueError:
                print("Please enter a valid number.")

        self.player.bank_account.withdraw(withdrawal)
        self.player.cash += withdrawal

        print(f"\nYou've withdrawn ${withdrawal:.2f} from your account.")
        print(f"Your new account balance is ${self.player.bank_account.balance:.2f}.")
        print(f"Your cash is now ${self.player.cash:.2f}.")

        input("\nPress Enter to continue...")

    def get_debit_card(self):
        """Get a debit card for the bank account."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("GET A DEBIT CARD")
        print("=" * 60)

        print("\nA debit card allows you to make purchases directly from your checking account.")
        print("There is no fee for this card.")

        self.player.debit_card = Card("Debit")

        print("\nYou now have a debit card linked to your checking account.")

        input("\nPress Enter to continue...")

    def apply_for_credit_card(self):
        """Apply for a credit card."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("APPLY FOR A CREDIT CARD")
        print("=" * 60)

        print("\nA credit card allows you to make purchases on credit.")
        print("You'll need to make monthly payments, and interest will be charged on unpaid balances.")
        print("Your credit limit will be based on your credit score and income.")

        # Check eligibility
        if self.player.age < 18:
            print("\nSorry, you must be at least 18 years old to apply for a credit card.")
            input("\nPress Enter to continue...")
            return

        if not self.player.job:
            print("\nSorry, you need to have a job to apply for a credit card.")
            input("\nPress Enter to continue...")
            return

        # Determine credit limit based on credit score and income
        base_limit = self.player.salary * 0.2  # 20% of annual income

        if self.player.credit_score >= 750:
            limit_multiplier = 1.5  # Excellent credit
        elif self.player.credit_score >= 700:
            limit_multiplier = 1.2  # Good credit
        elif self.player.credit_score >= 650:
            limit_multiplier = 1.0  # Fair credit
        elif self.player.credit_score >= 600:
            limit_multiplier = 0.8  # Poor credit
        else:
            limit_multiplier = 0.5  # Bad credit

        credit_limit = base_limit * limit_multiplier

        # Round to nearest $100
        credit_limit = round(credit_limit / 100) * 100

        # Minimum $500, maximum $50,000
        credit_limit = max(500, min(50000, credit_limit))

        print(f"\nBased on your credit score of {self.player.credit_score} and income of ${self.player.salary}/year,")
        print(f"you qualify for a credit card with a limit of ${credit_limit:.2f}.")

        choice = self.get_choice("Would you like to accept this credit card offer?", ["Yes", "No"])

        if choice == "Yes":
            self.player.credit_card = Card("Credit", credit_limit)
            print("\nCongratulations! You now have a credit card.")
            print(f"Your credit limit is ${self.player.credit_card.limit:.2f}.")
            print("Remember to make your payments on time to maintain a good credit score.")
        else:
            print("\nYou've declined the credit card offer.")

        input("\nPress Enter to continue...")

    def view_credit_card(self):
        """View credit card details."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("CREDIT CARD DETAILS")
        print("=" * 60)

        print(f"\nCredit Limit: ${self.player.credit_card.limit:.2f}")
        print(f"Current Balance: ${self.player.credit_card.balance:.2f}")
        print(f"Available Credit: ${self.player.credit_card.limit - self.player.credit_card.balance:.2f}")

        # Calculate minimum payment
        min_payment = max(25, self.player.credit_card.balance * 0.05)  # Minimum $25 or 5% of balance

        if self.player.credit_card.balance > 0:
            print(f"\nMinimum Payment Due: ${min_payment:.2f}")
            print("Interest Rate: 18% APR on unpaid balances")

            # Show interest that would be charged
            monthly_interest = self.player.credit_card.balance * 0.18 / 12
            print(f"Interest This Month (if unpaid): ${monthly_interest:.2f}")

        # Show recent transactions
        if self.player.credit_card.transaction_history:
            print("\nRecent Transactions:")
            for i, transaction in enumerate(reversed(self.player.credit_card.transaction_history[-5:])):
                if transaction["type"] == "charge":
                    print(f"  Charge: +${transaction['amount']:.2f}")
                elif transaction["type"] == "payment":
                    print(f"  Payment: -${transaction['amount']:.2f}")

        input("\nPress Enter to continue...")

    def pay_credit_card(self):
        """Make a payment on the credit card."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("PAY CREDIT CARD")
        print("=" * 60)

        print(f"\nCurrent Credit Card Balance: ${self.player.credit_card.balance:.2f}")

        # Calculate minimum payment
        min_payment = max(25, self.player.credit_card.balance * 0.05)  # Minimum $25 or 5% of balance

        print(f"Minimum Payment Due: ${min_payment:.2f}")
        print(f"Your Cash: ${self.player.cash:.2f}")

        if self.player.bank_account:
            print(f"Your Bank Balance: ${self.player.bank_account.balance:.2f}")

        # Payment options
        payment_options = ["Minimum Payment", "Full Balance"]
        if min_payment < self.player.credit_card.balance:
            payment_options.insert(1, "Custom Amount")

        payment_choice = self.get_choice("How much would you like to pay?", payment_options)

        if payment_choice == "Minimum Payment":
            payment_amount = min_payment
        elif payment_choice == "Full Balance":
            payment_amount = self.player.credit_card.balance
        else:  # Custom Amount
            payment_amount = 0
            while payment_amount < min_payment or payment_amount > self.player.credit_card.balance:
                try:
                    payment_amount = float(input(f"\nEnter payment amount (minimum ${min_payment:.2f}): $"))
                    if payment_amount < min_payment:
                        print(f"Payment must be at least the minimum payment of ${min_payment:.2f}.")
                    elif payment_amount > self.player.credit_card.balance:
                        print(f"Payment cannot exceed your balance of ${self.player.credit_card.balance:.2f}.")
                except ValueError:
                    print("Please enter a valid number.")

        # Payment method
        payment_methods = []
        if self.player.cash >= payment_amount:
            payment_methods.append("Cash")
        if self.player.bank_account and self.player.bank_account.balance >= payment_amount:
            payment_methods.append("Bank Account")

        if not payment_methods:
            print("\nYou don't have enough money to make this payment.")
            input("\nPress Enter to continue...")
            return

        payment_method = self.get_choice("How would you like to pay?", payment_methods)

        # Process payment
        if payment_method == "Cash":
            self.player.cash -= payment_amount
            self.player.credit_card.pay(payment_amount)
            print(f"\nYou paid ${payment_amount:.2f} from your cash.")
        else:  # Bank Account
            self.player.bank_account.withdraw(payment_amount)
            self.player.credit_card.pay(payment_amount)
            print(f"\nYou paid ${payment_amount:.2f} from your bank account.")

        print(f"Your new credit card balance is ${self.player.credit_card.balance:.2f}.")

        # Credit score improvement for on-time payments
        if payment_amount >= min_payment:
            score_increase = min(5, 850 - self.player.credit_score)  # Cap at 850
            if score_increase > 0:
                self.player.credit_score += score_increase
                print(f"\nYour on-time payment has improved your credit score by {score_increase} points.")
                print(f"Your credit score is now {self.player.credit_score}.")

        input("\nPress Enter to continue...")

    def view_loans(self):
        """View loan details."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("LOAN DETAILS")
        print("=" * 60)

        for i, loan in enumerate(self.player.loans):
            print(f"\nLoan {i+1}: {loan.loan_type}")
            print(f"Original Amount: ${loan.original_amount:.2f}")
            print(f"Current Balance: ${loan.current_balance:.2f}")
            print(f"Interest Rate: {loan.interest_rate*100:.2f}%")
            print(f"Term: {loan.term_years} years")
            print(f"Monthly Payment: ${loan.monthly_payment:.2f}")

            # Calculate payoff date
            remaining_payments = loan.current_balance / loan.monthly_payment
            remaining_months = int(remaining_payments)
            remaining_years = remaining_months // 12
            remaining_months %= 12

            print(f"Estimated Payoff: {remaining_years} years and {remaining_months} months")

            # Calculate total interest to be paid
            total_payments = loan.monthly_payment * remaining_payments
            total_interest = total_payments - loan.current_balance

            print(f"Remaining Interest to be Paid: ${total_interest:.2f}")

            if i < len(self.player.loans) - 1:
                print("\n" + "-" * 40)

        input("\nPress Enter to continue...")

    def make_extra_loan_payment(self):
        """Make an extra payment on a loan."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("MAKE EXTRA LOAN PAYMENT")
        print("=" * 60)

        print("\nMaking extra payments on your loans can help you pay them off faster")
        print("and save money on interest.")

        # Select loan
        if len(self.player.loans) > 1:
            print("\nWhich loan would you like to make an extra payment on?")
            for i, loan in enumerate(self.player.loans):
                print(f"{i+1}. {loan.loan_type} - ${loan.current_balance:.2f} remaining")

            loan_choice = 0
            while loan_choice < 1 or loan_choice > len(self.player.loans):
                try:
                    loan_choice = int(input(f"\nEnter your choice (1-{len(self.player.loans)}): "))
                except ValueError:
                    print("Please enter a valid number.")

            selected_loan = self.player.loans[loan_choice-1]
        else:
            selected_loan = self.player.loans[0]

        print(f"\nSelected Loan: {selected_loan.loan_type}")
        print(f"Current Balance: ${selected_loan.current_balance:.2f}")
        print(f"Interest Rate: {selected_loan.interest_rate*100:.2f}%")
        print(f"Regular Monthly Payment: ${selected_loan.monthly_payment:.2f}")

        print(f"\nYour Cash: ${self.player.cash:.2f}")
        if self.player.bank_account:
            print(f"Your Bank Balance: ${self.player.bank_account.balance:.2f}")

        # Enter payment amount
        payment_amount = 0
        while payment_amount <= 0:
            try:
                payment_amount = float(input("\nHow much extra would you like to pay? $"))
                if payment_amount <= 0:
                    print("Please enter a positive amount.")
                elif payment_amount > selected_loan.current_balance:
                    print(f"Payment cannot exceed your loan balance of ${selected_loan.current_balance:.2f}.")
                    payment_amount = 0
            except ValueError:
                print("Please enter a valid number.")

        # Payment method
        payment_methods = []
        if self.player.cash >= payment_amount:
            payment_methods.append("Cash")
        if self.player.bank_account and self.player.bank_account.balance >= payment_amount:
            payment_methods.append("Bank Account")

        if not payment_methods:
            print("\nYou don't have enough money to make this payment.")
            input("\nPress Enter to continue...")
            return

        payment_method = self.get_choice("How would you like to pay?", payment_methods)

        # Process payment
        if payment_method == "Cash":
            self.player.cash -= payment_amount
            selected_loan.make_payment(payment_amount)
            print(f"\nYou paid ${payment_amount:.2f} from your cash.")
        else:  # Bank Account
            self.player.bank_account.withdraw(payment_amount)
            selected_loan.make_payment(payment_amount)
            print(f"\nYou paid ${payment_amount:.2f} from your bank account.")

        print(f"Your new loan balance is ${selected_loan.current_balance:.2f}.")

        # Recalculate payoff date
        if selected_loan.current_balance > 0:
            remaining_payments = selected_loan.current_balance / selected_loan.monthly_payment
            remaining_months = int(remaining_payments)
            remaining_years = remaining_months // 12
            remaining_months %= 12

            print(f"\nYour extra payment has shortened your loan term!")
            print(f"New Estimated Payoff: {remaining_years} years and {remaining_months} months")

            # Calculate interest savings
            original_total = selected_loan.monthly_payment * (selected_loan.term_years * 12)
            new_total = selected_loan.monthly_payment * remaining_payments + payment_amount
            savings = original_total - new_total

            print(f"You'll save approximately ${savings:.2f} in interest over the life of the loan.")
        else:
            print("\nCongratulations! You've paid off this loan completely!")

            # Remove the loan from the player's loans
            self.player.loans.remove(selected_loan)

            # Credit score improvement for paying off a loan
            score_increase = min(20, 850 - self.player.credit_score)  # Cap at 850
            if score_increase > 0:
                self.player.credit_score += score_increase
                print(f"\nPaying off your loan has improved your credit score by {score_increase} points.")
                print(f"Your credit score is now {self.player.credit_score}.")

        input("\nPress Enter to continue...")

    def view_assets(self):
        """View asset details."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("ASSET DETAILS")
        print("=" * 60)

        for i, asset in enumerate(self.player.assets):
            print(f"\nAsset {i+1}: {asset.name}")
            print(f"Type: {asset.asset_type}")
            print(f"Purchase Value: ${asset.purchase_value:.2f}")
            print(f"Current Value: ${asset.current_value:.2f}")
            print(f"Condition: {asset.condition}")
            print(f"Age: {asset.age} years")

            # Value change
            value_change = asset.current_value - asset.purchase_value
            value_change_percent = (value_change / asset.purchase_value) * 100

            if value_change >= 0:
                print(f"Appreciation: ${value_change:.2f} ({value_change_percent:.1f}%)")
            else:
                print(f"Depreciation: ${abs(value_change):.2f} ({abs(value_change_percent):.1f}%)")

            if i < len(self.player.assets) - 1:
                print("\n" + "-" * 40)

        input("\nPress Enter to continue...")

    def look_for_job(self):
        """Look for a job or a better job."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("JOB SEARCH")
        print("=" * 60)

        current_salary = self.player.salary if self.player.job else 0

        print(f"\nCurrent Job: {self.player.job if self.player.job else 'Unemployed'}")
        if self.player.job:
            print(f"Current Salary: ${current_salary}/year")

        # Generate job options based on education and experience
        job_options = []

        # Base salary multiplier based on years of experience
        experience_years = max(0, self.player.age - 18)  # Assume working age starts at 18
        experience_multiplier = 1.0 + (experience_years * 0.03)  # 3% increase per year of experience

        if self.player.education == "High School" or self.player.education == "High School Graduate":
            job_options = [
                {"title": "Retail Associate", "salary": int(25000 * experience_multiplier)},
                {"title": "Food Service Worker", "salary": int(22000 * experience_multiplier)},
                {"title": "Warehouse Worker", "salary": int(28000 * experience_multiplier)},
                {"title": "Office Clerk", "salary": int(30000 * experience_multiplier)},
            ]
        elif self.player.education == "Trade School":
            job_options = [
                {"title": "Electrician", "salary": int(45000 * experience_multiplier)},
                {"title": "Plumber", "salary": int(48000 * experience_multiplier)},
                {"title": "HVAC Technician", "salary": int(50000 * experience_multiplier)},
                {"title": "Automotive Mechanic", "salary": int(42000 * experience_multiplier)},
            ]
        elif self.player.education == "College Graduate":
            job_options = [
                {"title": "Accountant", "salary": int(60000 * experience_multiplier)},
                {"title": "Marketing Manager", "salary": int(65000 * experience_multiplier)},
                {"title": "Software Developer", "salary": int(75000 * experience_multiplier)},
                {"title": "Financial Analyst", "salary": int(70000 * experience_multiplier)},
            ]
        else:  # Default/basic jobs
            job_options = [
                {"title": "Retail Associate", "salary": int(25000 * experience_multiplier)},
                {"title": "Food Service Worker", "salary": int(22000 * experience_multiplier)},
                {"title": "Warehouse Worker", "salary": int(28000 * experience_multiplier)},
            ]

        # Add some randomness to salaries (±10%)
        for job in job_options:
            job["salary"] = int(job["salary"] * random.uniform(0.9, 1.1))

        # Filter out jobs that don't offer at least 5% more than current salary (if employed)
        if self.player.job:
            job_options = [job for job in job_options if job["salary"] >= current_salary * 1.05]

        # If no jobs available after filtering
        if not job_options:
            print("\nAfter searching, you couldn't find any jobs that would be a significant")
            print("improvement over your current position. Keep building your skills and")
            print("try again later!")
            input("\nPress Enter to continue...")
            return

        # Display job options
        print("\nThe following job opportunities are available to you:")
        for i, job in enumerate(job_options):
            print(f"{i+1}. {job['title']} - ${job['salary']}/year")

        print("\n0. Cancel job search")

        # Get player choice
        choice = -1
        while choice < 0 or choice > len(job_options):
            try:
                choice = int(input(f"\nWhich job would you like to apply for? (0-{len(job_options)}): "))
            except ValueError:
                print("Please enter a valid number.")

        if choice == 0:
            print("\nYou've decided not to change jobs at this time.")
            input("\nPress Enter to continue...")
            return

        # Apply for job
        selected_job = job_options[choice-1]

        # Job application success chance based on qualifications
        base_success_chance = 0.7  # 70% base chance

        # Adjust for education
        if self.player.education == "College Graduate":
            base_success_chance += 0.2
        elif self.player.education == "Trade School":
            base_success_chance += 0.1

        # Adjust for experience
        base_success_chance += min(0.2, experience_years * 0.01)  # Up to 20% bonus for experience

        # Cap at 95% chance
        success_chance = min(0.95, base_success_chance)

        print(f"\nYou've applied for the {selected_job['title']} position.")
        print("The hiring manager is reviewing your application...")
        time.sleep(2)  # Dramatic pause

        if random.random() < success_chance:
            print("\nCongratulations! You got the job!")

            old_job = self.player.job
            old_salary = self.player.salary

            self.player.job = selected_job["title"]
            self.player.salary = selected_job["salary"]

            print(f"\nYou are now a {self.player.job} earning ${self.player.salary}/year.")

            if old_job:
                salary_increase = self.player.salary - old_salary
                percent_increase = (salary_increase / old_salary) * 100
                print(f"That's a raise of ${salary_increase}/year ({percent_increase:.1f}%)!")

            print(f"Your monthly income is now ${self.player.salary/12:.2f}.")
        else:
            print("\nUnfortunately, the company decided to go with another candidate.")
            print("Don't be discouraged! Keep improving your skills and try again.")

        input("\nPress Enter to continue...")

    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_choice(self, prompt, choices):
        """Get a choice from the player from a list of options."""
        print(f"\n{prompt}")
        for i, choice in enumerate(choices):
            print(f"{i+1}. {choice}")

        selection = 0
        while selection < 1 or selection > len(choices):
            try:
                selection = int(input(f"\nEnter your choice (1-{len(choices)}): "))
            except ValueError:
                print("Please enter a valid number.")

        return choices[selection-1]

    def end_game(self, reason):
        """End the game and show final stats (text version)."""
        self.clear_screen()
        print("\n" + "=" * 60)

        if reason == "retirement":
            print("CONGRATULATIONS ON YOUR RETIREMENT!")
            print("=" * 60)
            print(f"\nAfter {self.current_year} years, you've reached retirement age!")
        else:
            print("GAME OVER")
            print("=" * 60)
            print(f"\nYour financial journey has ended after {self.current_year} years.")

        # Calculate net worth
        cash = self.player.cash
        bank_balance = self.player.bank_account.balance if self.player.bank_account else 0
        credit_card_debt = self.player.credit_card.balance if self.player.credit_card else 0

        loan_debt = 0
        for loan in self.player.loans:
            loan_debt += loan.current_balance

        asset_value = 0
        for asset in self.player.assets:
            asset_value += asset.current_value

        net_worth = cash + bank_balance - credit_card_debt - loan_debt + asset_value

        # Display final stats
        print("\n--- FINAL FINANCIAL SUMMARY ---")
        print(f"Cash: ${cash:.2f}")
        print(f"Bank Balance: ${bank_balance:.2f}")
        print(f"Credit Card Debt: ${credit_card_debt:.2f}")
        print(f"Loan Debt: ${loan_debt:.2f}")
        print(f"Asset Value: ${asset_value:.2f}")
        print(f"Net Worth: ${net_worth:.2f}")
        print(f"Credit Score: {self.player.credit_score}")

        # Family summary
        if self.player.family:
            print("\n--- FAMILY ---")
            for member in self.player.family:
                if member["relation"] == "Spouse":
                    print(f"Spouse: Age {member['age'] + self.current_year}")
                else:
                    print(f"{member['relation']}: {member['name']}, Age {member['age'] + self.current_year}")

        # Financial rating
        if net_worth >= 1000000:
            rating = "Financial Wizard"
        elif net_worth >= 500000:
            rating = "Financially Secure"
        elif net_worth >= 100000:
            rating = "Financially Stable"
        elif net_worth >= 0:
            rating = "Breaking Even"
        else:
            rating = "In Debt"

        print(f"\nFinancial Rating: {rating}")

        print("\nThank you for playing MONEY SMARTZ!")
        print("=" * 60)

        self.game_over = True
        input("\nPress Enter to exit...")

    def end_game_gui(self, reason):
        """End the game and show final stats (GUI version)."""
        self.game_over = True
        self.gui_manager.set_screen(EndGameScreen(self, reason))

    def check_life_stage_events_gui(self):
        """Check for life stage events and show appropriate screens (GUI version)."""
        # High school graduation
        if self.player.age == 18 and self.player.education == "High School":
            from moneySmartz.screens.life_event_screens import HighSchoolGraduationScreen
            self.gui_manager.set_screen(HighSchoolGraduationScreen(self))
            return True

        # College graduation (if went to college)
        elif self.player.age == 22 and self.player.education == "College (In Progress)":
            from moneySmartz.screens.life_event_screens import CollegeGraduationScreen
            self.gui_manager.set_screen(CollegeGraduationScreen(self))
            return True

        # First full-time job opportunity
        elif self.player.age == 22 and not self.player.job and self.player.education != "College (In Progress)":
            from moneySmartz.screens.financial_screens import JobSearchScreen
            self.gui_manager.set_screen(JobSearchScreen(self))
            return True

        # Car purchase opportunity
        elif self.player.age == 20 and not any(a.asset_type == "Car" for a in self.player.assets):
            from moneySmartz.screens.life_event_screens import CarPurchaseScreen
            self.gui_manager.set_screen(CarPurchaseScreen(self))
            return True

        # House purchase opportunity
        elif self.player.age == 30 and not any(a.asset_type == "House" for a in self.player.assets) and self.player.job:
            self.gui_manager.set_screen(HousingScreen(self))
            return True

        # Family planning opportunity
        elif self.player.age >= 28 and not self.player.family and self.player.job:
            if random.random() < 0.1:  # 10% chance each year after 28
                self.gui_manager.set_screen(FamilyPlanningScreen(self))
                return True

        return False
