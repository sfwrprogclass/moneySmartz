import pygame
from moneySmartz.constants import *
from moneySmartz.ui import Screen, Button

HOME_OPTIONS = [
    {"name": "Starter Home", "price": 3000, "desc": "A cozy starter home. Affordable and simple."},
    {"name": "Family House", "price": 7000, "desc": "A spacious house for a growing family."},
    {"name": "Luxury Villa", "price": 20000, "desc": "A luxurious villa with all amenities."},
]

class HomePurchaseScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.selected_home = None
        self.message = ""
        self.create_buttons()

    def create_buttons(self):
        self.buttons = []
        y = 150
        for idx, home in enumerate(HOME_OPTIONS):
            btn = Button(80, y, 400, 60, f"{home['name']} - ${home['price']}", action=lambda i=idx: self.select_home(i))
            self.buttons.append(btn)
            y += 90
        self.buy_btn = Button(600, 200, 180, 50, "Buy Home", action=self.buy_home)
        self.back_btn = Button(600, 350, 120, 40, "Back", action=self.go_back)

    def select_home(self, idx):
        self.selected_home = HOME_OPTIONS[idx]
        self.message = f"Selected: {self.selected_home['name']}"

    def buy_home(self):
        if not self.selected_home:
            self.message = "Select a home first."
            return
        if self.game.player.cash >= self.selected_home['price']:
            self.game.player.cash -= self.selected_home['price']
            self.game.player.home = self.selected_home['name']
            self.message = f"Congratulations! You bought the {self.selected_home['name']}!"
        else:
            self.message = "Not enough cash."

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
            if self.buy_btn.rect.collidepoint(mouse_pos):
                if self.buy_btn.action:
                    self.buy_btn.action()
                    return
            if self.back_btn.rect.collidepoint(mouse_pos):
                if self.back_btn.action:
                    self.back_btn.action()
                    return

    def draw(self, surface):
        surface.fill((220, 240, 255))  # Light blue background for home screen
        font = pygame.font.SysFont('Arial', FONT_LARGE)
        title = font.render("Choose Your Home", True, BLUE)
        surface.blit(title, (80, 60))
        font_small = pygame.font.SysFont('Arial', FONT_MEDIUM)
        y = 150
        for home in HOME_OPTIONS:
            desc = font_small.render(home['desc'], True, BLACK)
            surface.blit(desc, (500, y+20))
            y += 90
        for btn in self.buttons:
            btn.draw(surface)
        self.buy_btn.draw(surface)
        self.back_btn.draw(surface)
        msg_font = pygame.font.SysFont('Arial', FONT_MEDIUM)
        msg = msg_font.render(self.message, True, RED if "Not" in self.message else GREEN)
        surface.blit(msg, (80, 420))

