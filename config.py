"""Configuration settings for the betting automation script."""

# URLs
LOGIN_URL = "https://vb.rebelbetting.com/login"
BET_LIST_URL = "https://vb.rebelbetting.com/"

# Selectors (placeholders - must be updated for actual site)
SELECTORS = {
    "bet_row": "div.bet-row",
    "bet_title": ".bet-title",
    "bet_odds": ".bet-odds",
    "place_button": ".place-bet-btn",
    "confirm_modal": "div.confirm-modal",
    "confirm_button": "button.confirm",
}



# Driver settings
HEADLESS = False
IMPLICIT_WAIT = 5

# Betting settings
STAKE_AMOUNT = 0.0
ACCUMULATED_STAKE = 0.0
MAX_BETS_PER_CARD = 6
CURRENT_BET_ATTEMPTS = 0
MAX_BET_COUNT = 4 # low rn for testing purposes

# Allowed betting regions/leagues
ALLOWED_BETS = [
    "Germany - BBL",
    "Brazil - Brasileirao Serie A",
    "NCAAB",
    "NCAA",
    "Sweden - Allsvenskan",
    "NBA",
    "Netherlands - Eerste Divisie",
    "International Tournaments - Euro Hockey Tour",
    "Portugal - Primeira Liga",
    "France - Ligue 1",
    "France - Elite",
    "France - Coupe de France",
    "Conference League",
    "Euroleague",
    "Italy - Lega A",
    "Italy - Lega A Basketball",
    "Champions League",
    "AHL",
    "WTA125 - Austin",
    "NHL",
    "EuroCup",
    "FIBA Europe Cup",
    "Germany - Bundesliga",
    "England - FA Cup",
    "England - The championship",
    "Spain - La Liga 2",
    "Spain - La Liga",
    "Denmark - Superligaen",
    "Denmark - Basketligaen",
    "Germany - Bundesliga (W)",
    "United Kingdom - Super League Basketball",
    "Spain - Copa del Rey",
    "England - EFL Cup",
    "Finland - Liiga",
    "Netherlands - KNVB Beker",
    "FIBA Europe Cup",
    "Denmark - 1st Division",
    "Finland - Korisliiga",
    "Belgium - Jupiler Pro League",
    "Poland - I Liga",
    "ATP - Next Gen Finals",
    "Spain - Liga ACB"
]

DENIED_BETS = [
    "Hungary - NB 1",
    "Peru - Liga 1",
    "Finland - Veikkausliiga",
    "UEFA Championship Qualification U21",
    "United Arab Emirates - Arabian Gulf League",
    "Turkey - Süper Lig",
    "China - CBA",
    "Switzerland - Super League"
]