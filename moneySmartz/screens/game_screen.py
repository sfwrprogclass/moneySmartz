import pygame
import random
from pygame.locals import *
from moneySmartz.constants import *
from moneySmartz.ui import Screen, Button

class GameScreen(Screen):
    """
    The main game screen that shows the player's status and allows them to take actions.
    """
    play_startup_music = False  # Disable music for this screen
    
    def __init__(self, game):
        super().__init__(game)
        self.create_buttons()

    def create_buttons(self):
        """Create the buttons for the game screen."""
        # Clear existing buttons
        self.buttons = []

        # Continue button (always present)
        continue_button = Button(
            SCREEN_WIDTH - 220, 
            SCREEN_HEIGHT - 60,
            200, 50,
            "Continue to Next Month",
            action=self.continue_to_next_month
        )
        self.buttons.append(continue_button)

        # Banking buttons
        if not self.game.player.bank_account:
            bank_button = Button(
                20, 
                SCREEN_HEIGHT - 270,
                200, 50,
                "Open Bank Account",
                action=self.open_bank_account
            )
            self.buttons.append(bank_button)
        else:
            view_bank_button = Button(
                20, 
                SCREEN_HEIGHT - 270,
                200, 50,
                "View Bank Account",
                action=self.view_bank_account
            )
            self.buttons.append(view_bank_button)

            deposit_button = Button(
                20, 
                SCREEN_HEIGHT - 210,
                200, 50,
                "Deposit to Bank",
                action=self.deposit_to_bank
            )
            self.buttons.append(deposit_button)

            withdraw_button = Button(
                20, 
                SCREEN_HEIGHT - 150,
                200, 50,
                "Withdraw from Bank",
                action=self.withdraw_from_bank
            )
            self.buttons.append(withdraw_button)

            if not self.game.player.debit_card:
                debit_button = Button(
                    20, 
                    SCREEN_HEIGHT - 90,
                    200, 50,
                    "Get Debit Card",
                    action=self.get_debit_card
                )
                self.buttons.append(debit_button)

        # Credit card buttons
        if not self.game.player.credit_card and self.game.player.age >= 18:
            credit_button = Button(
                240, 
                SCREEN_HEIGHT - 270,
                200, 50,
                "Apply for Credit Card",
                action=self.apply_for_credit_card
            )
            self.buttons.append(credit_button)
        elif self.game.player.credit_card:
            view_credit_button = Button(
                240, 
                SCREEN_HEIGHT - 270,
                200, 50,
                "View Credit Card",
                action=self.view_credit_card
            )
            self.buttons.append(view_credit_button)

            if self.game.player.credit_card.balance > 0:
                pay_credit_button = Button(
                    240, 
                    SCREEN_HEIGHT - 210,
                    200, 50,
                    "Pay Credit Card",
                    action=self.pay_credit_card
                )
                self.buttons.append(pay_credit_button)

        # Loan buttons
        if self.game.player.loans:
            view_loans_button = Button(
                240, 
                SCREEN_HEIGHT - 150,
                200, 50,
                "View Loans",
                action=self.view_loans
            )
            self.buttons.append(view_loans_button)

            pay_loan_button = Button(
                240, 
                SCREEN_HEIGHT - 90,
                200, 50,
                "Make Extra Loan Payment",
                action=self.make_extra_loan_payment
            )
            self.buttons.append(pay_loan_button)

        # Asset buttons
        if self.game.player.assets:
            view_assets_button = Button(
                460, 
                SCREEN_HEIGHT - 270,
                200, 50,
                "View Assets",
                action=self.view_assets
            )
            self.buttons.append(view_assets_button)

        # Job buttons
        if not self.game.player.job and self.game.player.age >= 16:
            job_button = Button(
                460, 
                SCREEN_HEIGHT - 210,
                200, 50,
                "Look for a Job",
                action=self.look_for_job
            )
            self.buttons.append(job_button)
        elif self.game.player.job and random.random() < 0.1:  # 10% chance of job opportunity each month
            better_job_button = Button(
                460, 
                SCREEN_HEIGHT - 210,
                200, 50,
                "Look for a Better Job",
                action=self.look_for_job
            )
            self.buttons.append(better_job_button)

        # --- System Control Buttons ---
        pause_button = Button(
            SCREEN_WIDTH - 220,
            20,
            90, 40,
            "Pause",
            action=self.pause_game
        )
        self.buttons.append(pause_button)

        play_button = Button(
            SCREEN_WIDTH - 120,
            20,
            90, 40,
            "Play",
            action=self.play_game
        )
        self.buttons.append(play_button)

        save_button = Button(
            SCREEN_WIDTH - 220,
            70,
            90, 40,
            "Save",
            action=self.save_game
        )
        self.buttons.append(save_button)

        quit_button = Button(
            SCREEN_WIDTH - 120,
            70,
            90, 40,
            "Quit",
            action=self.quit_game
        )
        self.buttons.append(quit_button)

        # --- Shop Button ---
        shop_button = Button(
            SCREEN_WIDTH - 220,
            SCREEN_HEIGHT - 120,
            200, 50,
            "Shop",
            action=self.open_shop
        )
        self.buttons.append(shop_button)

    def continue_to_next_month(self):
        """Continue to the next month."""
        # Increment month
        self.game.current_month += 1
        if self.game.current_month > 12:
            self.game.current_month = 1
            self.game.current_year += 1
            self.game.player.age += 1
            
            # Apply interest to savings
            if self.game.player.bank_account and self.game.player.bank_account.account_type == "Savings":
                self.game.player.bank_account.apply_interest()
            
            # Age assets
            for asset in self.game.player.assets:
                asset.age_asset()
        
        # Process monthly finances
        self.game.process_monthly_finances()
        
        # Random events
        if random.random() < 0.3:  # 30% chance of an event each month
            self.game.trigger_random_event()
            # Don't proceed further until event is handled
            return
        
        # Life stage events based on age
        life_event_triggered = self.game.check_life_stage_events_gui()
        
        # If no life event was triggered, refresh the game screen
        if not life_event_triggered:
            # Check game over conditions
            if self.game.player.age >= 65:  # Retirement age
                self.game.end_game_gui("retirement")
            else:
                # Refresh buttons (in case player status changed)
                self.create_buttons()

    def open_bank_account(self):
        """Open a bank account screen."""
        from moneySmartz.screens.financial_screens import BankAccountScreen
        self.game.gui_manager.set_screen(BankAccountScreen(self.game))

    def view_bank_account(self):
        """View bank account details."""
        from moneySmartz.screens.financial_screens import BankDetailsScreen
        self.game.gui_manager.set_screen(BankDetailsScreen(self.game))

    def deposit_to_bank(self):
        """Deposit money to bank account."""
        from moneySmartz.screens.financial_screens import DepositScreen
        self.game.gui_manager.set_screen(DepositScreen(self.game))

    def withdraw_from_bank(self):
        """Withdraw money from bank account."""
        from moneySmartz.screens.financial_screens import WithdrawScreen
        self.game.gui_manager.set_screen(WithdrawScreen(self.game))

    def get_debit_card(self):
        """Get a debit card."""
        from moneySmartz.screens.financial_screens import GetDebitCardScreen
        self.game.gui_manager.set_screen(GetDebitCardScreen(self.game))

    def apply_for_credit_card(self):
        """Apply for a credit card."""
        from moneySmartz.screens.financial_screens import CreditCardScreen
        self.game.gui_manager.set_screen(CreditCardScreen(self.game))

    def view_credit_card(self):
        """View credit card details."""
        from moneySmartz.screens.financial_screens import CreditCardDetailsScreen
        self.game.gui_manager.set_screen(CreditCardDetailsScreen(self.game))

    def pay_credit_card(self):
        """Make a payment on the credit card."""
        from moneySmartz.screens.financial_screens import PayCreditCardScreen
        self.game.gui_manager.set_screen(PayCreditCardScreen(self.game))

    def view_loans(self):
        """View loan details."""
        from moneySmartz.screens.financial_screens import LoanDetailsScreen
        self.game.gui_manager.set_screen(LoanDetailsScreen(self.game))

    def make_extra_loan_payment(self):
        """Make an extra payment on a loan."""
        from moneySmartz.screens.financial_screens import ExtraLoanPaymentScreen
        self.game.gui_manager.set_screen(ExtraLoanPaymentScreen(self.game))

    def view_assets(self):
        """View asset details."""
        from moneySmartz.screens.financial_screens import AssetDetailsScreen
        self.game.gui_manager.set_screen(AssetDetailsScreen(self.game))

    def look_for_job(self):
        """Look for a job or a better job."""
        from moneySmartz.screens.financial_screens import JobSearchScreen
        self.game.gui_manager.set_screen(JobSearchScreen(self.game))

    def open_shop(self):
        """Open the shop screen."""
        from moneySmartz.screens.shop_screen import ShopScreen
        self.game.gui_manager.set_screen(ShopScreen(self.game))

    def pause_game(self):
        """Pause the game (stops updates, disables actions)."""
        self.game.paused = True
        # Optionally, show a pause overlay or message

    def play_game(self):
        """Resume the game from pause."""
        self.game.paused = False
        # Optionally, hide pause overlay or message

    def save_game(self):
        """Save the current game state."""
        self.game.save_state()
        # Optionally, show a 'Game Saved' message

    def quit_game(self):
        """Quit the game and return to main menu or exit."""
        self.game.quit()

    def draw(self, surface):
        """Draw the game screen."""
        # Background
        surface.fill(WHITE)

        # Header
        pygame.draw.rect(surface, BLUE, (0, 0, SCREEN_WIDTH, 80))

        # Title
        title_font = pygame.font.SysFont('Arial', FONT_LARGE)
        title_surface = title_font.render(f"MONTH: {self.game.current_month}/YEAR: {self.game.current_year + 2023}", True, WHITE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 25))
        surface.blit(title_surface, title_rect)

        age_surface = title_font.render(f"AGE: {self.game.player.age}", True, WHITE)
        age_rect = age_surface.get_rect(center=(SCREEN_WIDTH // 2, 55))
        surface.blit(age_surface, age_rect)

        # Player info section
        info_font = pygame.font.SysFont('Arial', FONT_MEDIUM)

        # Name and education
        self.draw_text(surface, f"Name: {self.game.player.name}", 20, 100)
        self.draw_text(surface, f"Education: {self.game.player.education}", 20, 130)

        # Job and salary
        job_text = f"Job: {self.game.player.job if self.game.player.job else 'Unemployed'}"
        self.draw_text(surface, job_text, 20, 160)

        if self.game.player.job:
            salary_text = f"Salary: ${self.game.player.salary}/year (${self.game.player.salary/12:.2f}/month)"
            self.draw_text(surface, salary_text, 40, 190)

        # Financial info
        self.draw_text(surface, f"Cash: ${self.game.player.cash:.2f}", 20, 230)

        if self.game.player.bank_account:
            bank_text = f"Bank Account ({self.game.player.bank_account.account_type}): ${self.game.player.bank_account.balance:.2f}"
            self.draw_text(surface, bank_text, 20, 260)

        if self.game.player.credit_card:
            credit_text = f"Credit Card: ${self.game.player.credit_card.balance:.2f}/{self.game.player.credit_card.limit:.2f}"
            self.draw_text(surface, credit_text, 20, 290)

        self.draw_text(surface, f"Credit Score: {self.game.player.credit_score}", 20, 320)

        # Loans
        if self.game.player.loans:
            self.draw_text(surface, "LOANS:", 400, 100)
            for i, loan in enumerate(self.game.player.loans):
                loan_text = f"{loan.loan_type}: ${loan.current_balance:.2f} (${loan.monthly_payment:.2f}/month)"
                self.draw_text(surface, loan_text, 420, 130 + i * 30)

        # Assets
        if self.game.player.assets:
            self.draw_text(surface, "ASSETS:", 400, 230)
            for i, asset in enumerate(self.game.player.assets):
                asset_text = f"{asset.name}: ${asset.current_value:.2f} ({asset.condition})"
                self.draw_text(surface, asset_text, 420, 260 + i * 30)

        # Family
        if self.game.player.family:
            self.draw_text(surface, "FAMILY:", 700, 100)
            for i, member in enumerate(self.game.player.family):
                if member["relation"] == "Spouse":
                    family_text = f"Spouse: Age {member['age'] + self.game.current_year}"
                else:
                    family_text = f"{member['relation']}: {member['name']}, Age {member['age'] + self.game.current_year}"
                self.draw_text(surface, family_text, 720, 130 + i * 30)

        # Calculate and display net worth
        cash = self.game.player.cash
        bank_balance = self.game.player.bank_account.balance if self.game.player.bank_account else 0
        credit_card_debt = self.game.player.credit_card.balance if self.game.player.credit_card else 0

        loan_debt = 0
        for loan in self.game.player.loans:
            loan_debt += loan.current_balance

        asset_value = 0
        for asset in self.game.player.assets:
            asset_value += asset.current_value

        net_worth = cash + bank_balance - credit_card_debt - loan_debt + asset_value

        # Net worth with color based on value
        if net_worth >= 0:
            net_worth_color = GREEN
        else:
            net_worth_color = RED

        net_worth_font = pygame.font.SysFont('Arial', FONT_LARGE)
        net_worth_text = f"NET WORTH: ${net_worth:.2f}"
        net_worth_surface = net_worth_font.render(net_worth_text, True, net_worth_color)
        net_worth_rect = net_worth_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 330))
        surface.blit(net_worth_surface, net_worth_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

    def draw_text(self, surface, text, x, y, is_title=False):
        """Helper method to draw text."""
        font = pygame.font.SysFont('Arial', FONT_LARGE if is_title else FONT_MEDIUM)
        text_surface = font.render(text, True, BLACK)
        surface.blit(text_surface, (x, y))
