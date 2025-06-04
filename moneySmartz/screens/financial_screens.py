import pygame
import random
from pygame.locals import *
from moneySmartz.constants import *
from moneySmartz.ui import Screen, Button, TextInput
from moneySmartz.models import BankAccount, Card, Loan, Asset

class BankAccountScreen(Screen):
    """
    Screen for opening a bank account.
    """
    def __init__(self, game):
        super().__init__(game)

        # Title
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE)
        self.text_font = pygame.font.SysFont('Arial', FONT_MEDIUM)

        # Account type selection
        self.selected_account_type = "Checking"

        # Buttons
        checking_button = Button(
            SCREEN_WIDTH // 2 - 220,
            SCREEN_HEIGHT // 2 - 50,
            200, 50,
            "Checking Account",
            color=BLUE if self.selected_account_type == "Checking" else GRAY,
            action=self.select_checking
        )

        savings_button = Button(
            SCREEN_WIDTH // 2 + 20,
            SCREEN_HEIGHT // 2 - 50,
            200, 50,
            "Savings Account",
            color=BLUE if self.selected_account_type == "Savings" else GRAY,
            action=self.select_savings
        )

        open_button = Button(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2 + 50,
            200, 50,
            "Open Account",
            action=self.open_account
        )

        back_button = Button(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2 + 120,
            200, 50,
            "Back",
            action=self.go_back
        )

        self.buttons = [checking_button, savings_button, open_button, back_button]

        # Initial deposit input
        self.deposit_input = TextInput(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2 + 10,
            300, 30,
            font_size=FONT_MEDIUM,
            max_length=10,
            initial_text="50"
        )

    def select_checking(self):
        """Select checking account type."""
        self.selected_account_type = "Checking"
        self.buttons[0].color = BLUE
        self.buttons[1].color = GRAY

    def select_savings(self):
        """Select savings account type."""
        self.selected_account_type = "Savings"
        self.buttons[0].color = GRAY
        self.buttons[1].color = BLUE

    def open_account(self):
        """Open the selected account type."""
        try:
            deposit_amount = float(self.deposit_input.text)
            if deposit_amount <= 0:
                return  # Invalid amount
            if deposit_amount > self.game.player.cash:
                return  # Not enough cash

            # Create account
            self.game.player.bank_account = BankAccount(self.selected_account_type)

            # Make initial deposit
            self.game.player.cash -= deposit_amount
            self.game.player.bank_account.deposit(deposit_amount)

            # If checking account, offer debit card
            if self.selected_account_type == "Checking":
                from moneySmartz.screens.base_screens import DebitCardScreen
                self.game.gui_manager.set_screen(DebitCardScreen(self.game))
            else:
                from moneySmartz.screens.game_screen import GameScreen
                self.game.gui_manager.set_screen(GameScreen(self.game))
        except ValueError:
            # Invalid input, do nothing
            pass

    def go_back(self):
        """Go back to the game screen."""
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def handle_events(self, events):
        """Handle pygame events."""
        super().handle_events(events)
        self.deposit_input.update(events)

    def draw(self, surface):
        """Draw the bank account screen."""
        # Background
        surface.fill(WHITE)

        # Title
        title_surface = self.title_font.render("Open a Bank Account", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        surface.blit(title_surface, title_rect)

        # Explanation text
        text_lines = [
            "You can open a checking account for everyday transactions",
            "or a savings account that earns interest.",
            "",
            f"Your current cash: ${self.game.player.cash:.2f}",
            "",
            "Initial deposit amount:"
        ]

        for i, line in enumerate(text_lines):
            text_surface = self.text_font.render(line, True, BLACK)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 150 + i * 30))
            surface.blit(text_surface, text_rect)

        # Draw deposit input
        self.deposit_input.draw(surface)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class BankDetailsScreen(Screen):
    """
    Screen for viewing bank account details.
    """
    def __init__(self, game):
        super().__init__(game)

        # Title
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE)
        self.text_font = pygame.font.SysFont('Arial', FONT_MEDIUM)

        # Transaction history scroll
        self.scroll_position = 0
        self.max_visible_transactions = 10

        # Buttons
        back_button = Button(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT - 80,
            200, 50,
            "Back",
            action=self.go_back
        )

        scroll_up_button = Button(
            SCREEN_WIDTH - 80,
            150,
            60, 30,
            "▲",
            action=self.scroll_up
        )

        scroll_down_button = Button(
            SCREEN_WIDTH - 80,
            SCREEN_HEIGHT - 150,
            60, 30,
            "▼",
            action=self.scroll_down
        )

        self.buttons = [back_button, scroll_up_button, scroll_down_button]

    def scroll_up(self):
        """Scroll transaction history up."""
        if self.scroll_position > 0:
            self.scroll_position -= 1

    def scroll_down(self):
        """Scroll transaction history down."""
        if self.scroll_position < max(0, len(self.game.player.bank_account.transaction_history) - self.max_visible_transactions):
            self.scroll_position += 1

    def go_back(self):
        """Go back to the game screen."""
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def draw(self, surface):
        """Draw the bank details screen."""
        # Background
        surface.fill(WHITE)

        # Title
        title_surface = self.title_font.render("Bank Account Details", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        surface.blit(title_surface, title_rect)

        # Account info
        account_type = self.game.player.bank_account.account_type
        balance = self.game.player.bank_account.balance

        info_lines = [
            f"Account Type: {account_type}",
            f"Current Balance: ${balance:.2f}"
        ]

        if account_type == "Savings":
            interest_rate = self.game.player.bank_account.interest_rate * 100
            annual_interest = balance * self.game.player.bank_account.interest_rate
            info_lines.extend([
                f"Interest Rate: {interest_rate:.1f}% annually",
                f"Projected Annual Interest: ${annual_interest:.2f}"
            ])

        if self.game.player.debit_card:
            info_lines.append("You have a debit card linked to this account.")

        for i, line in enumerate(info_lines):
            text_surface = self.text_font.render(line, True, BLACK)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 100 + i * 30))
            surface.blit(text_surface, text_rect)

        # Transaction history
        history_title = self.title_font.render("Transaction History", True, BLACK)
        history_rect = history_title.get_rect(center=(SCREEN_WIDTH // 2, 250))
        surface.blit(history_title, history_rect)

        # Draw transaction list
        if self.game.player.bank_account.transaction_history:
            # Draw scrollable area background
            scroll_area = pygame.Rect(100, 280, SCREEN_WIDTH - 200, 300)
            pygame.draw.rect(surface, LIGHT_GRAY, scroll_area)
            pygame.draw.rect(surface, BLACK, scroll_area, 2)  # Border

            # Get visible transactions
            visible_transactions = self.game.player.bank_account.transaction_history[
                self.scroll_position:self.scroll_position + self.max_visible_transactions
            ]

            for i, transaction in enumerate(visible_transactions):
                if transaction["type"] == "deposit":
                    text = f"Deposit: +${transaction['amount']:.2f}"
                    color = GREEN
                elif transaction["type"] == "withdrawal":
                    text = f"Withdrawal: -${transaction['amount']:.2f}"
                    color = RED
                elif transaction["type"] == "interest":
                    text = f"Interest: +${transaction['amount']:.2f}"
                    color = BLUE
                else:
                    text = f"{transaction['type']}: ${transaction['amount']:.2f}"
                    color = BLACK

                text_surface = self.text_font.render(text, True, color)
                text_rect = text_surface.get_rect(midleft=(120, 300 + i * 30))
                surface.blit(text_surface, text_rect)
        else:
            no_transactions = self.text_font.render("No transactions yet.", True, BLACK)
            no_transactions_rect = no_transactions.get_rect(center=(SCREEN_WIDTH // 2, 320))
            surface.blit(no_transactions, no_transactions_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class DepositScreen(Screen):
    """
    Screen for depositing money to a bank account.
    """
    def __init__(self, game):
        super().__init__(game)

        # Title
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE)
        self.text_font = pygame.font.SysFont('Arial', FONT_MEDIUM)

        # Amount input
        self.amount_input = TextInput(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2,
            300, 40,
            font_size=FONT_MEDIUM,
            max_length=10
        )

        # Buttons
        deposit_button = Button(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2 + 60,
            200, 50,
            "Deposit",
            action=self.make_deposit
        )

        back_button = Button(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2 + 130,
            200, 50,
            "Back",
            action=self.go_back
        )

        self.buttons = [deposit_button, back_button]

        # Status message
        self.status_message = ""
        self.status_color = BLACK

    def make_deposit(self):
        """Make a deposit to the bank account."""
        try:
            amount = float(self.amount_input.text)
            if amount <= 0:
                self.status_message = "Please enter a positive amount."
                self.status_color = RED
                return

            if amount > self.game.player.cash:
                self.status_message = "You don't have that much cash."
                self.status_color = RED
                return

            # Make deposit
            self.game.player.cash -= amount
            self.game.player.bank_account.deposit(amount)

            self.status_message = f"Successfully deposited ${amount:.2f}."
            self.status_color = GREEN

            # Clear input
            self.amount_input.text = ""
        except ValueError:
            self.status_message = "Please enter a valid number."
            self.status_color = RED

    def go_back(self):
        """Go back to the game screen."""
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def handle_events(self, events):
        """Handle pygame events."""
        super().handle_events(events)
        self.amount_input.update(events)

    def draw(self, surface):
        """Draw the deposit screen."""
        # Background
        surface.fill(WHITE)

        # Title
        title_surface = self.title_font.render("Deposit to Bank", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        surface.blit(title_surface, title_rect)

        # Info text
        info_lines = [
            f"Your current cash: ${self.game.player.cash:.2f}",
            f"Your current bank balance: ${self.game.player.bank_account.balance:.2f}",
            "",
            "How much would you like to deposit?"
        ]

        for i, line in enumerate(info_lines):
            text_surface = self.text_font.render(line, True, BLACK)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 150 + i * 30))
            surface.blit(text_surface, text_rect)

        # Draw amount input
        self.amount_input.draw(surface)

        # Draw status message
        if self.status_message:
            status_surface = self.text_font.render(self.status_message, True, self.status_color)
            status_rect = status_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            surface.blit(status_surface, status_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class WithdrawScreen(Screen):
    """
    Screen for withdrawing money from a bank account.
    """
    def __init__(self, game):
        super().__init__(game)

        # Title
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE)
        self.text_font = pygame.font.SysFont('Arial', FONT_MEDIUM)

        # Amount input
        self.amount_input = TextInput(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2,
            300, 40,
            font_size=FONT_MEDIUM,
            max_length=10
        )

        # Buttons
        withdraw_button = Button(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2 + 60,
            200, 50,
            "Withdraw",
            action=self.make_withdrawal
        )

        back_button = Button(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2 + 130,
            200, 50,
            "Back",
            action=self.go_back
        )

        self.buttons = [withdraw_button, back_button]

        # Status message
        self.status_message = ""
        self.status_color = BLACK

    def make_withdrawal(self):
        """Make a withdrawal from the bank account."""
        try:
            amount = float(self.amount_input.text)
            if amount <= 0:
                self.status_message = "Please enter a positive amount."
                self.status_color = RED
                return

            if amount > self.game.player.bank_account.balance:
                self.status_message = "You don't have that much in your account."
                self.status_color = RED
                return

            # Make withdrawal
            self.game.player.bank_account.withdraw(amount)
            self.game.player.cash += amount

            self.status_message = f"Successfully withdrew ${amount:.2f}."
            self.status_color = GREEN

            # Clear input
            self.amount_input.text = ""
        except ValueError:
            self.status_message = "Please enter a valid number."
            self.status_color = RED

    def go_back(self):
        """Go back to the game screen."""
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def handle_events(self, events):
        """Handle pygame events."""
        super().handle_events(events)
        self.amount_input.update(events)

    def draw(self, surface):
        """Draw the withdraw screen."""
        # Background
        surface.fill(WHITE)

        # Title
        title_surface = self.title_font.render("Withdraw from Bank", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        surface.blit(title_surface, title_rect)

        # Info text
        info_lines = [
            f"Your current cash: ${self.game.player.cash:.2f}",
            f"Your current bank balance: ${self.game.player.bank_account.balance:.2f}",
            "",
            "How much would you like to withdraw?"
        ]

        for i, line in enumerate(info_lines):
            text_surface = self.text_font.render(line, True, BLACK)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 150 + i * 30))
            surface.blit(text_surface, text_rect)

        # Draw amount input
        self.amount_input.draw(surface)

        # Draw status message
        if self.status_message:
            status_surface = self.text_font.render(self.status_message, True, self.status_color)
            status_rect = status_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            surface.blit(status_surface, status_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class GetDebitCardScreen(Screen):
    """
    Screen for getting a debit card.
    """
    def __init__(self, game):
        super().__init__(game)

        # Title
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE)
        self.text_font = pygame.font.SysFont('Arial', FONT_MEDIUM)

        # Buttons
        get_card_button = Button(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2 + 50,
            200, 50,
            "Get Debit Card",
            action=self.get_debit_card
        )

        back_button = Button(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2 + 120,
            200, 50,
            "Back",
            action=self.go_back
        )

        self.buttons = [get_card_button, back_button]

    def get_debit_card(self):
        """Get a debit card and go back to the game screen."""
        self.game.player.debit_card = Card("Debit")
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def go_back(self):
        """Go back to the game screen."""
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def draw(self, surface):
        """Draw the debit card screen."""
        # Background
        surface.fill(WHITE)

        # Title
        title_surface = self.title_font.render("Get a Debit Card", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        surface.blit(title_surface, title_rect)

        # Card image (simple rectangle)
        card_rect = pygame.Rect(SCREEN_WIDTH // 2 - 125, 150, 250, 150)
        pygame.draw.rect(surface, BLUE, card_rect)
        pygame.draw.rect(surface, BLACK, card_rect, 2)  # Border

        # Card text
        card_title = self.text_font.render("DEBIT", True, WHITE)
        card_title_rect = card_title.get_rect(center=(SCREEN_WIDTH // 2, 180))
        surface.blit(card_title, card_title_rect)

        card_name = self.text_font.render(self.game.player.name, True, WHITE)
        card_name_rect = card_name.get_rect(center=(SCREEN_WIDTH // 2, 220))
        surface.blit(card_name, card_name_rect)

        card_number = self.text_font.render("**** **** **** 1234", True, WHITE)
        card_number_rect = card_number.get_rect(center=(SCREEN_WIDTH // 2, 260))
        surface.blit(card_number, card_number_rect)

        # Explanation text
        text_lines = [
            "A debit card allows you to make purchases directly from your checking account.",
            "There is no fee for this card.",
            "",
            "Would you like to get a debit card?"
        ]

        for i, line in enumerate(text_lines):
            text_surface = self.text_font.render(line, True, BLACK)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 350 + i * 30))
            surface.blit(text_surface, text_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

# Placeholder classes for the remaining financial screens
# These would be implemented similarly to the above screens

class CreditCardScreen(Screen):
    """
    Screen for applying for a credit card.
    """
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont('Arial', FONT_MEDIUM)
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE, bold=True)
        self.small_font = pygame.font.SysFont('Arial', FONT_SMALL)
        self.message = ""
        self.message_color = BLACK
        self.approved = False
        self.credit_limit = 0

        # Create back button
        back_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 70, 
            200, 50, 
            "Back", 
            action=self.go_back
        )

        self.buttons = [back_button]

        # Check eligibility and create apply button if eligible
        self.check_eligibility()

    def go_back(self):
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def check_eligibility(self):
        # Check if player is eligible for a credit card
        if self.game.player.age < 18:
            self.message = "You must be at least 18 years old to apply for a credit card."
            self.message_color = RED
        elif self.game.player.credit_card:
            self.message = "You already have a credit card."
            self.message_color = BLUE
        elif not self.game.player.job:
            self.message = "You need a job to qualify for a credit card."
            self.message_color = RED
        else:
            self.message = "You are eligible to apply for a credit card. Your approval and credit limit will be based on your income and credit score."
            self.message_color = GREEN

            # Add apply button
            apply_button = Button(
                SCREEN_WIDTH // 2 - 100,
                SCREEN_HEIGHT // 2,
                200, 50,
                "Apply Now",
                color=GREEN,
                hover_color=LIGHT_GREEN,
                action=self.apply_for_card
            )

            self.buttons.append(apply_button)

    def apply_for_card(self):
        # Calculate credit limit based on income and credit score
        base_limit = min(self.game.player.salary * 0.2, 5000)  # 20% of salary or $5000, whichever is lower

        # Adjust based on credit score
        if self.game.player.credit_score >= 750:
            self.credit_limit = base_limit * 1.5
        elif self.game.player.credit_score >= 700:
            self.credit_limit = base_limit * 1.2
        elif self.game.player.credit_score >= 650:
            self.credit_limit = base_limit
        elif self.game.player.credit_score >= 600:
            self.credit_limit = base_limit * 0.8
        else:
            self.credit_limit = base_limit * 0.5

        # Approve the card
        self.game.player.credit_card = Card("Credit", self.credit_limit)
        self.approved = True

        # Update message
        self.message = f"Congratulations! You've been approved for a credit card with a limit of ${self.credit_limit:.2f}. Use your credit card wisely to build your credit score."
        self.message_color = GREEN

        # Remove apply button
        self.buttons = [self.buttons[0]]  # Keep only the back button

        # Add view details button
        details_button = Button(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT // 2,
            200, 50,
            "View Card Details",
            action=self.view_card_details
        )

        self.buttons.append(details_button)

    def view_card_details(self):
        from moneySmartz.screens.financial_screens import CreditCardDetailsScreen
        self.game.gui_manager.set_screen(CreditCardDetailsScreen(self.game))

    def draw(self, surface):
        surface.fill(WHITE)

        # Draw header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        pygame.draw.rect(surface, PURPLE, header_rect)

        header_text = self.title_font.render("CREDIT CARD APPLICATION", True, WHITE)
        header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        surface.blit(header_text, header_rect)

        # Draw player info
        info_y = 100
        credit_score_text = self.font.render(f"Your Credit Score: {self.game.player.credit_score}", True, BLACK)
        surface.blit(credit_score_text, (50, info_y))

        if self.game.player.job:
            income_text = self.font.render(f"Annual Income: ${self.game.player.salary}", True, BLACK)
            surface.blit(income_text, (50, info_y + 30))

        # Draw message
        message_lines = []
        words = self.message.split()
        current_line = []

        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 60:  # Adjust based on font size
                message_lines.append(' '.join(current_line[:-1]))
                current_line = [current_line[-1]]

        if current_line:
            message_lines.append(' '.join(current_line))

        for i, line in enumerate(message_lines):
            message_text = self.font.render(line, True, self.message_color)
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, 180 + i * 30))
            surface.blit(message_text, message_rect)

        # If approved, draw the credit card
        if self.approved:
            card_rect = pygame.Rect(SCREEN_WIDTH // 2 - 125, 250, 250, 150)
            pygame.draw.rect(surface, PURPLE, card_rect)
            pygame.draw.rect(surface, BLACK, card_rect, 2)  # Border

            # Card text
            card_title = self.font.render("CREDIT CARD", True, WHITE)
            card_title_rect = card_title.get_rect(center=(SCREEN_WIDTH // 2, 280))
            surface.blit(card_title, card_title_rect)

            card_name = self.font.render(self.game.player.name, True, WHITE)
            card_name_rect = card_name.get_rect(center=(SCREEN_WIDTH // 2, 320))
            surface.blit(card_name, card_name_rect)

            card_number = self.font.render("**** **** **** 1234", True, WHITE)
            card_number_rect = card_number.get_rect(center=(SCREEN_WIDTH // 2, 350))
            surface.blit(card_number, card_number_rect)

            limit_text = self.small_font.render(f"Credit Limit: ${self.credit_limit:.2f}", True, WHITE)
            limit_rect = limit_text.get_rect(center=(SCREEN_WIDTH // 2, 380))
            surface.blit(limit_text, limit_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class CreditCardDetailsScreen(Screen):
    """
    Screen for viewing credit card details.
    """
    def __init__(self, game):
        super().__init__(game)
        self.buttons = [Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50, "Back", action=self.go_back)]

    def go_back(self):
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def draw(self, surface):
        surface.fill(WHITE)
        # This would be implemented with credit card details display

class PayCreditCardScreen(Screen):
    """
    Screen for paying a credit card.
    """
    def __init__(self, game):
        super().__init__(game)
        self.buttons = [Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50, "Back", action=self.go_back)]

    def go_back(self):
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def draw(self, surface):
        surface.fill(WHITE)
        # This would be implemented with credit card payment logic

class LoanDetailsScreen(Screen):
    """
    Screen for viewing loan details.
    """
    def __init__(self, game):
        super().__init__(game)
        self.buttons = [Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50, "Back", action=self.go_back)]

    def go_back(self):
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def draw(self, surface):
        surface.fill(WHITE)
        # This would be implemented with loan details display

class ExtraLoanPaymentScreen(Screen):
    """
    Screen for making an extra loan payment.
    """
    def __init__(self, game):
        super().__init__(game)
        self.buttons = [Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50, "Back", action=self.go_back)]

    def go_back(self):
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def draw(self, surface):
        surface.fill(WHITE)
        # This would be implemented with extra loan payment logic

class AssetDetailsScreen(Screen):
    """
    Screen for viewing asset details.
    """
    def __init__(self, game):
        super().__init__(game)
        self.buttons = [Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50, "Back", action=self.go_back)]

    def go_back(self):
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def draw(self, surface):
        surface.fill(WHITE)
        # This would be implemented with asset details display

class JobSearchScreen(Screen):
    """
    Screen for searching for a job.
    """
    def __init__(self, game):
        super().__init__(game)

        # Title and fonts
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE)
        self.text_font = pygame.font.SysFont('Arial', FONT_MEDIUM)

        # Generate job options based on education and experience
        self.job_options = self.generate_job_options()

        # Create buttons for job options
        self.buttons = [Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50, "Back", action=self.go_back)]

        # Add job option buttons if jobs are available
        if self.job_options:
            y_pos = 250
            for i, job in enumerate(self.job_options):
                self.buttons.append(
                    Button(
                        SCREEN_WIDTH // 2 - 200,
                        y_pos + i * 60,
                        400, 50,
                        f"{job['title']} - ${job['salary']}/year",
                        action=lambda j=job: self.apply_for_job(j)
                    )
                )

        # Status message
        self.status_message = ""
        self.status_color = BLACK

    def generate_job_options(self):
        """Generate job options based on player's education and experience."""
        job_options = []

        # Current job info
        current_salary = self.game.player.salary if self.game.player.job else 0

        # Base salary multiplier based on years of experience
        experience_years = max(0, self.game.player.age - 18)  # Assume working age starts at 18
        experience_multiplier = 1.0 + (experience_years * 0.03)  # 3% increase per year of experience

        # Generate job options based on education
        if self.game.player.education == "High School" or self.game.player.education == "High School Graduate":
            job_options = [
                {"title": "Retail Associate", "salary": int(25000 * experience_multiplier)},
                {"title": "Food Service Worker", "salary": int(22000 * experience_multiplier)},
                {"title": "Warehouse Worker", "salary": int(28000 * experience_multiplier)},
                {"title": "Office Clerk", "salary": int(30000 * experience_multiplier)},
            ]
        elif self.game.player.education == "Trade School":
            job_options = [
                {"title": "Electrician", "salary": int(45000 * experience_multiplier)},
                {"title": "Plumber", "salary": int(48000 * experience_multiplier)},
                {"title": "HVAC Technician", "salary": int(50000 * experience_multiplier)},
                {"title": "Automotive Mechanic", "salary": int(42000 * experience_multiplier)},
            ]
        elif self.game.player.education == "College Graduate":
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
        if self.game.player.job:
            job_options = [job for job in job_options if job["salary"] >= current_salary * 1.05]

        return job_options

    def apply_for_job(self, job):
        """Apply for the selected job."""
        # Job application success chance based on qualifications
        base_success_chance = 0.7  # 70% base chance

        # Adjust for education
        if self.game.player.education == "College Graduate":
            base_success_chance += 0.2
        elif self.game.player.education == "Trade School":
            base_success_chance += 0.1

        # Adjust for experience
        experience_years = max(0, self.game.player.age - 18)
        base_success_chance += min(0.2, experience_years * 0.01)  # Up to 20% bonus for experience

        # Cap at 95% chance
        success_chance = min(0.95, base_success_chance)

        # Determine if application is successful
        if random.random() < success_chance:
            old_job = self.game.player.job
            old_salary = self.game.player.salary

            self.game.player.job = job["title"]
            self.game.player.salary = job["salary"]

            if old_job:
                salary_increase = self.game.player.salary - old_salary
                percent_increase = (salary_increase / old_salary) * 100
                self.status_message = f"Congratulations! You got the job! That's a raise of ${salary_increase}/year ({percent_increase:.1f}%)!"
            else:
                self.status_message = f"Congratulations! You got the job! You are now earning ${self.game.player.salary}/year."

            self.status_color = GREEN

            # Disable job buttons after getting a job
            self.buttons = [self.buttons[0]]  # Keep only the back button
        else:
            self.status_message = "Unfortunately, the company decided to go with another candidate. Try again!"
            self.status_color = RED

    def go_back(self):
        """Go back to the game screen."""
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def draw(self, surface):
        """Draw the job search screen."""
        # Background
        surface.fill(WHITE)

        # Title
        title_surface = self.title_font.render("Job Search", True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
        surface.blit(title_surface, title_rect)

        # Current job info
        current_job_text = f"Current Job: {self.game.player.job if self.game.player.job else 'Unemployed'}"
        current_job_surface = self.text_font.render(current_job_text, True, BLACK)
        current_job_rect = current_job_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(current_job_surface, current_job_rect)

        if self.game.player.job:
            salary_text = f"Current Salary: ${self.game.player.salary}/year"
            salary_surface = self.text_font.render(salary_text, True, BLACK)
            salary_rect = salary_surface.get_rect(center=(SCREEN_WIDTH // 2, 130))
            surface.blit(salary_surface, salary_rect)

        # Available jobs or no jobs message
        if self.job_options:
            jobs_title = self.text_font.render("Available Job Opportunities:", True, BLACK)
            jobs_title_rect = jobs_title.get_rect(center=(SCREEN_WIDTH // 2, 180))
            surface.blit(jobs_title, jobs_title_rect)

            jobs_subtitle = self.text_font.render("Click on a job to apply", True, BLACK)
            jobs_subtitle_rect = jobs_subtitle.get_rect(center=(SCREEN_WIDTH // 2, 210))
            surface.blit(jobs_subtitle, jobs_subtitle_rect)
        else:
            no_jobs_text = "No better job opportunities available at this time."
            no_jobs_surface = self.text_font.render(no_jobs_text, True, BLACK)
            no_jobs_rect = no_jobs_surface.get_rect(center=(SCREEN_WIDTH // 2, 200))
            surface.blit(no_jobs_surface, no_jobs_rect)

            advice_text = "Keep building your skills and try again later!"
            advice_surface = self.text_font.render(advice_text, True, BLACK)
            advice_rect = advice_surface.get_rect(center=(SCREEN_WIDTH // 2, 230))
            surface.blit(advice_surface, advice_rect)

        # Status message
        if self.status_message:
            # Split long messages into multiple lines
            words = self.status_message.split()
            lines = []
            current_line = []

            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 50:  # Adjust based on your font size
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [current_line[-1]]

            if current_line:
                lines.append(' '.join(current_line))

            for i, line in enumerate(lines):
                status_surface = self.text_font.render(line, True, self.status_color)
                status_rect = status_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150 + i * 30))
                surface.blit(status_surface, status_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
