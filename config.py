import logging
import os

import discord
from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("egyptair-bot")

# ==========================================================
# BOT
# ==========================================================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")

if not DISCORD_TOKEN:
    logger.warning(
        "DISCORD_TOKEN is not set. Please add it to your environment "
        "or .env file before starting the bot."
    )

# Kept for backwards compatibility with any code still referencing TOKEN.
TOKEN = DISCORD_TOKEN

COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")

INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True
INTENTS.guilds = True

GUILD_ID = 1363962490542620805

# ==========================================================
# CHANNELS
# ==========================================================

DEPARTURE_CHANNEL_ID = 1533788808510963763

TICKET_CATEGORY_ID = 1533790870380347463

CLOSED_TICKET_LOG_CHANNEL_ID = 1533791496573030460

# ==========================================================
# ROLES
# ==========================================================

OPERATIONS_ROLE_ID = 1533790969697276004

MODMAIL_STAFF_ROLE_ID = 1533791008721076234

# ==========================================================
# BOT SETTINGS
# ==========================================================

DATABASE_NAME = "database.db"

TIMEZONE = "Africa/Cairo"

BOT_ACTIVITY = "EgyptAir"

AIRLINE_NAME = "EgyptAir"

AIRLINE_SHORT = "MS"

COUNTRY = "Egypt"

COUNTRY_FLAG = "🇪🇬"

# ==========================================================
# EMBED
# ==========================================================

EMBED_COLOR = 0x002F6C

FOOTER_TEXT = "EgyptAir Customer Core"

# ==========================================================
# EMOJIS
# ==========================================================

NOTIFICATION = "<:Notification:1533792741903962112>"

INFORMATION = "<:Information:1533792771259760691>"

TICK = "<:Tick:1533787700459733062>"

CROSS = "<:Cross:1533787729198841866>"

DEVELOPMENT = "<:Development:1533784618556461086>"

PERSONNEL = "<:Personnel:1533785053220438146>"

FOLDER = "<:Folder:1533784800408764517>"

NETWORK = "<:Network:1533784832427954256>"

SCHEDULE = "<:Schedule:1533784526017396746>"

ANNOUNCE = "<:Announce:1533784495713550418>"

FLAG = "<:Flag:1533790147831795754>"

LOCK = "<:Lock:1533792193846841457>"

UNLOCK = "<:Unlock:1533792215363489944>"

TAIL = "<:tail:1533789675276210217>"

# ==========================================================
# MODMAIL
# ==========================================================

MODMAIL_WELCOME = (
    "Welcome aboard EgyptAir! 🇪🇬\n\n"
    "Thank you for contacting EgyptAir Customer Support.\n"
    "Please describe your issue below and a member of our team "
    "will assist you as soon as possible."
)

TICKET_CLOSED_MESSAGE = (
    "Your EgyptAir support ticket has now been closed.\n"
    "Thank you for contacting EgyptAir."
)

# ==========================================================
# FLIGHTS
# ==========================================================

DEFAULT_FLIGHT_DURATION = 60  # Minutes

MAX_FLIGHT_DURATION = 60
