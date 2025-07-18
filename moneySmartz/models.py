import random

class Player:
    """
    Represents the player character in the game.
    Tracks personal and financial information.
    """
    def __init__(self, name):
        self.name = name
        self.age = 16
        self.education = "High School"
        self.job = None
        self.salary = 0
        self.cash = 100  # Start with $100 cash
        self.bank_account = None
        self.debit_card = None
        self.credit_card = None
        self.credit_score = 650  # Average starting credit score
        self.loans = []
        self.assets = []
        self.family = []  # List of family members (spouse, children)
        self.inventory = []  # List of purchased items
        self.recurring_bills = []  # List of dicts: {name, amount, source}
        self.utility_bills = [
            {"name": "Electricity", "amount": 60},
            {"name": "Water", "amount": 30},
            {"name": "Internet", "amount": 50}
        ]

class BankAccount:
    """
    Represents a bank account that can hold money and earn interest.
    """
    def __init__(self, account_type="Checking"):
        self.account_type = account_type
        self.balance = 0
        self.interest_rate = 0.01 if account_type == "Savings" else 0.0
        self.transaction_history = []

    def deposit(self, amount):
        """Deposit money into the account."""
        if amount > 0:
            self.balance += amount
            self.transaction_history.append({"type": "deposit", "amount": amount})
            return True
        return False

    def withdraw(self, amount):
        """Withdraw money from the account if sufficient funds are available."""
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.transaction_history.append({"type": "withdrawal", "amount": amount})
            return True
        return False

    def apply_interest(self):
        """Apply interest to the account balance (for savings accounts)."""
        if self.account_type == "Savings" and self.balance > 0:
            interest = self.balance * self.interest_rate
            self.balance += interest
            self.transaction_history.append({"type": "interest", "amount": interest})
            return interest
        return 0

class Card:
    """
    Represents a payment card (debit or credit).
    """
    def __init__(self, card_type, limit=0):
        self.card_type = card_type
        self.limit = limit
        self.balance = 0
        self.transaction_history = []

    def charge(self, amount):
        """
        Charge an amount to the card.
        For debit cards, this is a placeholder as they use the bank account directly.
        For credit cards, this adds to the balance if within the limit.
        """
        if amount <= 0:
            return False
            
        if self.card_type == "Credit":
            if self.balance + amount <= self.limit:
                self.balance += amount
                self.transaction_history.append({"type": "charge", "amount": amount})
                return True
            return False
        return True  # Debit cards don't track balance here

    def pay(self, amount):
        """Pay off some of the credit card balance."""
        if self.card_type == "Credit" and 0 < amount <= self.balance:
            self.balance -= amount
            self.transaction_history.append({"type": "payment", "amount": amount})
            return True
        return False

class Loan:
    """
    Represents a loan with principal, interest rate, and term.
    """
    def __init__(self, loan_type, amount, interest_rate, term_years):
        self.loan_type = loan_type
        self.original_amount = amount
        self.current_balance = amount
        self.interest_rate = interest_rate
        self.term_years = term_years
        self.monthly_payment = self.calculate_payment()
        self.payment_history = []

    def calculate_payment(self):
        """Calculate the monthly payment for the loan."""
        r = self.interest_rate / 12  # Monthly interest rate
        n = self.term_years * 12     # Total number of payments
        if r == 0:  # Handle zero interest case
            return self.original_amount / n
        return (self.original_amount * r * (1 + r) ** n) / ((1 + r) ** n - 1)

    def make_payment(self, amount):
        """Make a payment on the loan."""
        if amount <= 0:
            return False
            
        # Apply payment to interest first, then principal
        interest_payment = self.current_balance * (self.interest_rate / 12)
        principal_payment = min(amount - interest_payment, self.current_balance)
        
        if principal_payment < 0:
            # If payment doesn't cover interest, all goes to interest
            interest_payment = amount
            principal_payment = 0
            
        self.current_balance -= principal_payment
        
        if self.current_balance < 0.01:  # Handle small floating-point errors
            self.current_balance = 0
            
        self.payment_history.append({
            "amount": amount,
            "interest": interest_payment,
            "principal": principal_payment
        })
        
        return True

class Asset:
    """
    Represents an asset owned by the player (car, house, etc.).
    """
    def __init__(self, asset_type, name, value, condition="Good"):
        self.asset_type = asset_type
        self.name = name
        self.purchase_value = value
        self.current_value = value
        self.condition = condition
        self.age = 0  # Years since purchase

    def age_asset(self):
        """Age the asset by one year, affecting its value and condition."""
        self.age += 1
        
        # Update condition based on age
        if self.age > 10 and self.condition == "Good":
            self.condition = "Fair"
        elif self.age > 15 and self.condition == "Fair":
            self.condition = "Poor"
            
        # Update value based on asset type
        if self.asset_type == "Car":
            self.current_value *= 0.85  # 15% depreciation per year
        elif self.asset_type == "House":
            # Houses might appreciate
            appreciation = random.uniform(-0.05, 0.1)  # -5% to +10%
            self.current_value *= (1 + appreciation)

    def repair(self, cost):
        """Repair the asset to improve its condition."""
        self.condition = "Good"
        return cost
