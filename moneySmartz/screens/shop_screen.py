import pygame
from moneySmartz.constants import *
from moneySmartz.ui import Screen, Button

SHOP_ITEMS = [
    {"name": "Groceries", "price": 50, "desc": "Weekly groceries for your family."},
    {"name": "Clothes", "price": 100, "desc": "A new set of clothes."},
    {"name": "Smartphone", "price": 600, "desc": "A modern smartphone.", "recurring": {"name": "Phone Plan", "amount": 30, "source": "bank_or_credit"}},
    {"name": "TV", "price": 400, "desc": "A 50-inch smart TV.", "recurring": {"name": "Streaming Service", "amount": 15, "source": "bank_or_credit"}},
    {"name": "Laptop", "price": 900, "desc": "A new laptop for work or school.", "recurring": {"name": "Software Subscription", "amount": 10, "source": "bank_or_credit"}},
    {"name": "Gift", "price": 30, "desc": "A gift for a friend or family member."},
    {"name": "Home", "price": 5000, "desc": "A place to call your own. Unlocks a new chapter!"},
    {"name": "Vehicle", "price": 1200, "desc": "Buy a new or used vehicle!"},
]

class ShopScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.selected_item = None
        self.message = ""
        self.create_buttons()

    def create_buttons(self):
        self.buttons = []
        y = 120
        for idx, item in enumerate(SHOP_ITEMS):
            btn = Button(60, y, 300, 50, f"{item['name']} - ${item['price']}", action=lambda i=idx: self.select_item(i))
            self.buttons.append(btn)
            y += 60
        # Move payment and back buttons to the far right
        right_x = 700  # Adjust as needed for your window size
        self.pay_cash_btn = Button(right_x, 120, 180, 40, "Pay Cash", action=self.pay_cash)
        self.pay_bank_btn = Button(right_x, 180, 180, 40, "Pay Bank", action=self.pay_bank)
        self.pay_credit_btn = Button(right_x, 240, 180, 40, "Pay Credit", action=self.pay_credit)
        self.back_btn = Button(right_x, 420, 120, 40, "Back", action=self.go_back)

    def select_item(self, idx):
        self.selected_item = SHOP_ITEMS[idx]
        if self.selected_item['name'] == "Home":
            from moneySmartz.screens.home_purchase_screen import HomePurchaseScreen
            self.game.gui_manager.set_screen(HomePurchaseScreen(self.game))
            return
        if self.selected_item['name'] == "Vehicle":
            from moneySmartz.screens.vehicle_purchase_screen import VehiclePurchaseScreen
            self.game.gui_manager.set_screen(VehiclePurchaseScreen(self.game))
            return
        self.message = f"Selected: {self.selected_item['name']}"

    def pay_cash(self):
        if not self.selected_item:
            self.message = "Select an item first."
            return
        # Special logic for buying a home
        if self.selected_item['name'] == "Home":
            if self.game.player.cash >= self.selected_item['price']:
                self.game.player.cash -= self.selected_item['price']
                self.game.player.inventory.append(self.selected_item['name'])
                self.game.player.has_home = True
                self.message = "Congratulations! You bought a home and unlocked a new chapter!"
                # Optionally, trigger a new screen or event here
            else:
                self.message = "Not enough cash to buy a home."
            return
        if self.game.player.cash >= self.selected_item['price']:
            self.game.player.cash -= self.selected_item['price']
            self.game.player.inventory.append(self.selected_item['name'])
            # Add recurring bill if item has one
            if 'recurring' in self.selected_item:
                self.game.player.recurring_bills.append(self.selected_item['recurring'])
            self.message = f"Bought {self.selected_item['name']} with cash!"
        else:
            self.message = "Not enough cash."

    def pay_bank(self):
        if not self.selected_item:
            self.message = "Select an item first."
            return
        # Special logic for buying a home
        if self.selected_item['name'] == "Home":
            acct = self.game.player.bank_account
            if acct and acct.balance >= self.selected_item['price']:
                acct.withdraw(self.selected_item['price'])
                self.game.player.inventory.append(self.selected_item['name'])
                self.game.player.has_home = True
                self.message = "Congratulations! You bought a home and unlocked a new chapter!"
                # Optionally, trigger a new screen or event here
            else:
                self.message = "Not enough in bank account to buy a home."
            return
        acct = self.game.player.bank_account
        if acct and acct.balance >= self.selected_item['price']:
            acct.withdraw(self.selected_item['price'])
            self.game.player.inventory.append(self.selected_item['name'])
            if 'recurring' in self.selected_item:
                self.game.player.recurring_bills.append(self.selected_item['recurring'])
            self.message = f"Bought {self.selected_item['name']} from bank!"
        else:
            self.message = "Not enough in bank account."

    def pay_credit(self):
        if not self.selected_item:
            self.message = "Select an item first."
            return
        # Special logic for buying a home
        if self.selected_item['name'] == "Home":
            card = self.game.player.credit_card
            if card and card.charge(self.selected_item['price']):
                self.game.player.inventory.append(self.selected_item['name'])
                self.game.player.has_home = True
                self.message = "Congratulations! You bought a home and unlocked a new chapter!"
                # Optionally, trigger a new screen or event here
            else:
                self.message = "Not enough credit or no card to buy a home."
            return
        card = self.game.player.credit_card
        if card and card.charge(self.selected_item['price']):
            self.game.player.inventory.append(self.selected_item['name'])
            if 'recurring' in self.selected_item:
                self.game.player.recurring_bills.append(self.selected_item['recurring'])
            self.message = f"Bought {self.selected_item['name']} on credit!"
        else:
            self.message = "Not enough credit or no card."

    def go_back(self):
        from moneySmartz.screens.game_screen import GameScreen
        self.game.gui_manager.set_screen(GameScreen(self.game))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            # Check item buttons
            for btn in self.buttons:
                if btn.rect.collidepoint(mouse_pos):
                    if btn.action:
                        btn.action()
                        return
            # Check payment buttons
            if self.selected_item:
                for btn in [self.pay_cash_btn, self.pay_bank_btn, self.pay_credit_btn]:
                    if btn.rect.collidepoint(mouse_pos):
                        if btn.action:
                            btn.action()
                            return
            # Check back button
            if self.back_btn.rect.collidepoint(mouse_pos):
                if self.back_btn.action:
                    self.back_btn.action()
                    return

    def draw(self, surface):
        surface.fill(WHITE)
        font = pygame.font.SysFont('Arial', FONT_LARGE)
        title = font.render("Shop", True, BLUE)
        surface.blit(title, (60, 40))
        font_small = pygame.font.SysFont('Arial', FONT_MEDIUM)
        y = 120
        for idx, item in enumerate(SHOP_ITEMS):
            desc = font_small.render(item['desc'], True, BLACK)
            surface.blit(desc, (380, y+10))
            y += 60
        for btn in self.buttons:
            btn.draw(surface)
        if self.selected_item:
            self.pay_cash_btn.draw(surface)
            self.pay_bank_btn.draw(surface)
            self.pay_credit_btn.draw(surface)
        self.back_btn.draw(surface)
        msg_font = pygame.font.SysFont('Arial', FONT_MEDIUM)
        msg = msg_font.render(self.message, True, RED if "Not" in self.message else GREEN)
        # Move message text further down to avoid overlap
        surface.blit(msg, (60, 500))
