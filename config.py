"""
Configuration for the Discord bot.

All configuration values are loaded from environment variables so the
bot can be safely configured per-deployment (e.g. via Railway variables)
without touching source code. Optional settings fall back to sensible
defaults and never raise on import, even if unset.
"""

import logging
import os
from typing import Optional

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

logger = logging.getLogger("discord-bot")


def _get_int_env(name: str) -> Optional[int]:
    """Safely parse an optional integer environment variable."""
    value = os.getenv(name)
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        logger.warning("Environment variable %s=%r is not a valid integer. Ignoring.", name, value)
        return None


# ==========================================================
# BOT CORE
# ==========================================================

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")

if not DISCORD_TOKEN:
    logger.warning(
        "DISCORD_TOKEN is not set. The bot will not attempt to log in to "
        "Discord until it is configured. Add DISCORD_TOKEN (or TOKEN) to "
        "your environment or .env file, then redeploy/restart the bot."
    )

COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")

INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.guilds = True

BOT_ACTIVITY = os.getenv("BOT_ACTIVITY", "!help")

# ==========================================================
# OPTIONAL FEATURE CONFIGURATION
# ==========================================================
# These are optional. If unset, the related commands will respond with a
# friendly message instead of failing.

# Category channel that new modmail ticket channels are created under.
TICKET_CATEGORY_ID = _get_int_env("TICKET_CATEGORY_ID")

# Role that gets access to modmail ticket channels in addition to the author.
MODMAIL_STAFF_ROLE_ID = _get_int_env("MODMAIL_STAFF_ROLE_ID")

# Role required to run staff-only commands (eventcard, serverunlock).
OPERATIONS_ROLE_ID = _get_int_env("OPERATIONS_ROLE_ID")

# ==========================================================
# EMBED / MESSAGE STYLING
# ==========================================================

EMBED_COLOR = 0x5865F2

FOOTER_TEXT = os.getenv("FOOTER_TEXT", "Operations Bot")

TICK = "✅"
CROSS = "❌"
ANNOUNCE = "📢"
UNLOCK = "🔓"

MODMAIL_WELCOME = (
    "Thanks for reaching out!\n\n"
    "A member of staff will be with you shortly. "
    "Please describe your issue in as much detail as possible."
)
