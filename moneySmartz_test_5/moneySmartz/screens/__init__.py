"""
Screen modules for the Money Smartz game.

This package contains all the screen classes used in the game,
organized by category.
"""

# Base screens
from moneySmartz.screens.base_screens import (
    TitleScreen,
    NameInputScreen,
    IntroScreen,
    DebitCardScreen,
    EndGameScreen
)

# Financial screens
from moneySmartz.screens.financial_screens import (
    BankAccountScreen,
    BankDetailsScreen,
    DepositScreen,
    WithdrawScreen,
    GetDebitCardScreen,
    CreditCardScreen,
    CreditCardDetailsScreen,
    PayCreditCardScreen,
    LoanDetailsScreen,
    ExtraLoanPaymentScreen,
    AssetDetailsScreen,
    JobSearchScreen
)

# Game screen
from moneySmartz.screens.game_screen import GameScreen

# Life event screens
from moneySmartz.screens.life_event_screens import (
    HighSchoolGraduationScreen,
    CollegeGraduationScreen,
    CarPurchaseScreen,
    HousingScreen,
    FamilyPlanningScreen
)

# Random event screens
from moneySmartz.screens.random_event_screens import RandomEventScreen
