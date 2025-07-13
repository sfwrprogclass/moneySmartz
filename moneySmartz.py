import random
import time
import os
import pygame
import sys
from pygame.locals import *

# Initialize pygame
pygame.init()

# GUI Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
BLUE = (0, 120, 255)
LIGHT_BLUE = (100, 180, 255)
GREEN = (0, 200, 0)
LIGHT_GREEN = (100, 255, 100)
RED = (255, 0, 0)
LIGHT_RED = (255, 100, 100)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Font sizes
FONT_SMALL = 18
FONT_MEDIUM = 24
FONT_LARGE = 32
FONT_TITLE = 48

# GUI Classes
class Button:
    def __init__(self, x, y, width, height, text, color=BLUE, hover_color=LIGHT_BLUE, text_color=WHITE, font_size=FONT_MEDIUM, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont('Arial', font_size)
        self.action = action
        self.hovered = False

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Border

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def update(self, mouse_pos, mouse_click):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and mouse_click and self.action:
            return self.action
        return None

class TextInput:
    def __init__(self, x, y, width, height, font_size=FONT_MEDIUM, max_length=20, initial_text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = initial_text
        self.font = pygame.font.SysFont('Arial', font_size)
        self.active = False
        self.max_length = max_length

    def draw(self, surface):
        color = LIGHT_BLUE if self.active else WHITE
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Border

        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        surface.blit(text_surface, text_rect)

    def update(self, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                self.active = self.rect.collidepoint(event.pos)

            if event.type == KEYDOWN and self.active:
                if event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == K_RETURN:
                    self.active = False
                elif len(self.text) < self.max_length:
                    self.text += event.unicode

        return self.text

class Screen:
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.next_screen = None

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_click = True

        for button in self.buttons:
            action = button.update(mouse_pos, mouse_click)
            if action:
                return action

        return None

    def update(self):
        pass

    def draw(self, surface):
        surface.fill(WHITE)
        for button in self.buttons:
            button.draw(surface)

class GUIManager:
    def __init__(self, game):
        self.game = game
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Money Smartz: Financial Life Simulator")
        self.clock = pygame.time.Clock()
        self.current_screen = None
        self.running = True

    def set_screen(self, screen):
        self.current_screen = screen

    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    self.running = False

            if self.current_screen:
                action = self.current_screen.handle_events(events)
                if action:
                    action()

                self.current_screen.update()
                self.current_screen.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

# Game Screens
class TitleScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont('Arial', FONT_TITLE, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', FONT_MEDIUM)

        # Create buttons
        start_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT // 2, 
            200, 60, 
            "Start Game", 
            action=lambda: self.game.gui_manager.set_screen(NameInputScreen(self.game))
        )

        quit_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT // 2 + 100, 
            200, 60, 
            "Quit", 
            color=RED,
            hover_color=LIGHT_RED,
            action=lambda: setattr(self.game.gui_manager, 'running', False)
        )

        self.buttons = [start_button, quit_button]

    def draw(self, surface):
        surface.fill(WHITE)

        # Draw title
        title_text = self.title_font.render("MONEY SMARTZ", True, BLUE)
        subtitle_text = self.subtitle_font.render("Financial Life Simulator", True, BLACK)

        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 60))

        surface.blit(title_text, title_rect)
        surface.blit(subtitle_text, subtitle_rect)

        # Draw tagline
        tagline_font = pygame.font.SysFont('Arial', FONT_SMALL)
        tagline_text = tagline_font.render("Inspired by the classic Oregon Trail", True, DARK_GRAY)
        tagline_rect = tagline_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 100))
        surface.blit(tagline_text, tagline_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class NameInputScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont('Arial', FONT_LARGE)
        self.text_input = TextInput(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 50, initial_text="")

        # Create buttons
        continue_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT // 2 + 100, 
            200, 60, 
            "Continue", 
            action=self.start_game
        )

        back_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT // 2 + 180, 
            200, 60, 
            "Back", 
            color=GRAY,
            hover_color=LIGHT_GRAY,
            action=lambda: self.game.gui_manager.set_screen(TitleScreen(self.game))
        )

        self.buttons = [continue_button, back_button]

    def start_game(self):
        name = self.text_input.text.strip()
        if name:
            self.game.player = Player(name)
            self.game.gui_manager.set_screen(IntroScreen(self.game))

    def handle_events(self, events):
        # Handle button events
        result = super().handle_events(events)

        # Handle text input
        self.text_input.update(events)

        return result

    def draw(self, surface):
        surface.fill(WHITE)

        # Draw prompt
        prompt_text = self.font.render("Enter your name:", True, BLACK)
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        surface.blit(prompt_text, prompt_rect)

        # Draw text input
        self.text_input.draw(surface)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class IntroScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont('Arial', FONT_MEDIUM)

        # Create buttons
        yes_button = Button(
            SCREEN_WIDTH // 2 - 220, 
            SCREEN_HEIGHT - 150, 
            200, 60, 
            "Yes", 
            action=self.open_bank_account
        )

        no_button = Button(
            SCREEN_WIDTH // 2 + 20, 
            SCREEN_HEIGHT - 150, 
            200, 60, 
            "No", 
            action=self.skip_bank_account
        )

        self.buttons = [yes_button, no_button]

    def open_bank_account(self):
        self.game.player.bank_account = BankAccount()
        self.game.player.bank_account.deposit(50)  # Parents give you $50 to start
        self.game.gui_manager.set_screen(DebitCardScreen(self.game))

    def skip_bank_account(self):
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def draw(self, surface):
        surface.fill(WHITE)

        # Draw welcome message
        welcome_font = pygame.font.SysFont('Arial', FONT_LARGE)
        welcome_text = welcome_font.render(f"Welcome, {self.game.player.name}!", True, BLUE)
        welcome_rect = welcome_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(welcome_text, welcome_rect)

        # Draw intro text
        lines = [
            f"You're a 16-year-old high school student.",
            "Your parents suggest that you should open your first bank account.",
            "This will help you manage your money and start building your financial future.",
            "",
            "Do you want to open a bank account?"
        ]

        for i, line in enumerate(lines):
            text = self.font.render(line, True, BLACK)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 40))
            surface.blit(text, rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class DebitCardScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont('Arial', FONT_MEDIUM)

        # Create buttons
        yes_button = Button(
            SCREEN_WIDTH // 2 - 220, 
            SCREEN_HEIGHT - 150, 
            200, 60, 
            "Yes", 
            action=self.get_debit_card
        )

        no_button = Button(
            SCREEN_WIDTH // 2 + 20, 
            SCREEN_HEIGHT - 150, 
            200, 60, 
            "No", 
            action=self.skip_debit_card
        )

        self.buttons = [yes_button, no_button]

    def get_debit_card(self):
        self.game.player.debit_card = Card("Debit")
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def skip_debit_card(self):
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def draw(self, surface):
        surface.fill(WHITE)

        # Draw congratulations message
        congrats_font = pygame.font.SysFont('Arial', FONT_LARGE)
        congrats_text = congrats_font.render("Congratulations!", True, GREEN)
        congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(congrats_text, congrats_rect)

        # Draw account info
        lines = [
            "You've opened your first checking account.",
            "Your parents deposited $50 to get you started.",
            "",
            "Would you like a debit card with your account?",
            "A debit card will allow you to make purchases and withdraw cash from ATMs."
        ]

        for i, line in enumerate(lines):
            text = self.font.render(line, True, BLACK)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 40))
            surface.blit(text, rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class GameScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont('Arial', FONT_MEDIUM)
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE, bold=True)
        self.small_font = pygame.font.SysFont('Arial', FONT_SMALL)
        self.create_buttons()

    def create_buttons(self):
        self.buttons = []

        # Continue button (always present)
        continue_button = Button(
            SCREEN_WIDTH - 220, 
            SCREEN_HEIGHT - 70, 
            200, 50, 
            "Continue to next month", 
            action=self.continue_to_next_month
        )
        self.buttons.append(continue_button)

        # Dynamic buttons based on player state
        button_y = 400
        button_height = 50
        button_spacing = 10

        # Banking actions
        if not self.game.player.bank_account:
            self.buttons.append(Button(
                20, button_y, 250, button_height, 
                "Open a bank account", 
                action=lambda: self.game.gui_manager.set_screen(BankAccountScreen(self.game))
            ))
            button_y += button_height + button_spacing
        else:
            self.buttons.append(Button(
                20, button_y, 250, button_height, 
                "View bank account details", 
                action=lambda: self.game.gui_manager.set_screen(BankDetailsScreen(self.game))
            ))
            button_y += button_height + button_spacing

            self.buttons.append(Button(
                20, button_y, 250, button_height, 
                "Deposit money to bank", 
                action=lambda: self.game.gui_manager.set_screen(DepositScreen(self.game))
            ))
            button_y += button_height + button_spacing

            self.buttons.append(Button(
                20, button_y, 250, button_height, 
                "Withdraw money from bank", 
                action=lambda: self.game.gui_manager.set_screen(WithdrawScreen(self.game))
            ))
            button_y += button_height + button_spacing

            if not self.game.player.debit_card and self.game.player.bank_account.account_type == "Checking":
                self.buttons.append(Button(
                    20, button_y, 250, button_height, 
                    "Get a debit card", 
                    action=lambda: self.game.gui_manager.set_screen(GetDebitCardScreen(self.game))
                ))
                button_y += button_height + button_spacing

        # Credit card actions
        if not self.game.player.credit_card and self.game.player.age >= 18:
            self.buttons.append(Button(
                20, button_y, 250, button_height, 
                "Apply for a credit card", 
                action=lambda: self.game.gui_manager.set_screen(CreditCardScreen(self.game))
            ))
            button_y += button_height + button_spacing
        elif self.game.player.credit_card:
            self.buttons.append(Button(
                20, button_y, 250, button_height, 
                "View credit card details", 
                action=lambda: self.game.gui_manager.set_screen(CreditCardDetailsScreen(self.game))
            ))
            button_y += button_height + button_spacing

            if self.game.player.credit_card.balance > 0:
                self.buttons.append(Button(
                    20, button_y, 250, button_height, 
                    "Make a credit card payment", 
                    action=lambda: self.game.gui_manager.set_screen(PayCreditCardScreen(self.game))
                ))
                button_y += button_height + button_spacing

        # Reset button position for second column
        button_y = 400

        # Loan actions
        if self.game.player.loans:
            self.buttons.append(Button(
                290, button_y, 250, button_height, 
                "View loan details", 
                action=lambda: self.game.gui_manager.set_screen(LoanDetailsScreen(self.game))
            ))
            button_y += button_height + button_spacing

            self.buttons.append(Button(
                290, button_y, 250, button_height, 
                "Make extra loan payment", 
                action=lambda: self.game.gui_manager.set_screen(ExtraLoanPaymentScreen(self.game))
            ))
            button_y += button_height + button_spacing

        # Asset actions
        if self.game.player.assets:
            self.buttons.append(Button(
                290, button_y, 250, button_height, 
                "View assets", 
                action=lambda: self.game.gui_manager.set_screen(AssetDetailsScreen(self.game))
            ))
            button_y += button_height + button_spacing

        # Career actions
        if self.game.player.age >= 18:
            self.buttons.append(Button(
                290, button_y, 250, button_height, 
                "Look for a better job", 
                action=lambda: self.game.gui_manager.set_screen(JobSearchScreen(self.game))
            ))
            button_y += button_height + button_spacing

        # Housing actions
        if self.game.player.age >= 22 and not any(a.asset_type == "House" for a in self.game.player.assets):
            self.buttons.append(Button(
                290, button_y, 250, button_height, 
                "Look for housing", 
                action=lambda: self.game.gui_manager.set_screen(HousingScreen(self.game))
            ))
            button_y += button_height + button_spacing

        # Family actions
        if self.game.player.age >= 25 and not self.game.player.family:
            self.buttons.append(Button(
                290, button_y, 250, button_height, 
                "Consider starting a family", 
                action=lambda: self.game.gui_manager.set_screen(FamilyPlanningScreen(self.game))
            ))
            button_y += button_height + button_spacing

        # Retirement action
        if self.game.player.age >= 60:
            self.buttons.append(Button(
                290, button_y, 250, button_height, 
                "Retire", 
                action=lambda: self.game.end_game_gui("retirement")
            ))

    def continue_to_next_month(self):
        # Advance time
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
            event_type = "positive" if random.random() < 0.5 else "negative"
            event = random.choice(self.game.events[event_type])
            cash_effect = event["cash_effect"]()

            if cash_effect != 0:
                self.game.gui_manager.set_screen(RandomEventScreen(self.game, event, cash_effect))
                return

        # Life stage events
        self.game.check_life_stage_events_gui()

        # Refresh the screen with updated info
        self.create_buttons()

        # Check game over conditions
        if self.game.player.age >= 65:  # Retirement age
            self.game.end_game_gui("retirement")

    def draw(self, surface):
        surface.fill(WHITE)

        # Draw header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        pygame.draw.rect(surface, LIGHT_BLUE, header_rect)

        header_text = self.title_font.render(f"MONEY SMARTZ - Year {self.game.current_year}, Month {self.game.current_month}", True, WHITE)
        header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        surface.blit(header_text, header_rect)

        # Draw player info
        info_x = 20
        info_y = 100

        # Basic info
        self.draw_text(surface, f"Name: {self.game.player.name}", info_x, info_y)
        self.draw_text(surface, f"Age: {self.game.player.age}", info_x, info_y + 30)
        self.draw_text(surface, f"Education: {self.game.player.education}", info_x, info_y + 60)

        # Career
        if self.game.player.job:
            self.draw_text(surface, f"Job: {self.game.player.job}", info_x, info_y + 90)
            self.draw_text(surface, f"Annual Salary: ${self.game.player.salary}", info_x, info_y + 120)
            self.draw_text(surface, f"Monthly Income: ${self.game.player.salary / 12:.2f}", info_x, info_y + 150)
        else:
            self.draw_text(surface, "Job: Unemployed", info_x, info_y + 90)

        # Financial status
        status_x = SCREEN_WIDTH // 2 + 20
        status_y = 100

        self.draw_text(surface, "FINANCIAL STATUS", status_x, status_y, is_title=True)
        self.draw_text(surface, f"Cash: ${self.game.player.cash:.2f}", status_x, status_y + 40)

        if self.game.player.bank_account:
            self.draw_text(surface, f"{self.game.player.bank_account.account_type} Account: ${self.game.player.bank_account.balance:.2f}", status_x, status_y + 70)

        if self.game.player.credit_card:
            self.draw_text(surface, f"Credit Card Balance: ${self.game.player.credit_card.balance:.2f}", status_x, status_y + 100)
            self.draw_text(surface, f"Credit Card Limit: ${self.game.player.credit_card.limit:.2f}", status_x, status_y + 130)

        self.draw_text(surface, f"Credit Score: {self.game.player.credit_score}", status_x, status_y + 160)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

    def draw_text(self, surface, text, x, y, is_title=False):
        font = self.title_font if is_title else self.font
        text_surface = font.render(text, True, BLACK)
        surface.blit(text_surface, (x, y))

class RandomEventScreen(Screen):
    def __init__(self, game, event, cash_effect):
        super().__init__(game)
        self.event = event
        self.cash_effect = cash_effect
        self.font = pygame.font.SysFont('Arial', FONT_MEDIUM)
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE, bold=True)

        # Process the event
        if cash_effect > 0:
            self.game.player.cash += cash_effect
            self.result_message = f"You received ${cash_effect}!"
        else:
            self.result_message = f"This costs you ${abs(cash_effect)}."

            # Handle payment
            if self.game.player.cash >= abs(cash_effect):
                self.game.player.cash -= abs(cash_effect)
                self.payment_message = "You paid in cash."
            elif self.game.player.bank_account and self.game.player.bank_account.balance >= abs(cash_effect):
                self.game.player.bank_account.withdraw(abs(cash_effect))
                self.payment_message = "You paid using your bank account."
            elif self.game.player.credit_card and (self.game.player.credit_card.balance + abs(cash_effect)) <= self.game.player.credit_card.limit:
                self.game.player.credit_card.charge(abs(cash_effect))
                self.payment_message = "You paid using your credit card."
            else:
                self.game.player.credit_score -= 15
                self.payment_message = "You couldn't afford this expense! Your credit score has been affected."

        # Continue button
        continue_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 100, 
            200, 60, 
            "Continue", 
            action=lambda: self.game.gui_manager.set_screen(GameScreen(self.game))
        )

        self.buttons = [continue_button]

    def draw(self, surface):
        surface.fill(WHITE)

        # Draw event header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        event_color = GREEN if self.cash_effect > 0 else RED
        pygame.draw.rect(surface, event_color, header_rect)

        header_text = self.title_font.render(f"LIFE EVENT: {self.event['name']}", True, WHITE)
        header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        surface.blit(header_text, header_rect)

        # Draw event description
        desc_text = self.font.render(self.event['description'], True, BLACK)
        desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        surface.blit(desc_text, desc_rect)

        # Draw result
        result_text = self.font.render(self.result_message, True, BLACK)
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        surface.blit(result_text, result_rect)

        # Draw payment message if applicable
        if self.cash_effect < 0:
            payment_text = self.font.render(self.payment_message, True, BLACK)
            payment_rect = payment_text.get_rect(center=(SCREEN_WIDTH // 2, 270))
            surface.blit(payment_text, payment_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

# Placeholder for other screen classes that will be implemented
class BankAccountScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        # Implementation will be added later
        back_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 100, 
            200, 60, 
            "Back", 
            action=lambda: self.game.gui_manager.set_screen(GameScreen(self.game))
        )
        self.buttons = [back_button]

class BankDetailsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont('Arial', FONT_MEDIUM)
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE, bold=True)
        self.small_font = pygame.font.SysFont('Arial', FONT_SMALL)

        # Scrolling for transaction history
        self.scroll_offset = 0
        self.max_visible_transactions = 10

        # Create buttons
        back_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 70, 
            200, 60, 
            "Back", 
            action=lambda: self.game.gui_manager.set_screen(GameScreen(self.game))
        )

        scroll_up_button = Button(
            SCREEN_WIDTH - 100, 
            300, 
            80, 40, 
            "↑", 
            action=self.scroll_up
        )

        scroll_down_button = Button(
            SCREEN_WIDTH - 100, 
            350, 
            80, 40, 
            "↓", 
            action=self.scroll_down
        )

        self.buttons = [back_button, scroll_up_button, scroll_down_button]

    def scroll_up(self):
        if self.scroll_offset > 0:
            self.scroll_offset -= 1

    def scroll_down(self):
        if self.scroll_offset < max(0, len(self.game.player.bank_account.transaction_history) - self.max_visible_transactions):
            self.scroll_offset += 1

    def draw(self, surface):
        surface.fill(WHITE)

        # Draw header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        pygame.draw.rect(surface, LIGHT_BLUE, header_rect)

        header_text = self.title_font.render("BANK ACCOUNT DETAILS", True, WHITE)
        header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        surface.blit(header_text, header_rect)

        # Draw account info
        account_type_text = self.font.render(f"Account Type: {self.game.player.bank_account.account_type}", True, BLACK)
        surface.blit(account_type_text, (50, 100))

        balance_text = self.font.render(f"Current Balance: ${self.game.player.bank_account.balance:.2f}", True, BLACK)
        surface.blit(balance_text, (50, 140))

        if self.game.player.bank_account.account_type == "Savings":
            interest_text = self.font.render(f"Interest Rate: {self.game.player.bank_account.interest_rate * 100:.1f}%", True, BLACK)
            surface.blit(interest_text, (50, 180))

        # Draw transaction history section
        history_title = self.font.render("Transaction History:", True, BLUE)
        surface.blit(history_title, (50, 230))

        # Draw transaction history box
        history_box = pygame.Rect(50, 270, SCREEN_WIDTH - 200, 300)
        pygame.draw.rect(surface, LIGHT_GRAY, history_box)
        pygame.draw.rect(surface, BLACK, history_box, 2)  # Border

        # Draw transactions
        transactions = self.game.player.bank_account.transaction_history

        if not transactions:
            no_transactions_text = self.font.render("No transactions yet.", True, DARK_GRAY)
            no_transactions_rect = no_transactions_text.get_rect(center=(history_box.centerx, history_box.centery))
            surface.blit(no_transactions_text, no_transactions_rect)
        else:
            # Display transactions with scrolling
            visible_transactions = transactions[self.scroll_offset:self.scroll_offset + self.max_visible_transactions]

            for i, transaction in enumerate(visible_transactions):
                y_pos = 280 + i * 30
                transaction_text = self.small_font.render(transaction, True, BLACK)
                surface.blit(transaction_text, (60, y_pos))

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class DepositScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont('Arial', FONT_MEDIUM)
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE, bold=True)
        self.message = ""
        self.message_color = BLACK

        # Create text input for amount
        self.amount_input = TextInput(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2 - 50,
            300, 50,
            initial_text=""
        )

        # Create buttons
        deposit_button = Button(
            SCREEN_WIDTH // 2 - 220, 
            SCREEN_HEIGHT // 2 + 50, 
            200, 60, 
            "Deposit", 
            action=self.make_deposit
        )

        back_button = Button(
            SCREEN_WIDTH // 2 + 20, 
            SCREEN_HEIGHT // 2 + 50, 
            200, 60, 
            "Back", 
            color=GRAY,
            hover_color=LIGHT_GRAY,
            action=lambda: self.game.gui_manager.set_screen(GameScreen(self.game))
        )

        self.buttons = [deposit_button, back_button]

    def make_deposit(self):
        try:
            amount = float(self.amount_input.text)
            if amount <= 0:
                self.message = "Please enter a positive amount."
                self.message_color = RED
            elif amount > self.game.player.cash:
                self.message = "You don't have enough cash for this deposit."
                self.message_color = RED
            else:
                # Process the deposit
                self.game.player.bank_account.deposit(amount)
                self.game.player.cash -= amount
                self.message = f"Successfully deposited ${amount:.2f}."
                self.message_color = GREEN
                self.amount_input.text = ""  # Clear the input
        except ValueError:
            self.message = "Please enter a valid number."
            self.message_color = RED

    def handle_events(self, events):
        # Handle button events
        result = super().handle_events(events)

        # Handle text input
        self.amount_input.update(events)

        return result

    def draw(self, surface):
        surface.fill(WHITE)

        # Draw header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        pygame.draw.rect(surface, LIGHT_BLUE, header_rect)

        header_text = self.title_font.render("DEPOSIT TO BANK ACCOUNT", True, WHITE)
        header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        surface.blit(header_text, header_rect)

        # Draw account info
        account_text = self.font.render(f"Current Balance: ${self.game.player.bank_account.balance:.2f}", True, BLACK)
        account_rect = account_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        surface.blit(account_text, account_rect)

        cash_text = self.font.render(f"Available Cash: ${self.game.player.cash:.2f}", True, BLACK)
        cash_rect = cash_text.get_rect(center=(SCREEN_WIDTH // 2, 160))
        surface.blit(cash_text, cash_rect)

        # Draw prompt
        prompt_text = self.font.render("Enter amount to deposit:", True, BLACK)
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        surface.blit(prompt_text, prompt_rect)

        # Draw text input
        self.amount_input.draw(surface)

        # Draw message if any
        if self.message:
            message_text = self.font.render(self.message, True, self.message_color)
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
            surface.blit(message_text, message_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class WithdrawScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont('Arial', FONT_MEDIUM)
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE, bold=True)
        self.message = ""
        self.message_color = BLACK

        # Create text input for amount
        self.amount_input = TextInput(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2 - 50,
            300, 50,
            initial_text=""
        )

        # Create buttons
        withdraw_button = Button(
            SCREEN_WIDTH // 2 - 220, 
            SCREEN_HEIGHT // 2 + 50, 
            200, 60, 
            "Withdraw", 
            action=self.make_withdrawal
        )

        back_button = Button(
            SCREEN_WIDTH // 2 + 20, 
            SCREEN_HEIGHT // 2 + 50, 
            200, 60, 
            "Back", 
            color=GRAY,
            hover_color=LIGHT_GRAY,
            action=lambda: self.game.gui_manager.set_screen(GameScreen(self.game))
        )

        self.buttons = [withdraw_button, back_button]

    def make_withdrawal(self):
        try:
            amount = float(self.amount_input.text)
            if amount <= 0:
                self.message = "Please enter a positive amount."
                self.message_color = RED
            elif amount > self.game.player.bank_account.balance:
                self.message = "You don't have enough funds in your account."
                self.message_color = RED
            else:
                # Process the withdrawal
                success = self.game.player.bank_account.withdraw(amount)
                if success:
                    self.game.player.cash += amount
                    self.message = f"Successfully withdrew ${amount:.2f}."
                    self.message_color = GREEN
                    self.amount_input.text = ""  # Clear the input
                else:
                    self.message = "Withdrawal failed. Please try again."
                    self.message_color = RED
        except ValueError:
            self.message = "Please enter a valid number."
            self.message_color = RED

    def handle_events(self, events):
        # Handle button events
        result = super().handle_events(events)

        # Handle text input
        self.amount_input.update(events)

        return result

    def draw(self, surface):
        surface.fill(WHITE)

        # Draw header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        pygame.draw.rect(surface, LIGHT_BLUE, header_rect)

        header_text = self.title_font.render("WITHDRAW FROM BANK ACCOUNT", True, WHITE)
        header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        surface.blit(header_text, header_rect)

        # Draw account info
        account_text = self.font.render(f"Current Balance: ${self.game.player.bank_account.balance:.2f}", True, BLACK)
        account_rect = account_text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        surface.blit(account_text, account_rect)

        cash_text = self.font.render(f"Current Cash: ${self.game.player.cash:.2f}", True, BLACK)
        cash_rect = cash_text.get_rect(center=(SCREEN_WIDTH // 2, 160))
        surface.blit(cash_text, cash_rect)

        # Draw prompt
        prompt_text = self.font.render("Enter amount to withdraw:", True, BLACK)
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        surface.blit(prompt_text, prompt_rect)

        # Draw text input
        self.amount_input.draw(surface)

        # Draw message if any
        if self.message:
            message_text = self.font.render(self.message, True, self.message_color)
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
            surface.blit(message_text, message_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class GetDebitCardScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        # Implementation will be added later
        back_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 100, 
            200, 60, 
            "Back", 
            action=lambda: self.game.gui_manager.set_screen(GameScreen(self.game))
        )
        self.buttons = [back_button]

class CreditCardScreen(Screen):
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
            200, 60, 
            "Back", 
            action=lambda: self.game.gui_manager.set_screen(GameScreen(self.game))
        )

        self.buttons = [back_button]

        # Check eligibility and create apply button if eligible
        self.check_eligibility()

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
                200, 60,
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
            200, 60,
            "View Card Details",
            action=lambda: self.game.gui_manager.set_screen(CreditCardDetailsScreen(self.game))
        )

        self.buttons.append(details_button)

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
        if self.message:
            # Split message into multiple lines if it's too long
            words = self.message.split()
            lines = []
            current_line = []

            for word in words:
                current_line.append(word)
                test_line = " ".join(current_line)
                if self.font.size(test_line)[0] > SCREEN_WIDTH - 100:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [word]

            if current_line:
                lines.append(" ".join(current_line))

            for i, line in enumerate(lines):
                message_text = self.font.render(line, True, self.message_color)
                message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 30))
                surface.blit(message_text, message_rect)

        # Draw credit card image if approved
        if self.approved:
            card_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 180)
            pygame.draw.rect(surface, PURPLE, card_rect, border_radius=10)
            pygame.draw.rect(surface, BLACK, card_rect, 2, border_radius=10)

            # Card details
            card_title = self.small_font.render("MONEY SMARTZ CREDIT CARD", True, WHITE)
            surface.blit(card_title, (card_rect.left + 20, card_rect.top + 20))

            card_number = self.small_font.render("**** **** **** 1234", True, WHITE)
            surface.blit(card_number, (card_rect.left + 20, card_rect.top + 60))

            card_name = self.small_font.render(self.game.player.name.upper(), True, WHITE)
            surface.blit(card_name, (card_rect.left + 20, card_rect.top + 100))

            card_limit = self.small_font.render(f"LIMIT: ${self.credit_limit:.2f}", True, WHITE)
            surface.blit(card_limit, (card_rect.left + 20, card_rect.top + 140))

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class CreditCardDetailsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont('Arial', FONT_MEDIUM)
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE, bold=True)
        self.small_font = pygame.font.SysFont('Arial', FONT_SMALL)

        # Scrolling for transaction history
        self.scroll_offset = 0
        self.max_visible_transactions = 8

        # Create buttons
        back_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 70, 
            200, 60, 
            "Back", 
            action=lambda: self.game.gui_manager.set_screen(GameScreen(self.game))
        )

        make_payment_button = Button(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT - 150,
            200, 60,
            "Make a Payment",
            action=lambda: self.game.gui_manager.set_screen(PayCreditCardScreen(self.game))
        )

        scroll_up_button = Button(
            SCREEN_WIDTH - 100, 
            350, 
            80, 40, 
            "↑", 
            action=self.scroll_up
        )

        scroll_down_button = Button(
            SCREEN_WIDTH - 100, 
            400, 
            80, 40, 
            "↓", 
            action=self.scroll_down
        )

        self.buttons = [back_button, make_payment_button, scroll_up_button, scroll_down_button]

    def scroll_up(self):
        if self.scroll_offset > 0:
            self.scroll_offset -= 1

    def scroll_down(self):
        if self.scroll_offset < max(0, len(self.game.player.credit_card.transaction_history) - self.max_visible_transactions):
            self.scroll_offset += 1

    def draw(self, surface):
        surface.fill(WHITE)

        # Draw header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        pygame.draw.rect(surface, PURPLE, header_rect)

        header_text = self.title_font.render("CREDIT CARD DETAILS", True, WHITE)
        header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        surface.blit(header_text, header_rect)

        # Draw credit card image
        card_rect = pygame.Rect(50, 100, 300, 180)
        pygame.draw.rect(surface, PURPLE, card_rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, card_rect, 2, border_radius=10)

        # Card details
        card_title = self.small_font.render("MONEY SMARTZ CREDIT CARD", True, WHITE)
        surface.blit(card_title, (card_rect.left + 20, card_rect.top + 20))

        card_number = self.small_font.render("**** **** **** 1234", True, WHITE)
        surface.blit(card_number, (card_rect.left + 20, card_rect.top + 60))

        card_name = self.small_font.render(self.game.player.name.upper(), True, WHITE)
        surface.blit(card_name, (card_rect.left + 20, card_rect.top + 100))

        card_limit = self.small_font.render(f"LIMIT: ${self.game.player.credit_card.limit:.2f}", True, WHITE)
        surface.blit(card_limit, (card_rect.left + 20, card_rect.top + 140))

        # Draw account info
        info_x = 400
        info_y = 120

        limit_text = self.font.render(f"Credit Limit: ${self.game.player.credit_card.limit:.2f}", True, BLACK)
        surface.blit(limit_text, (info_x, info_y))

        balance_text = self.font.render(f"Current Balance: ${self.game.player.credit_card.balance:.2f}", True, BLACK)
        surface.blit(balance_text, (info_x, info_y + 40))

        available_text = self.font.render(f"Available Credit: ${self.game.player.credit_card.limit - self.game.player.credit_card.balance:.2f}", True, BLACK)
        surface.blit(available_text, (info_x, info_y + 80))

        if self.game.player.credit_card.balance > 0:
            min_payment = max(25, self.game.player.credit_card.balance * 0.03)
            payment_text = self.font.render(f"Minimum Payment: ${min_payment:.2f}", True, RED)
            surface.blit(payment_text, (info_x, info_y + 120))

        # Draw transaction history section
        history_title = self.font.render("Transaction History:", True, BLUE)
        surface.blit(history_title, (50, 320))

        # Draw transaction history box
        history_box = pygame.Rect(50, 350, SCREEN_WIDTH - 200, 250)
        pygame.draw.rect(surface, LIGHT_GRAY, history_box)
        pygame.draw.rect(surface, BLACK, history_box, 2)  # Border

        # Draw transactions
        transactions = self.game.player.credit_card.transaction_history

        if not transactions:
            no_transactions_text = self.font.render("No transactions yet.", True, DARK_GRAY)
            no_transactions_rect = no_transactions_text.get_rect(center=(history_box.centerx, history_box.centery))
            surface.blit(no_transactions_text, no_transactions_rect)
        else:
            # Display transactions with scrolling
            visible_transactions = transactions[self.scroll_offset:self.scroll_offset + self.max_visible_transactions]

            for i, transaction in enumerate(visible_transactions):
                y_pos = 360 + i * 30
                transaction_text = self.small_font.render(transaction, True, BLACK)
                surface.blit(transaction_text, (60, y_pos))

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class PayCreditCardScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont('Arial', FONT_MEDIUM)
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE, bold=True)
        self.small_font = pygame.font.SysFont('Arial', FONT_SMALL)
        self.message = ""
        self.message_color = BLACK

        # Calculate minimum payment
        self.min_payment = max(25, self.game.player.credit_card.balance * 0.03)

        # Create text input for custom payment amount
        self.amount_input = TextInput(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2 + 50,
            300, 50,
            initial_text=""
        )

        # Create back button
        back_button = Button(
            SCREEN_WIDTH // 2 - 220, 
            SCREEN_HEIGHT - 70, 
            200, 60, 
            "Back", 
            color=GRAY,
            hover_color=LIGHT_GRAY,
            action=lambda: self.game.gui_manager.set_screen(CreditCardDetailsScreen(self.game))
        )

        # Create payment buttons
        min_payment_button = Button(
            SCREEN_WIDTH // 2 - 220,
            SCREEN_HEIGHT // 2 - 50,
            200, 60,
            f"Pay Minimum (${self.min_payment:.2f})",
            color=BLUE,
            hover_color=LIGHT_BLUE,
            action=lambda: self.make_payment(self.min_payment)
        )

        full_payment_button = Button(
            SCREEN_WIDTH // 2 + 20,
            SCREEN_HEIGHT // 2 - 50,
            200, 60,
            f"Pay Full (${self.game.player.credit_card.balance:.2f})",
            color=GREEN,
            hover_color=LIGHT_GREEN,
            action=lambda: self.make_payment(self.game.player.credit_card.balance)
        )

        custom_payment_button = Button(
            SCREEN_WIDTH // 2 + 20,
            SCREEN_HEIGHT // 2 + 50,
            200, 60,
            "Pay Custom Amount",
            action=self.make_custom_payment
        )

        self.buttons = [back_button, min_payment_button, full_payment_button, custom_payment_button]

    def make_payment(self, amount):
        # Check if player has enough cash
        if self.game.player.cash >= amount:
            self.game.player.cash -= amount
            self.game.player.credit_card.pay(amount)
            self.message = f"Payment of ${amount:.2f} made successfully from cash."
            self.message_color = GREEN
        # Check if player has enough in bank account
        elif self.game.player.bank_account and self.game.player.bank_account.balance >= amount:
            self.game.player.bank_account.withdraw(amount)
            self.game.player.credit_card.pay(amount)
            self.message = f"Payment of ${amount:.2f} made successfully from bank account."
            self.message_color = GREEN
        else:
            self.message = "Insufficient funds for this payment. Please try a smaller amount."
            self.message_color = RED

    def make_custom_payment(self):
        try:
            amount = float(self.amount_input.text)
            if amount <= 0:
                self.message = "Please enter a positive amount."
                self.message_color = RED
            elif amount < self.min_payment:
                self.message = f"Payment must be at least the minimum payment of ${self.min_payment:.2f}."
                self.message_color = RED
            elif amount > self.game.player.credit_card.balance:
                self.message = f"Payment cannot exceed the current balance of ${self.game.player.credit_card.balance:.2f}."
                self.message_color = RED
            else:
                self.make_payment(amount)
        except ValueError:
            self.message = "Please enter a valid number."
            self.message_color = RED

    def handle_events(self, events):
        # Handle button events
        result = super().handle_events(events)

        # Handle text input
        self.amount_input.update(events)

        return result

    def draw(self, surface):
        surface.fill(WHITE)

        # Draw header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        pygame.draw.rect(surface, PURPLE, header_rect)

        header_text = self.title_font.render("MAKE CREDIT CARD PAYMENT", True, WHITE)
        header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        surface.blit(header_text, header_rect)

        # Draw account info
        info_y = 100
        balance_text = self.font.render(f"Current Balance: ${self.game.player.credit_card.balance:.2f}", True, BLACK)
        min_payment_text = self.font.render(f"Minimum Payment: ${self.min_payment:.2f}", True, BLACK)
        cash_text = self.font.render(f"Available Cash: ${self.game.player.cash:.2f}", True, BLACK)

        balance_rect = balance_text.get_rect(center=(SCREEN_WIDTH // 2, info_y))
        min_payment_rect = min_payment_text.get_rect(center=(SCREEN_WIDTH // 2, info_y + 40))
        cash_rect = cash_text.get_rect(center=(SCREEN_WIDTH // 2, info_y + 80))

        surface.blit(balance_text, balance_rect)
        surface.blit(min_payment_text, min_payment_rect)
        surface.blit(cash_text, cash_rect)

        if self.game.player.bank_account:
            bank_text = self.font.render(f"Bank Account Balance: ${self.game.player.bank_account.balance:.2f}", True, BLACK)
            bank_rect = bank_text.get_rect(center=(SCREEN_WIDTH // 2, info_y + 120))
            surface.blit(bank_text, bank_rect)

        # Draw payment options title
        options_text = self.font.render("Payment Options:", True, BLUE)
        options_rect = options_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        surface.blit(options_text, options_rect)

        # Draw custom payment input label
        custom_text = self.font.render("Custom Payment Amount:", True, BLACK)
        custom_rect = custom_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        surface.blit(custom_text, custom_rect)

        # Draw text input
        self.amount_input.draw(surface)

        # Draw message if any
        if self.message:
            message_text = self.font.render(self.message, True, self.message_color)
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150))
            surface.blit(message_text, message_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class LoanDetailsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        # Implementation will be added later
        back_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 100, 
            200, 60, 
            "Back", 
            action=lambda: self.game.gui_manager.set_screen(GameScreen(self.game))
        )
        self.buttons = [back_button]

class ExtraLoanPaymentScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        # Implementation will be added later
        back_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 100, 
            200, 60, 
            "Back", 
            action=lambda: self.game.gui_manager.set_screen(GameScreen(self.game))
        )
        self.buttons = [back_button]

class AssetDetailsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        # Implementation will be added later
        back_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 100, 
            200, 60, 
            "Back", 
            action=lambda: self.game.gui_manager.set_screen(GameScreen(self.game))
        )
        self.buttons = [back_button]

class JobSearchScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont('Arial', FONT_MEDIUM)
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE, bold=True)
        self.small_font = pygame.font.SysFont('Arial', FONT_SMALL)
        self.job_options = []
        self.message = ""
        self.message_color = BLACK

        # Generate job opportunities
        self.generate_job_options()

        # Create back button
        back_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 70, 
            200, 60, 
            "Back", 
            action=lambda: self.game.gui_manager.set_screen(GameScreen(self.game))
        )

        self.buttons = [back_button]

        # Create job option buttons if player is eligible
        if self.game.player.age >= 18:
            self.create_job_buttons()

    def generate_job_options(self):
        # Clear previous options
        self.job_options = []

        # Check if player is too young
        if self.game.player.age < 18:
            self.message = "You're too young to work full-time. Wait until you're 18."
            self.message_color = RED
            return

        # Base salary multiplier based on education
        salary_multiplier = 1.0
        if self.game.player.education == "College Graduate":
            salary_multiplier = 1.5
        elif self.game.player.education == "Associate's Degree":
            salary_multiplier = 1.2
        elif self.game.player.education == "Trade School Graduate":
            salary_multiplier = 1.3

        # Add experience multiplier (1% per year over 22)
        experience_years = max(0, self.game.player.age - 22)
        experience_multiplier = 1.0 + (experience_years * 0.01)

        # Generate 3 random job opportunities
        for i in range(3):
            # Job quality varies (some better, some worse)
            job_quality = random.uniform(0.8, 1.3)

            if self.game.player.education == "College Graduate":
                job_title = random.choice([
                    "Senior Professional", "Department Manager", "Project Lead",
                    "Consultant", "Specialist", "Team Lead"
                ])
                base_salary = random.randint(50000, 80000)
            elif self.game.player.education == "Associate's Degree":
                job_title = random.choice([
                    "Technical Lead", "Office Manager", "Sales Manager",
                    "Assistant Director", "Coordinator", "Supervisor"
                ])
                base_salary = random.randint(40000, 60000)
            elif self.game.player.education == "Trade School Graduate":
                job_title = random.choice([
                    "Master Tradesperson", "Shop Foreman", "Lead Technician",
                    "Service Manager", "Contractor", "Specialist"
                ])
                base_salary = random.randint(45000, 65000)
            else:  # High school only
                job_title = random.choice([
                    "Shift Supervisor", "Team Lead", "Assistant Manager",
                    "Sales Representative", "Office Assistant", "Customer Service Manager"
                ])
                base_salary = random.randint(30000, 45000)

            # Calculate final salary with all multipliers
            final_salary = int(base_salary * salary_multiplier * experience_multiplier * job_quality)

            # Only add jobs that are better than current (or if unemployed)
            if not self.game.player.job or final_salary > self.game.player.salary:
                self.job_options.append({"title": job_title, "salary": final_salary})

        # Add option to stay at current job
        if self.game.player.job:
            self.job_options.append({"title": self.game.player.job, "salary": self.game.player.salary, "current": True})

        # No better jobs found
        if len(self.job_options) == 0 or (len(self.job_options) == 1 and self.game.player.job):
            self.message = "Unfortunately, you couldn't find any better job opportunities at this time. Try again later or improve your qualifications."
            self.message_color = ORANGE

    def create_job_buttons(self):
        # Create buttons for each job option
        button_y = 200
        button_height = 60
        button_spacing = 20

        for i, job in enumerate(self.job_options):
            if job.get("current"):
                button_text = f"Stay at current job: {job['title']} - ${job['salary']}/year"
                button_color = GRAY
                hover_color = LIGHT_GRAY
            else:
                button_text = f"{job['title']} - ${job['salary']}/year"
                button_color = GREEN
                hover_color = LIGHT_GREEN

            job_button = Button(
                SCREEN_WIDTH // 2 - 250,
                button_y + (i * (button_height + button_spacing)),
                500, button_height,
                button_text,
                color=button_color,
                hover_color=hover_color,
                action=lambda j=job: self.select_job(j)
            )

            self.buttons.append(job_button)

    def select_job(self, job):
        if job.get("current"):
            self.message = "You've decided to stay at your current job."
            self.message_color = BLUE
        else:
            # Update player's job and salary
            self.game.player.job = job["title"]
            self.game.player.salary = job["salary"]

            self.message = f"Congratulations! You've been hired as a {job['title']} with an annual salary of ${job['salary']}."
            self.message_color = GREEN

            # Refresh the buttons to show the updated job
            self.buttons = [self.buttons[0]]  # Keep only the back button
            self.generate_job_options()
            self.create_job_buttons()

    def draw(self, surface):
        surface.fill(WHITE)

        # Draw header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        pygame.draw.rect(surface, BLUE, header_rect)

        header_text = self.title_font.render("JOB SEARCH", True, WHITE)
        header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        surface.blit(header_text, header_rect)

        # Draw current job info if any
        info_y = 100
        if self.game.player.job:
            current_job_text = self.font.render(f"Current Job: {self.game.player.job}", True, BLACK)
            current_salary_text = self.font.render(f"Current Salary: ${self.game.player.salary}/year", True, BLACK)

            surface.blit(current_job_text, (50, info_y))
            surface.blit(current_salary_text, (50, info_y + 30))
        else:
            no_job_text = self.font.render("You are currently unemployed.", True, BLACK)
            surface.blit(no_job_text, (50, info_y))

        # Draw message if any
        if self.message:
            message_text = self.font.render(self.message, True, self.message_color)
            message_rect = message_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
            surface.blit(message_text, message_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

class HousingScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        # Implementation will be added later
        back_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 100, 
            200, 60, 
            "Back", 
            action=lambda: self.game.gui_manager.set_screen(GameScreen(self.game))
        )
        self.buttons = [back_button]

class FamilyPlanningScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        # Implementation will be added later
        back_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 100, 
            200, 60, 
            "Back", 
            action=lambda: self.game.gui_manager.set_screen(GameScreen(self.game))
        )
        self.buttons = [back_button]

class EndGameScreen(Screen):
    def __init__(self, game, reason):
        super().__init__(game)
        self.reason = reason
        self.font = pygame.font.SysFont('Arial', FONT_MEDIUM)
        self.title_font = pygame.font.SysFont('Arial', FONT_LARGE, bold=True)

        # Calculate net worth
        self.cash = self.game.player.cash
        self.bank_balance = self.game.player.bank_account.balance if self.game.player.bank_account else 0
        self.credit_card_debt = self.game.player.credit_card.balance if self.game.player.credit_card else 0

        self.loan_debt = 0
        for loan in self.game.player.loans:
            self.loan_debt += loan.current_balance

        self.asset_value = 0
        for asset in self.game.player.assets:
            self.asset_value += asset.current_value

        self.net_worth = self.cash + self.bank_balance - self.credit_card_debt - self.loan_debt + self.asset_value

        # Financial rating
        if self.net_worth >= 1000000:
            self.rating = "Financial Wizard"
        elif self.net_worth >= 500000:
            self.rating = "Financially Secure"
        elif self.net_worth >= 100000:
            self.rating = "Financially Stable"
        elif self.net_worth >= 0:
            self.rating = "Breaking Even"
        else:
            self.rating = "In Debt"

        # Create buttons
        quit_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 100, 
            200, 60, 
            "Quit Game", 
            color=RED,
            hover_color=LIGHT_RED,
            action=lambda: setattr(self.game.gui_manager, 'running', False)
        )

        new_game_button = Button(
            SCREEN_WIDTH // 2 - 100, 
            SCREEN_HEIGHT - 180, 
            200, 60, 
            "New Game", 
            action=lambda: self.game.gui_manager.set_screen(TitleScreen(self.game))
        )

        self.buttons = [new_game_button, quit_button]

    def draw(self, surface):
        surface.fill(WHITE)

        # Draw header
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 80)
        pygame.draw.rect(surface, GREEN, header_rect)

        if self.reason == "retirement":
            header_text = self.title_font.render("CONGRATULATIONS ON YOUR RETIREMENT!", True, WHITE)
        else:
            header_text = self.title_font.render("GAME OVER", True, WHITE)

        header_rect = header_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        surface.blit(header_text, header_rect)

        # Draw financial summary
        summary_y = 100
        self.draw_text(surface, "FINAL FINANCIAL SUMMARY", SCREEN_WIDTH // 2, summary_y, center=True, is_title=True)

        summary_y += 50
        self.draw_text(surface, f"Cash: ${self.cash:.2f}", SCREEN_WIDTH // 2 - 200, summary_y)
        self.draw_text(surface, f"Bank Balance: ${self.bank_balance:.2f}", SCREEN_WIDTH // 2 - 200, summary_y + 30)
        self.draw_text(surface, f"Credit Card Debt: ${self.credit_card_debt:.2f}", SCREEN_WIDTH // 2 - 200, summary_y + 60)
        self.draw_text(surface, f"Loan Debt: ${self.loan_debt:.2f}", SCREEN_WIDTH // 2 - 200, summary_y + 90)
        self.draw_text(surface, f"Asset Value: ${self.asset_value:.2f}", SCREEN_WIDTH // 2 - 200, summary_y + 120)

        # Net worth with larger font
        net_worth_font = pygame.font.SysFont('Arial', FONT_LARGE, bold=True)
        net_worth_text = net_worth_font.render(f"Net Worth: ${self.net_worth:.2f}", True, BLUE)
        net_worth_rect = net_worth_text.get_rect(center=(SCREEN_WIDTH // 2, summary_y + 180))
        surface.blit(net_worth_text, net_worth_rect)

        # Financial rating
        rating_text = self.title_font.render(f"Financial Rating: {self.rating}", True, PURPLE)
        rating_rect = rating_text.get_rect(center=(SCREEN_WIDTH // 2, summary_y + 240))
        surface.blit(rating_text, rating_rect)

        # Thank you message
        thank_you_text = self.font.render("Thank you for playing MONEY SMARTZ!", True, BLACK)
        thank_you_rect = thank_you_text.get_rect(center=(SCREEN_WIDTH // 2, summary_y + 300))
        surface.blit(thank_you_text, thank_you_rect)

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

    def draw_text(self, surface, text, x, y, center=False, is_title=False):
        font = self.title_font if is_title else self.font
        text_surface = font.render(text, True, BLACK)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
            surface.blit(text_surface, text_rect)
        else:
            surface.blit(text_surface, (x, y))

class Player:
    def __init__(self, name):
        self.name = name
        self.age = 16
        self.education = "High School"
        self.job = None
        self.salary = 0
        self.cash = 50  # Starting cash
        self.bank_account = None
        self.credit_card = None
        self.debit_card = None
        self.credit_score = 650  # Starting credit score
        self.assets = []  # Cars, houses, etc.
        self.loans = []  # Student loans, mortgages, etc.
        self.family = []  # Spouse, children
        self.life_events = []  # History of major life events

class BankAccount:
    def __init__(self, account_type="Checking"):
        self.account_type = account_type
        self.balance = 0
        self.interest_rate = 0.01 if account_type == "Savings" else 0.0
        self.transaction_history = []

    def deposit(self, amount):
        self.balance += amount
        self.transaction_history.append(f"Deposit: ${amount}")
        return True

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            self.transaction_history.append(f"Withdrawal: ${amount}")
            return True
        return False

    def apply_interest(self):
        if self.account_type == "Savings":
            interest = self.balance * self.interest_rate
            self.balance += interest
            self.transaction_history.append(f"Interest: ${interest:.2f}")

class Card:
    def __init__(self, card_type, limit=0):
        self.card_type = card_type
        self.limit = limit
        self.balance = 0
        self.transaction_history = []

    def charge(self, amount):
        if self.card_type == "Credit":
            if self.balance + amount <= self.limit:
                self.balance += amount
                self.transaction_history.append(f"Charge: ${amount}")
                return True
            return False
        else:  # Debit card
            # Debit card is linked to bank account, handled elsewhere
            self.transaction_history.append(f"Charge: ${amount}")
            return True

    def pay(self, amount):
        if self.card_type == "Credit":
            if amount <= self.balance:
                self.balance -= amount
                self.transaction_history.append(f"Payment: ${amount}")
                return True
            return False
        return True  # No action needed for debit card

class Loan:
    def __init__(self, loan_type, amount, interest_rate, term_years):
        self.loan_type = loan_type
        self.original_amount = amount
        self.current_balance = amount
        self.interest_rate = interest_rate
        self.term_years = term_years
        self.monthly_payment = self.calculate_payment()
        self.payment_history = []

    def calculate_payment(self):
        # Simple monthly payment calculation
        monthly_rate = self.interest_rate / 12
        num_payments = self.term_years * 12
        return (self.original_amount * monthly_rate) / (1 - (1 + monthly_rate) ** -num_payments)

    def make_payment(self, amount):
        if amount >= self.monthly_payment:
            self.current_balance -= (amount - (self.monthly_payment * self.interest_rate / 12))
            self.payment_history.append(f"Payment: ${amount}")
            return True
        return False

class Asset:
    def __init__(self, asset_type, name, value, condition="Good"):
        self.asset_type = asset_type  # Car, House, etc.
        self.name = name
        self.purchase_value = value
        self.current_value = value
        self.condition = condition
        self.age = 0

    def age_asset(self):
        self.age += 1
        # Depreciate value based on type and age
        if self.asset_type == "Car":
            self.current_value *= 0.85  # 15% depreciation per year
        elif self.asset_type == "House":
            # Houses might appreciate
            appreciation = random.uniform(-0.05, 0.1)  # -5% to +10%
            self.current_value *= (1 + appreciation)

    def repair(self, cost):
        self.condition = "Good"
        return cost

class Game:
    def __init__(self):
        self.player = None
        self.current_month = 1
        self.current_year = 0
        self.game_over = False
        self.events = self.initialize_events()
        self.gui_manager = GUIManager(self)

    def initialize_events(self):
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
        # Process income
        if self.player.job:
            monthly_income = self.player.salary / 12
            self.player.cash += monthly_income

            # Auto deposit to bank if account exists
            if self.player.bank_account:
                self.player.bank_account.deposit(monthly_income * 0.8)  # 80% of income goes to bank
                self.player.cash -= monthly_income * 0.8

        # Process loan payments
        for loan in self.player.loans:
            if self.player.cash >= loan.monthly_payment:
                self.player.cash -= loan.monthly_payment
                loan.make_payment(loan.monthly_payment)
            elif self.player.bank_account and self.player.bank_account.balance >= loan.monthly_payment:
                self.player.bank_account.withdraw(loan.monthly_payment)
                loan.make_payment(loan.monthly_payment)
            else:
                # Missed payment - credit score impact
                self.player.credit_score -= 20
                print(f"You missed a payment on your {loan.loan_type}. Your credit score has decreased.")

        # Process credit card payments (minimum payment)
        if self.player.credit_card and self.player.credit_card.balance > 0:
            min_payment = max(25, self.player.credit_card.balance * 0.03)  # 3% or $25, whichever is higher

            if self.player.cash >= min_payment:
                self.player.cash -= min_payment
                self.player.credit_card.pay(min_payment)
            elif self.player.bank_account and self.player.bank_account.balance >= min_payment:
                self.player.bank_account.withdraw(min_payment)
                self.player.credit_card.pay(min_payment)
            else:
                # Missed payment - credit score impact
                self.player.credit_score -= 30
                print("You missed your credit card payment. Your credit score has decreased significantly.")

    def trigger_random_event(self):
        # Decide if it's a positive or negative event
        event_type = "positive" if random.random() < 0.5 else "negative"
        event = random.choice(self.events[event_type])

        cash_effect = event["cash_effect"]()

        # Only show events that have an effect
        if cash_effect != 0:
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
        self.clear_screen()
        print("\n" + "=" * 60)
        print("LIFE EVENT: HIGH SCHOOL GRADUATION")
        print("=" * 60)
        print("\nCongratulations! You've graduated from high school.")
        print("It's time to make some important decisions about your future.")

        choices = ["Go to college (costs $20,000/year for 4 years)",
                  "Community college (costs $5,000/year for 2 years)",
                  "Trade school (costs $10,000 for 1 year)",
                  "Start working full-time"]

        choice = self.get_choice("What would you like to do?", choices)

        if choice == choices[0]:  # 4-year college
            # Check if player can afford or needs loans
            total_cost = 80000
            if self.player.bank_account and self.player.bank_account.balance >= 20000:
                self.player.bank_account.withdraw(20000)  # First year tuition
                print("\nYou paid your first year's tuition from your savings.")
                loan_amount = 60000  # Remaining 3 years
            else:
                loan_amount = total_cost

            # Create student loan
            student_loan = Loan("Student Loan", loan_amount, 0.05, 10)  # 5% interest, 10 year term
            self.player.loans.append(student_loan)

            self.player.education = "College (In Progress)"
            print(f"\nYou've enrolled in a 4-year college program!")
            print(f"You've taken out a student loan of ${loan_amount} at 5% interest.")

        elif choice == choices[1]:  # Community college
            total_cost = 10000
            if self.player.bank_account and self.player.bank_account.balance >= 5000:
                self.player.bank_account.withdraw(5000)  # First year tuition
                print("\nYou paid your first year's tuition from your savings.")
                loan_amount = 5000  # Second year
            else:
                loan_amount = total_cost

            # Create student loan
            student_loan = Loan("Student Loan", loan_amount, 0.04, 5)  # 4% interest, 5 year term
            self.player.loans.append(student_loan)

            self.player.education = "Community College (In Progress)"
            print(f"\nYou've enrolled in a community college program!")
            print(f"You've taken out a student loan of ${loan_amount} at 4% interest.")

        elif choice == choices[2]:  # Trade school
            if self.player.bank_account and self.player.bank_account.balance >= 10000:
                self.player.bank_account.withdraw(10000)
                print("\nYou paid your trade school tuition from your savings.")
            else:
                # Create student loan
                student_loan = Loan("Student Loan", 10000, 0.04, 5)  # 4% interest, 5 year term
                self.player.loans.append(student_loan)
                print(f"\nYou've taken out a student loan of $10,000 at 4% interest.")

            self.player.education = "Trade School (In Progress)"
            print("\nYou've enrolled in a trade school program!")

        else:  # Start working
            self.player.education = "High School Graduate"
            self.player.job = "Entry Level Worker"
            self.player.salary = 25000
            print("\nYou've decided to start working full-time.")
            print(f"You found a job as an {self.player.job} with a salary of ${self.player.salary}/year.")

        input("\nPress Enter to continue your journey...")

    def college_graduation_event(self):
        self.clear_screen()
        print("\n" + "=" * 60)
        print("LIFE EVENT: COLLEGE GRADUATION")
        print("=" * 60)
        print("\nCongratulations! You've graduated from college.")

        # Update education status
        if self.player.education == "College (In Progress)":
            self.player.education = "College Graduate"
            self.player.job = "College Graduate"
            self.player.salary = random.randint(40000, 60000)
        elif self.player.education == "Community College (In Progress)":
            self.player.education = "Associate's Degree"
            self.player.job = "Associate's Degree Holder"
            self.player.salary = random.randint(35000, 45000)
        elif self.player.education == "Trade School (In Progress)":
            self.player.education = "Trade School Graduate"
            self.player.job = "Skilled Tradesperson"
            self.player.salary = random.randint(40000, 55000)

        print(f"\nYou've found a job as a {self.player.job} with a salary of ${self.player.salary}/year.")

        # Credit card offer
        if not self.player.credit_card:
            print("\nNow that you have a steady income, you've received a credit card offer.")
            choice = self.get_choice("Would you like to apply for a credit card?", ["Yes", "No"])

            if choice == "Yes":
                limit = min(self.player.salary * 0.2, 5000)  # 20% of salary or $5000, whichever is lower
                self.player.credit_card = Card("Credit", limit)
                print(f"\nCongratulations! You've been approved for a credit card with a ${int(limit)} limit.")
                print("Use it wisely to build your credit score!")

        input("\nPress Enter to continue your journey...")

    def job_opportunity_event(self):
        self.clear_screen()
        print("\n" + "=" * 60)
        print("LIFE EVENT: JOB OPPORTUNITY")
        print("=" * 60)

        # Job options based on education
        job_options = []
        if self.player.education == "College Graduate":
            job_options = [
                {"title": "Entry-Level Professional", "salary": random.randint(45000, 60000)},
                {"title": "Management Trainee", "salary": random.randint(50000, 65000)},
                {"title": "Research Assistant", "salary": random.randint(40000, 55000)}
            ]
        elif self.player.education == "Associate's Degree":
            job_options = [
                {"title": "Technical Specialist", "salary": random.randint(35000, 50000)},
                {"title": "Administrative Assistant", "salary": random.randint(30000, 45000)},
                {"title": "Sales Representative", "salary": random.randint(35000, 55000)}
            ]
        elif self.player.education == "Trade School Graduate":
            job_options = [
                {"title": "Electrician", "salary": random.randint(40000, 60000)},
                {"title": "Plumber", "salary": random.randint(45000, 65000)},
                {"title": "Mechanic", "salary": random.randint(35000, 55000)}
            ]
        else:  # High school only
            job_options = [
                {"title": "Retail Associate", "salary": random.randint(25000, 35000)},
                {"title": "Customer Service Rep", "salary": random.randint(28000, 38000)},
                {"title": "Delivery Driver", "salary": random.randint(30000, 40000)}
            ]

        print("\nYou've received several job offers!")

        choices = []
        for i, job in enumerate(job_options):
            choices.append(f"{job['title']} - ${job['salary']}/year")

        choice_index = choices.index(self.get_choice("Which job would you like to accept?", choices))
        selected_job = job_options[choice_index]

        self.player.job = selected_job["title"]
        self.player.salary = selected_job["salary"]

        print(f"\nCongratulations! You are now a {self.player.job} earning ${self.player.salary}/year.")

        input("\nPress Enter to continue your journey...")

    def car_purchase_opportunity(self):
        self.clear_screen()
        print("\n" + "=" * 60)
        print("LIFE EVENT: TRANSPORTATION NEEDS")
        print("=" * 60)
        print("\nYou need reliable transportation for work or school.")

        car_options = [
            {"name": "Used Economy Car", "value": 5000, "condition": "Fair"},
            {"name": "Used Midsize Car", "value": 10000, "condition": "Good"},
            {"name": "New Economy Car", "value": 20000, "condition": "Excellent"}
        ]

        choices = [f"{car['name']} - ${car['value']} ({car['condition']} condition)" for car in car_options]
        choices.append("Public Transportation - $0")

        choice = self.get_choice("What transportation option would you like to choose?", choices)

        if choice != choices[-1]:  # If not public transportation
            car_index = choices.index(choice)
            selected_car = car_options[car_index]

            # Payment options
            payment_choices = []

            # Cash option if they have enough money
            if self.player.cash >= selected_car["value"]:
                payment_choices.append(f"Pay cash (${selected_car['value']})")

            # Bank account option
            if self.player.bank_account and self.player.bank_account.balance >= selected_car["value"]:
                payment_choices.append(f"Pay from bank account (${selected_car['value']})")

            # Auto loan option
            payment_choices.append(f"Auto loan (${selected_car['value']} at 6% interest for 5 years)")

            payment_choice = self.get_choice("How would you like to pay?", payment_choices)

            if "cash" in payment_choice.lower():
                self.player.cash -= selected_car["value"]
                print(f"\nYou paid ${selected_car['value']} in cash for your {selected_car['name']}.")
            elif "bank account" in payment_choice.lower():
                self.player.bank_account.withdraw(selected_car["value"])
                print(f"\nYou paid ${selected_car['value']} from your bank account for your {selected_car['name']}.")
            else:  # Auto loan
                # Create auto loan
                auto_loan = Loan("Auto Loan", selected_car["value"], 0.06, 5)  # 6% interest, 5 year term
                self.player.loans.append(auto_loan)
                print(f"\nYou took out an auto loan of ${selected_car['value']} at 6% interest for 5 years.")
                print(f"Your monthly payment is ${auto_loan.monthly_payment:.2f}")

            # Add car to assets
            new_car = Asset("Car", selected_car["name"], selected_car["value"], selected_car["condition"])
            self.player.assets.append(new_car)

            print(f"\nCongratulations on your new {selected_car['name']}!")
        else:
            print("\nYou've decided to use public transportation for now.")
            print("This saves money but may limit your job opportunities and lifestyle choices.")

        input("\nPress Enter to continue your journey...")

    def house_purchase_opportunity(self):
        self.clear_screen()
        print("\n" + "=" * 60)
        print("LIFE EVENT: HOUSING DECISION")
        print("=" * 60)
        print("\nYou've been renting for a while. It might be time to consider buying a home.")

        # Housing options
        house_options = [
            {"name": "Small Condo", "value": 150000, "condition": "Good"},
            {"name": "Townhouse", "value": 250000, "condition": "Good"},
            {"name": "Single Family Home", "value": 350000, "condition": "Good"}
        ]

        choices = [f"{house['name']} - ${house['value']} ({house['condition']} condition)" for house in house_options]
        choices.append("Continue Renting - $1,200/month")

        choice = self.get_choice("What housing option would you like to choose?", choices)

        if choice != choices[-1]:  # If not continuing to rent
            house_index = choices.index(choice)
            selected_house = house_options[house_index]

            # Check if they qualify for a mortgage
            max_mortgage = self.player.salary * 4  # Rough estimate of maximum mortgage
            down_payment_needed = selected_house["value"] * 0.2  # 20% down payment

            if selected_house["value"] > max_mortgage:
                print(f"\nBased on your income of ${self.player.salary}/year, you don't qualify for a ${selected_house['value']} mortgage.")
                print("You'll need to increase your income or choose a less expensive property.")
                input("\nPress Enter to continue...")
                return

            print(f"\nYou qualify for this mortgage! You'll need a down payment of ${down_payment_needed:.2f} (20%).")

            # Check if they have the down payment
            if self.player.cash >= down_payment_needed:
                print(f"You have ${self.player.cash:.2f} in cash, which is enough for the down payment.")
            elif self.player.bank_account and self.player.bank_account.balance >= down_payment_needed:
                print(f"You have ${self.player.bank_account.balance:.2f} in your bank account, which is enough for the down payment.")
            else:
                print(f"You don't have enough for the down payment. You need ${down_payment_needed:.2f}.")
                print("You should save more money before buying a house.")
                input("\nPress Enter to continue...")
                return

            # Payment options for down payment
            payment_choices = []

            # Cash option if they have enough money
            if self.player.cash >= down_payment_needed:
                payment_choices.append(f"Pay down payment in cash (${down_payment_needed:.2f})")

            # Bank account option
            if self.player.bank_account and self.player.bank_account.balance >= down_payment_needed:
                payment_choices.append(f"Pay down payment from bank account (${down_payment_needed:.2f})")

            payment_choice = self.get_choice("How would you like to pay the down payment?", payment_choices)

            if "cash" in payment_choice.lower():
                self.player.cash -= down_payment_needed
            else:  # bank account
                self.player.bank_account.withdraw(down_payment_needed)

            # Create mortgage
            mortgage_amount = selected_house["value"] - down_payment_needed
            mortgage = Loan("Mortgage", mortgage_amount, 0.04, 30)  # 4% interest, 30 year term
            self.player.loans.append(mortgage)

            # Add house to assets
            new_house = Asset("House", selected_house["name"], selected_house["value"], selected_house["condition"])
            self.player.assets.append(new_house)

            print(f"\nCongratulations on your new {selected_house['name']}!")
            print(f"You took out a mortgage of ${mortgage_amount:.2f} at 4% interest for 30 years.")
            print(f"Your monthly payment is ${mortgage.monthly_payment:.2f}")
        else:
            print("\nYou've decided to continue renting for now.")
            print("This gives you flexibility but doesn't build equity.")

        input("\nPress Enter to continue your journey...")

    def family_planning_opportunity(self):
        self.clear_screen()
        print("\n" + "=" * 60)
        print("LIFE EVENT: FAMILY PLANNING")
        print("=" * 60)
        print("\nYou're at a point in life where you might want to start a family.")

        choices = ["Get married", "Stay single for now"]
        choice = self.get_choice("What would you like to do?", choices)

        if choice == choices[0]:  # Get married
            print("\nCongratulations on your marriage!")
            print("Your spouse also has an income, which will help with expenses.")

            # Add spouse to family
            spouse_income = int(self.player.salary * random.uniform(0.5, 1.2))  # 50% to 120% of player's salary
            self.player.family.append({"relation": "Spouse", "name": "Spouse", "age": self.player.age - random.randint(-5, 5), "income": spouse_income})

            print(f"Your spouse earns ${spouse_income}/year.")

            # Wedding costs
            wedding_cost = random.randint(5000, 30000)
            print(f"\nYour wedding cost ${wedding_cost}.")

            # Handle payment
            if self.player.cash >= wedding_cost:
                self.player.cash -= wedding_cost
                print("You paid for the wedding in cash.")
            elif self.player.bank_account and self.player.bank_account.balance >= wedding_cost:
                self.player.bank_account.withdraw(wedding_cost)
                print("You paid for the wedding from your bank account.")
            elif self.player.credit_card and (self.player.credit_card.balance + wedding_cost) <= self.player.credit_card.limit:
                self.player.credit_card.charge(wedding_cost)
                print("You paid for the wedding with your credit card.")
            else:
                print("You couldn't afford a big wedding, so you had a small ceremony.")
                self.player.cash -= min(self.player.cash, 1000)

            # Children option
            child_choice = self.get_choice("Would you like to have children?", ["Yes", "Not yet"])

            if child_choice == "Yes":
                num_children = random.randint(1, 2)  # Start with 1-2 children
                for i in range(num_children):
                    child_age = random.randint(0, 2)  # 0-2 years old
                    self.player.family.append({"relation": "Child", "name": f"Child {i+1}", "age": child_age, "income": 0})

                print(f"\nCongratulations! You now have {num_children} {'child' if num_children == 1 else 'children'}.")
                print("Children bring joy but also financial responsibilities.")
                print("Your monthly expenses have increased.")
        else:
            print("\nYou've decided to stay single for now. This gives you more financial flexibility.")

        input("\nPress Enter to continue your journey...")

    def display_status(self):
        """Display the current status of the player and game."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print(f"MONEY SMARTZ - Year {self.current_year}, Month {self.current_month}")
        print("=" * 60)

        # Basic info
        print(f"\nName: {self.player.name}")
        print(f"Age: {self.player.age}")
        print(f"Education: {self.player.education}")

        # Career
        if self.player.job:
            print(f"Job: {self.player.job}")
            print(f"Annual Salary: ${self.player.salary}")
            print(f"Monthly Income: ${self.player.salary / 12:.2f}")
        else:
            print("Job: Unemployed")

        # Financial status
        print("\n--- FINANCIAL STATUS ---")
        print(f"Cash: ${self.player.cash:.2f}")

        if self.player.bank_account:
            print(f"{self.player.bank_account.account_type} Account Balance: ${self.player.bank_account.balance:.2f}")

        if self.player.credit_card:
            print(f"Credit Card Balance: ${self.player.credit_card.balance:.2f}")
            print(f"Credit Card Limit: ${self.player.credit_card.limit:.2f}")

        print(f"Credit Score: {self.player.credit_score}")

        # Loans
        if self.player.loans:
            print("\n--- LOANS ---")
            for loan in self.player.loans:
                print(f"{loan.loan_type}: ${loan.current_balance:.2f} remaining (${loan.monthly_payment:.2f}/month)")

        # Assets
        if self.player.assets:
            print("\n--- ASSETS ---")
            for asset in self.player.assets:
                print(f"{asset.name} ({asset.asset_type}): ${asset.current_value:.2f} current value, {asset.condition} condition")

        # Family
        if self.player.family:
            print("\n--- FAMILY ---")
            for member in self.player.family:
                if member["relation"] == "Spouse":
                    print(f"Spouse: Age {member['age']}, Income: ${member['income']}/year")
                else:
                    print(f"{member['relation']}: {member['name']}, Age {member['age']}")

        print("\n" + "=" * 60)

    def get_player_action(self):
        """Get the player's next action."""
        actions = ["Continue to next month"]

        # Add banking actions if no bank account
        if not self.player.bank_account:
            actions.append("Open a bank account")
        else:
            # Add banking actions
            actions.append("View bank account details")
            actions.append("Deposit money to bank")
            actions.append("Withdraw money from bank")

            # Add debit card action if no debit card
            if not self.player.debit_card:
                actions.append("Get a debit card")

        # Add credit card actions
        if not self.player.credit_card and self.player.age >= 18:
            actions.append("Apply for a credit card")
        elif self.player.credit_card:
            actions.append("View credit card details")
            if self.player.credit_card.balance > 0:
                actions.append("Make a credit card payment")

        # Add loan actions
        if self.player.loans:
            actions.append("View loan details")
            actions.append("Make extra loan payment")

        # Add asset actions
        if self.player.assets:
            actions.append("View assets")

        # Add career actions
        if self.player.age >= 18:
            actions.append("Look for a better job")

        # Add housing actions if player is old enough
        if self.player.age >= 22 and not any(a.asset_type == "House" for a in self.player.assets):
            actions.append("Look for housing")

        # Add family actions
        if self.player.age >= 25 and not self.player.family:
            actions.append("Consider starting a family")

        # Add retirement action
        if self.player.age >= 60:
            actions.append("Retire")

        choice = self.get_choice("What would you like to do?", actions)

        # Handle the chosen action
        if choice == "Continue to next month":
            return
        elif choice == "Open a bank account":
            self.open_bank_account()
        elif choice == "View bank account details":
            self.view_bank_account()
        elif choice == "Deposit money to bank":
            self.deposit_to_bank()
        elif choice == "Withdraw money from bank":
            self.withdraw_from_bank()
        elif choice == "Get a debit card":
            self.get_debit_card()
        elif choice == "Apply for a credit card":
            self.apply_for_credit_card()
        elif choice == "View credit card details":
            self.view_credit_card()
        elif choice == "Make a credit card payment":
            self.pay_credit_card()
        elif choice == "View loan details":
            self.view_loans()
        elif choice == "Make extra loan payment":
            self.make_extra_loan_payment()
        elif choice == "View assets":
            self.view_assets()
        elif choice == "Look for a better job":
            self.look_for_job()
        elif choice == "Look for housing":
            self.house_purchase_opportunity()
        elif choice == "Consider starting a family":
            self.family_planning_opportunity()
        elif choice == "Retire":
            self.end_game("retirement")

    def open_bank_account(self):
        """Open a new bank account."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("OPENING A BANK ACCOUNT")
        print("=" * 60)

        account_type = self.get_choice("What type of account would you like to open?", ["Checking", "Savings"])

        self.player.bank_account = BankAccount(account_type)

        # Initial deposit
        if self.player.cash > 0:
            max_deposit = min(self.player.cash, 1000)
            deposit_amount = float(input(f"\nHow much would you like to deposit? (0-{max_deposit}): $"))

            if deposit_amount > 0 and deposit_amount <= self.player.cash:
                self.player.bank_account.deposit(deposit_amount)
                self.player.cash -= deposit_amount
                print(f"\nYou've deposited ${deposit_amount} into your new {account_type} account.")
            else:
                print("\nInvalid amount. No deposit made.")

        print(f"\nCongratulations! You've opened a new {account_type} account.")

        # Offer debit card
        if account_type == "Checking":
            debit_choice = self.get_choice("Would you like a debit card with your account?", ["Yes", "No"])
            if debit_choice == "Yes":
                self.player.debit_card = Card("Debit")
                print("\nYou now have a debit card linked to your checking account.")

        input("\nPress Enter to continue...")

    def view_bank_account(self):
        """View bank account details."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("BANK ACCOUNT DETAILS")
        print("=" * 60)

        if not self.player.bank_account:
            print("\nYou don't have a bank account yet.")
            input("\nPress Enter to continue...")
            return

        print(f"\nAccount Type: {self.player.bank_account.account_type}")
        print(f"Current Balance: ${self.player.bank_account.balance:.2f}")

        if self.player.bank_account.account_type == "Savings":
            print(f"Interest Rate: {self.player.bank_account.interest_rate * 100:.2f}%")
            annual_interest = self.player.bank_account.balance * self.player.bank_account.interest_rate
            print(f"Estimated Annual Interest: ${annual_interest:.2f}")

        print("\nRecent Transactions:")
        for transaction in self.player.bank_account.transaction_history[-5:]:
            print(f"- {transaction}")

        input("\nPress Enter to continue...")

    def deposit_to_bank(self):
        """Deposit money to bank account."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("DEPOSIT TO BANK")
        print("=" * 60)

        if not self.player.bank_account:
            print("\nYou don't have a bank account yet.")
            input("\nPress Enter to continue...")
            return

        print(f"\nYour cash: ${self.player.cash:.2f}")
        print(f"Current {self.player.bank_account.account_type} Balance: ${self.player.bank_account.balance:.2f}")

        if self.player.cash <= 0:
            print("\nYou don't have any cash to deposit.")
            input("\nPress Enter to continue...")
            return

        try:
            deposit_amount = float(input(f"\nHow much would you like to deposit? (0-{self.player.cash:.2f}): $"))

            if deposit_amount > 0 and deposit_amount <= self.player.cash:
                self.player.bank_account.deposit(deposit_amount)
                self.player.cash -= deposit_amount
                print(f"\nYou've deposited ${deposit_amount:.2f} into your {self.player.bank_account.account_type} account.")
                print(f"New balance: ${self.player.bank_account.balance:.2f}")
            else:
                print("\nInvalid amount. No deposit made.")
        except ValueError:
            print("\nInvalid input. Please enter a number.")

        input("\nPress Enter to continue...")

    def withdraw_from_bank(self):
        """Withdraw money from bank account."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("WITHDRAW FROM BANK")
        print("=" * 60)

        if not self.player.bank_account:
            print("\nYou don't have a bank account yet.")
            input("\nPress Enter to continue...")
            return

        print(f"\nYour cash: ${self.player.cash:.2f}")
        print(f"Current {self.player.bank_account.account_type} Balance: ${self.player.bank_account.balance:.2f}")

        if self.player.bank_account.balance <= 0:
            print("\nYou don't have any money in your account to withdraw.")
            input("\nPress Enter to continue...")
            return

        try:
            withdraw_amount = float(input(f"\nHow much would you like to withdraw? (0-{self.player.bank_account.balance:.2f}): $"))

            if withdraw_amount > 0 and withdraw_amount <= self.player.bank_account.balance:
                if self.player.bank_account.withdraw(withdraw_amount):
                    self.player.cash += withdraw_amount
                    print(f"\nYou've withdrawn ${withdraw_amount:.2f} from your {self.player.bank_account.account_type} account.")
                    print(f"New balance: ${self.player.bank_account.balance:.2f}")
                else:
                    print("\nWithdrawal failed.")
            else:
                print("\nInvalid amount. No withdrawal made.")
        except ValueError:
            print("\nInvalid input. Please enter a number.")

        input("\nPress Enter to continue...")

    def get_debit_card(self):
        """Get a debit card for the checking account."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("GET A DEBIT CARD")
        print("=" * 60)

        if not self.player.bank_account:
            print("\nYou need a bank account before you can get a debit card.")
        elif self.player.bank_account.account_type != "Checking":
            print("\nDebit cards are only available for checking accounts.")
            print("You currently have a savings account.")
        elif self.player.debit_card:
            print("\nYou already have a debit card.")
        else:
            print("\nYou've been approved for a debit card linked to your checking account.")
            self.player.debit_card = Card("Debit")
            print("You can now use your debit card for purchases and ATM withdrawals.")

        input("\nPress Enter to continue...")

    def apply_for_credit_card(self):
        """Apply for a credit card."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("APPLY FOR A CREDIT CARD")
        print("=" * 60)

        if self.player.age < 18:
            print("\nYou must be at least 18 years old to apply for a credit card.")
        elif self.player.credit_card:
            print("\nYou already have a credit card.")
        elif not self.player.job:
            print("\nYou need a job to qualify for a credit card.")
        else:
            # Credit limit based on income and credit score
            base_limit = min(self.player.salary * 0.2, 5000)  # 20% of salary or $5000, whichever is lower

            # Adjust based on credit score
            if self.player.credit_score >= 750:
                limit = base_limit * 1.5
            elif self.player.credit_score >= 700:
                limit = base_limit * 1.2
            elif self.player.credit_score >= 650:
                limit = base_limit
            elif self.player.credit_score >= 600:
                limit = base_limit * 0.8
            else:
                limit = base_limit * 0.5

            print("\nBased on your income and credit score, you've been approved for a credit card!")
            self.player.credit_card = Card("Credit", limit)
            print(f"Your credit limit is ${limit:.2f}")
            print("Use your credit card wisely to build your credit score.")

        input("\nPress Enter to continue...")

    def view_credit_card(self):
        """View credit card details."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("CREDIT CARD DETAILS")
        print("=" * 60)

        if not self.player.credit_card:
            print("\nYou don't have a credit card yet.")
            input("\nPress Enter to continue...")
            return

        print(f"\nCredit Limit: ${self.player.credit_card.limit:.2f}")
        print(f"Current Balance: ${self.player.credit_card.balance:.2f}")
        print(f"Available Credit: ${self.player.credit_card.limit - self.player.credit_card.balance:.2f}")

        if self.player.credit_card.balance > 0:
            min_payment = max(25, self.player.credit_card.balance * 0.03)
            print(f"Minimum Monthly Payment: ${min_payment:.2f}")

        print("\nRecent Transactions:")
        for transaction in self.player.credit_card.transaction_history[-5:]:
            print(f"- {transaction}")

        input("\nPress Enter to continue...")

    def pay_credit_card(self):
        """Make a payment on the credit card."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("PAY CREDIT CARD")
        print("=" * 60)

        if not self.player.credit_card:
            print("\nYou don't have a credit card yet.")
            input("\nPress Enter to continue...")
            return

        if self.player.credit_card.balance <= 0:
            print("\nYour credit card has a zero balance. No payment needed.")
            input("\nPress Enter to continue...")
            return

        print(f"\nCredit Card Balance: ${self.player.credit_card.balance:.2f}")
        print(f"Your Cash: ${self.player.cash:.2f}")

        if self.player.bank_account:
            print(f"Bank Account Balance: ${self.player.bank_account.balance:.2f}")

        min_payment = max(25, self.player.credit_card.balance * 0.03)
        print(f"Minimum Payment Required: ${min_payment:.2f}")

        # Payment options
        payment_options = []

        if self.player.cash >= min_payment:
            payment_options.append(f"Pay minimum (${min_payment:.2f}) from cash")

        if self.player.cash >= self.player.credit_card.balance:
            payment_options.append(f"Pay full balance (${self.player.credit_card.balance:.2f}) from cash")

        if self.player.bank_account and self.player.bank_account.balance >= min_payment:
            payment_options.append(f"Pay minimum (${min_payment:.2f}) from bank account")

        if self.player.bank_account and self.player.bank_account.balance >= self.player.credit_card.balance:
            payment_options.append(f"Pay full balance (${self.player.credit_card.balance:.2f}) from bank account")

        payment_options.append("Custom payment amount")
        payment_options.append("Skip payment (will affect credit score)")

        choice = self.get_choice("How would you like to pay?", payment_options)

        if "minimum" in choice and "cash" in choice:
            self.player.cash -= min_payment
            self.player.credit_card.pay(min_payment)
            print(f"\nYou paid the minimum payment of ${min_payment:.2f} from cash.")
        elif "full balance" in choice and "cash" in choice:
            payment = self.player.credit_card.balance
            self.player.cash -= payment
            self.player.credit_card.pay(payment)
            print(f"\nYou paid the full balance of ${payment:.2f} from cash.")
        elif "minimum" in choice and "bank account" in choice:
            self.player.bank_account.withdraw(min_payment)
            self.player.credit_card.pay(min_payment)
            print(f"\nYou paid the minimum payment of ${min_payment:.2f} from your bank account.")
        elif "full balance" in choice and "bank account" in choice:
            payment = self.player.credit_card.balance
            self.player.bank_account.withdraw(payment)
            self.player.credit_card.pay(payment)
            print(f"\nYou paid the full balance of ${payment:.2f} from your bank account.")
        elif "Custom" in choice:
            try:
                payment = float(input(f"\nEnter payment amount (${min_payment:.2f}-${self.player.credit_card.balance:.2f}): $"))

                if payment < min_payment:
                    print(f"\nPayment must be at least the minimum payment of ${min_payment:.2f}.")
                elif payment > self.player.credit_card.balance:
                    print(f"\nPayment cannot exceed the current balance of ${self.player.credit_card.balance:.2f}.")
                else:
                    # Choose payment source
                    source = self.get_choice("Pay from:", ["Cash", "Bank Account"])

                    if source == "Cash" and self.player.cash >= payment:
                        self.player.cash -= payment
                        self.player.credit_card.pay(payment)
                        print(f"\nYou paid ${payment:.2f} from cash.")
                    elif source == "Bank Account" and self.player.bank_account and self.player.bank_account.balance >= payment:
                        self.player.bank_account.withdraw(payment)
                        self.player.credit_card.pay(payment)
                        print(f"\nYou paid ${payment:.2f} from your bank account.")
                    else:
                        print("\nInsufficient funds for this payment.")
            except ValueError:
                print("\nInvalid input. Please enter a number.")
        elif "Skip" in choice:
            print("\nYou've chosen to skip this payment. This will negatively affect your credit score.")
            self.player.credit_score -= 30

        input("\nPress Enter to continue...")

    def view_loans(self):
        """View details of all loans."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("LOAN DETAILS")
        print("=" * 60)

        if not self.player.loans:
            print("\nYou don't have any loans.")
            input("\nPress Enter to continue...")
            return

        for i, loan in enumerate(self.player.loans):
            print(f"\n--- {loan.loan_type} ---")
            print(f"Original Amount: ${loan.original_amount:.2f}")
            print(f"Current Balance: ${loan.current_balance:.2f}")
            print(f"Interest Rate: {loan.interest_rate * 100:.2f}%")
            print(f"Term: {loan.term_years} years")
            print(f"Monthly Payment: ${loan.monthly_payment:.2f}")

            # Calculate payoff date
            months_left = loan.current_balance / (loan.monthly_payment - (loan.current_balance * loan.interest_rate / 12))
            years_left = months_left / 12
            print(f"Estimated Payoff: {years_left:.1f} years")

        input("\nPress Enter to continue...")

    def make_extra_loan_payment(self):
        """Make an extra payment on a loan."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("MAKE EXTRA LOAN PAYMENT")
        print("=" * 60)

        if not self.player.loans:
            print("\nYou don't have any loans.")
            input("\nPress Enter to continue...")
            return

        # Choose which loan to pay
        loan_choices = []
        for loan in self.player.loans:
            loan_choices.append(f"{loan.loan_type}: ${loan.current_balance:.2f} remaining")

        loan_choice = self.get_choice("Which loan would you like to make an extra payment on?", loan_choices)
        loan_index = loan_choices.index(loan_choice)
        selected_loan = self.player.loans[loan_index]

        print(f"\nSelected: {selected_loan.loan_type}")
        print(f"Current Balance: ${selected_loan.current_balance:.2f}")
        print(f"Regular Monthly Payment: ${selected_loan.monthly_payment:.2f}")
        print(f"Your Cash: ${self.player.cash:.2f}")

        if self.player.bank_account:
            print(f"Bank Account Balance: ${self.player.bank_account.balance:.2f}")

        try:
            extra_payment = float(input("\nHow much extra would you like to pay? $"))

            if extra_payment <= 0:
                print("\nPayment must be greater than zero.")
            else:
                # Choose payment source
                source = self.get_choice("Pay from:", ["Cash", "Bank Account"])

                if source == "Cash" and self.player.cash >= extra_payment:
                    self.player.cash -= extra_payment
                    selected_loan.make_payment(extra_payment)
                    print(f"\nYou made an extra payment of ${extra_payment:.2f} on your {selected_loan.loan_type}.")
                    print(f"New balance: ${selected_loan.current_balance:.2f}")
                elif source == "Bank Account" and self.player.bank_account and self.player.bank_account.balance >= extra_payment:
                    self.player.bank_account.withdraw(extra_payment)
                    selected_loan.make_payment(extra_payment)
                    print(f"\nYou made an extra payment of ${extra_payment:.2f} on your {selected_loan.loan_type}.")
                    print(f"New balance: ${selected_loan.current_balance:.2f}")
                else:
                    print("\nInsufficient funds for this payment.")
        except ValueError:
            print("\nInvalid input. Please enter a number.")

        input("\nPress Enter to continue...")

    def view_assets(self):
        """View details of all assets."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("ASSET DETAILS")
        print("=" * 60)

        if not self.player.assets:
            print("\nYou don't have any assets yet.")
            input("\nPress Enter to continue...")
            return

        for asset in self.player.assets:
            print(f"\n--- {asset.name} ({asset.asset_type}) ---")
            print(f"Purchase Value: ${asset.purchase_value:.2f}")
            print(f"Current Value: ${asset.current_value:.2f}")
            print(f"Condition: {asset.condition}")
            print(f"Age: {asset.age} years")

            # Show appreciation/depreciation
            value_change = asset.current_value - asset.purchase_value
            value_percent = (value_change / asset.purchase_value) * 100
            if value_change >= 0:
                print(f"Appreciation: ${value_change:.2f} ({value_percent:.1f}%)")
            else:
                print(f"Depreciation: ${abs(value_change):.2f} ({abs(value_percent):.1f}%)")

        input("\nPress Enter to continue...")

    def look_for_job(self):
        """Look for a better job opportunity."""
        self.clear_screen()
        print("\n" + "=" * 60)
        print("JOB SEARCH")
        print("=" * 60)

        if self.player.age < 18:
            print("\nYou're too young to work full-time. Wait until you're 18.")
            input("\nPress Enter to continue...")
            return

        print("\nYou're searching for a better job opportunity...")
        print("This will take time and effort, but could lead to higher income.")

        # Current job info
        if self.player.job:
            print(f"\nCurrent Job: {self.player.job}")
            print(f"Current Salary: ${self.player.salary}/year")

        # Generate job opportunities based on education and experience
        job_options = []

        # Base salary multiplier based on education
        salary_multiplier = 1.0
        if self.player.education == "College Graduate":
            salary_multiplier = 1.5
        elif self.player.education == "Associate's Degree":
            salary_multiplier = 1.2
        elif self.player.education == "Trade School Graduate":
            salary_multiplier = 1.3

        # Add experience multiplier (1% per year over 22)
        experience_years = max(0, self.player.age - 22)
        experience_multiplier = 1.0 + (experience_years * 0.01)

        # Generate 3 random job opportunities
        for i in range(3):
            # Job quality varies (some better, some worse)
            job_quality = random.uniform(0.8, 1.3)

            if self.player.education == "College Graduate":
                job_title = random.choice([
                    "Senior Professional", "Department Manager", "Project Lead",
                    "Consultant", "Specialist", "Team Lead"
                ])
                base_salary = random.randint(50000, 80000)
            elif self.player.education == "Associate's Degree":
                job_title = random.choice([
                    "Technical Lead", "Office Manager", "Sales Manager",
                    "Assistant Director", "Coordinator", "Supervisor"
                ])
                base_salary = random.randint(40000, 60000)
            elif self.player.education == "Trade School Graduate":
                job_title = random.choice([
                    "Master Tradesperson", "Shop Foreman", "Lead Technician",
                    "Service Manager", "Contractor", "Specialist"
                ])
                base_salary = random.randint(45000, 65000)
            else:  # High school only
                job_title = random.choice([
                    "Shift Supervisor", "Team Lead", "Assistant Manager",
                    "Sales Representative", "Office Assistant", "Customer Service Manager"
                ])
                base_salary = random.randint(30000, 45000)

            # Calculate final salary with all multipliers
            final_salary = int(base_salary * salary_multiplier * experience_multiplier * job_quality)

            # Only add jobs that are better than current (or if unemployed)
            if not self.player.job or final_salary > self.player.salary:
                job_options.append({"title": job_title, "salary": final_salary})

        # Add option to stay at current job
        if self.player.job:
            job_options.append({"title": self.player.job, "salary": self.player.salary, "current": True})

        # Add option to cancel job search
        job_options.append({"title": "Cancel job search", "salary": 0, "cancel": True})

        # No better jobs found
        if len(job_options) <= 2:  # Only current job and cancel option
            print("\nUnfortunately, you couldn't find any better job opportunities at this time.")
            print("Try again later or improve your qualifications.")
            input("\nPress Enter to continue...")
            return

        # Present job options
        print("\nYou've found the following job opportunities:")

        choices = []
        for job in job_options:
            if job.get("current"):
                choices.append(f"Stay at current job: {job['title']} - ${job['salary']}/year")
            elif job.get("cancel"):
                choices.append("Cancel job search")
            else:
                choices.append(f"{job['title']} - ${job['salary']}/year")

        choice = self.get_choice("Which job would you like to pursue?", choices)

        if "Cancel" in choice:
            print("\nYou've decided to cancel your job search.")
        elif "Stay at current job" in choice:
            print("\nYou've decided to stay at your current job.")
        else:
            # Find the selected job
            job_index = choices.index(choice)
            selected_job = job_options[job_index]

            # Update player's job and salary
            self.player.job = selected_job["title"]
            self.player.salary = selected_job["salary"]

            print(f"\nCongratulations! You are now a {self.player.job} earning ${self.player.salary}/year.")

            # Credit score boost for stable employment
            self.player.credit_score += 5
            print("Your credit score has improved due to stable employment.")

        input("\nPress Enter to continue...")

    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_choice(self, prompt, choices):
        """Get a choice from the user from a list of options."""
        self.clear_screen()
        print("\n" + prompt)

        for i, choice in enumerate(choices):
            print(f"{i+1}. {choice}")

        while True:
            try:
                choice_num = int(input("\nEnter your choice (number): "))
                if 1 <= choice_num <= len(choices):
                    return choices[choice_num - 1]
                else:
                    print(f"Please enter a number between 1 and {len(choices)}.")
            except ValueError:
                print("Please enter a valid number.")

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

# Main function to run the game
def main():
    game = Game()
    # Set the initial screen to the title screen
    game.gui_manager.set_screen(TitleScreen(game))
    # Run the GUI
    game.gui_manager.run()

if __name__ == "__main__":
    main()
