import pygame
from moneySmartz.constants import *
from moneySmartz.ui import Screen, Button

VEHICLE_OPTIONS = [
    {"name": "Used Car", "price": 1200, "desc": "Reliable but basic transportation."},
    {"name": "Sedan", "price": 6000, "desc": "A comfortable family sedan."},
    {"name": "SUV", "price": 15000, "desc": "Spacious and powerful SUV."},
]

class VehiclePurchaseScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.selected_vehicle = None
        self.message = ""
        self.create_buttons()

    def create_buttons(self):
        self.buttons = []
        y = 150
        for idx, vehicle in enumerate(VEHICLE_OPTIONS):
            btn = Button(80, y, 400, 60, f"{vehicle['name']} - ${vehicle['price']}", action=lambda i=idx: self.select_vehicle(i))
            self.buttons.append(btn)
            y += 90
        self.buy_cash_btn = Button(600, 150, 180, 40, "Buy Cash", action=self.buy_cash)
        self.buy_bank_btn = Button(600, 210, 180, 40, "Buy Bank", action=self.buy_bank)
        self.buy_credit_btn = Button(600, 270, 180, 40, "Buy Credit", action=self.buy_credit)
        self.finance_btn = Button(600, 330, 180, 40, "Finance", action=self.finance_vehicle)
        self.back_btn = Button(600, 400, 120, 40, "Back", action=self.go_back)

    def select_vehicle(self, idx):
        self.selected_vehicle = VEHICLE_OPTIONS[idx]
        self.message = f"Selected: {self.selected_vehicle['name']}"

    def buy_cash(self):
        if not self.selected_vehicle:
            self.message = "Select a vehicle first."
            return
        if self.game.player.cash >= self.selected_vehicle['price']:
            self.game.player.cash -= self.selected_vehicle['price']
            self.game.player.vehicle = self.selected_vehicle['name']
            self.message = f"You bought the {self.selected_vehicle['name']} with cash!"
        else:
            self.message = "Not enough cash."

    def buy_bank(self):
        if not self.selected_vehicle:
            self.message = "Select a vehicle first."
            return
        acct = self.game.player.bank_account
        if acct and acct.balance >= self.selected_vehicle['price']:
            acct.withdraw(self.selected_vehicle['price'])
            self.game.player.vehicle = self.selected_vehicle['name']
            self.message = f"You bought the {self.selected_vehicle['name']} from bank!"
        else:
            self.message = "Not enough in bank account."

    def buy_credit(self):
        if not self.selected_vehicle:
            self.message = "Select a vehicle first."
            return
        card = self.game.player.credit_card
        if card and card.charge(self.selected_vehicle['price']):
            self.game.player.vehicle = self.selected_vehicle['name']
            self.message = f"You bought the {self.selected_vehicle['name']} on credit!"
        else:
            self.message = "Not enough credit or no card."

    def finance_vehicle(self):
        if not self.selected_vehicle:
            self.message = "Select a vehicle first."
            return
        # Assume player.credit_score is available and 700+ is good
        if hasattr(self.game.player, 'credit_score') and self.game.player.credit_score >= 700:
            # Example: 20% down, rest as a recurring bill
            down_payment = int(self.selected_vehicle['price'] * 0.2)
            financed_amount = self.selected_vehicle['price'] - down_payment
            if self.game.player.cash >= down_payment:
                self.game.player.cash -= down_payment
                self.game.player.vehicle = self.selected_vehicle['name']
                # Add a recurring bill for the financed amount (e.g., 12 months)
                monthly_payment = int(financed_amount / 12)
                self.game.player.recurring_bills.append({
                    'name': f"{self.selected_vehicle['name']} Loan",
                    'amount': monthly_payment,
                    'months': 12,
                    'source': 'bank_or_credit'
                })
                self.message = f"Financed {self.selected_vehicle['name']}! ${monthly_payment}/mo for 12 months."
            else:
                self.message = f"Need at least 20% down payment: ${down_payment}."
        else:
            self.message = "Credit score too low to finance."

    def go_back(self):
        from moneySmartz.screens.shop_screen import ShopScreen
        self.game.gui_manager.set_screen(ShopScreen(self.game))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for btn in self.buttons:
                if btn.rect.collidepoint(mouse_pos):
                    if btn.action:
                        btn.action()
                        return
            for btn in [self.buy_cash_btn, self.buy_bank_btn, self.buy_credit_btn, self.finance_btn, self.back_btn]:
                if btn.rect.collidepoint(mouse_pos):
                    if btn.action:
                        btn.action()
                        return

    def draw(self, surface):
        surface.fill((240, 240, 220))  # Light tan background for vehicle screen
        font = pygame.font.SysFont('Arial', FONT_LARGE)
        title = font.render("Choose Your Vehicle", True, BLUE)
        surface.blit(title, (80, 60))
        font_small = pygame.font.SysFont('Arial', FONT_MEDIUM)
        y = 150
        for vehicle in VEHICLE_OPTIONS:
            desc = font_small.render(vehicle['desc'], True, BLACK)
            surface.blit(desc, (500, y+20))
            y += 90
        for btn in self.buttons:
            btn.draw(surface)
        self.buy_cash_btn.draw(surface)
        self.buy_bank_btn.draw(surface)
        self.buy_credit_btn.draw(surface)
        self.finance_btn.draw(surface)
        self.back_btn.draw(surface)
        msg_font = pygame.font.SysFont('Arial', FONT_MEDIUM)
        msg = msg_font.render(self.message, True, RED if "Not" in self.message or "low" in self.message else GREEN)
        surface.blit(msg, (80, 480))

