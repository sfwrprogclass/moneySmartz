import pygame
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
        self.buttons = [Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50, "Back", action=self.go_back)]
        
    def go_back(self):
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))
        
    def draw(self, surface):
        surface.fill(WHITE)
        # This would be implemented with credit card application logic

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
        self.buttons = [Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50, "Back", action=self.go_back)]
        
    def go_back(self):
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))
        
    def draw(self, surface):
        surface.fill(WHITE)
        # This would be implemented with job search logic