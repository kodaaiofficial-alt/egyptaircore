"""
Discord bot for Roblox game operations.

Provides simple operational commands: a health-check ping, modmail
ticket creation, event announcement cards, and Roblox server unlock
announcements.
"""

import logging
import os
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer

import discord
from discord.ext import commands

import config

logger = logging.getLogger("discord-bot")


class OperationsBot(commands.Bot):
    """Bot subclass with lifecycle hooks."""

    def __init__(self):
        super().__init__(
            command_prefix=config.COMMAND_PREFIX,
            intents=config.INTENTS,
            help_command=commands.DefaultHelpCommand(),
        )

    async def setup_hook(self):
        logger.info("Bot setup complete. Prefix: %s", config.COMMAND_PREFIX)


bot = OperationsBot()


# ==========================================================
# EVENTS
# ==========================================================

@bot.event
async def on_ready():
    logger.info("Logged in as %s (ID: %s)", bot.user, bot.user.id if bot.user else "unknown")
    logger.info("Connected to %d guild(s).", len(bot.guilds))

    try:
        await bot.change_presence(activity=discord.Game(name=config.BOT_ACTIVITY))
    except Exception:
        logger.exception("Failed to set bot presence.")

    logger.info("Bot is ready.")


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{config.CROSS} Missing required argument: `{error.param.name}`.")
        return

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{config.CROSS} You do not have permission to run this command.")
        return

    if isinstance(error, commands.MissingRole):
        await ctx.send(f"{config.CROSS} You do not have the required role to run this command.")
        return

    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send(f"{config.CROSS} This command can only be used in a server.")
        return

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"{config.CROSS} This command is on cooldown. Try again in {error.retry_after:.1f}s.")
        return

    logger.error("Unhandled command error in '%s': %s", ctx.command, error)
    traceback.print_exception(type(error), error, error.__traceback__)

    try:
        await ctx.send(f"{config.CROSS} An unexpected error occurred while running that command.")
    except discord.HTTPException:
        logger.exception("Failed to notify user of command error.")


@bot.event
async def on_error(event_method: str, *args, **kwargs):
    logger.error("Unhandled exception in event '%s'", event_method)
    logger.error(traceback.format_exc())


# ==========================================================
# PING
# ==========================================================

@bot.command(name="ping")
async def ping(ctx: commands.Context):
    """Check that the bot is alive and measure latency."""
    latency_ms = round(bot.latency * 1000)
    await ctx.send(f"{config.TICK} Pong! Latency: {latency_ms}ms")


# ==========================================================
# MODMAIL
# ==========================================================

@bot.command(name="modmail")
@commands.guild_only()
async def modmail(ctx: commands.Context, *, message: str = None):
    """Create a modmail support ticket for the requesting member."""
    if not message:
        await ctx.send(f"{config.CROSS} Please describe your issue, e.g. `!modmail I need help.`")
        return

    guild = ctx.guild

    if config.TICKET_CATEGORY_ID is None:
        await ctx.send(f"{config.CROSS} Modmail is not configured. Please contact staff directly.")
        return

    category = guild.get_channel(config.TICKET_CATEGORY_ID)

    if category is None or not isinstance(category, discord.CategoryChannel):
        logger.error("Ticket category %s not found or invalid.", config.TICKET_CATEGORY_ID)
        await ctx.send(f"{config.CROSS} Modmail is currently unavailable. Please contact staff directly.")
        return

    try:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        if config.MODMAIL_STAFF_ROLE_ID is not None:
            staff_role = guild.get_role(config.MODMAIL_STAFF_ROLE_ID)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{ctx.author.name}".lower().replace(" ", "-"),
            category=category,
            overwrites=overwrites,
            topic=f"Modmail ticket opened by {ctx.author} ({ctx.author.id})",
        )

        embed = discord.Embed(
            title="New Support Ticket",
            description=config.MODMAIL_WELCOME,
            color=config.EMBED_COLOR,
        )
        embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
        embed.add_field(name="Message", value=message, inline=False)
        embed.set_footer(text=config.FOOTER_TEXT)

        await ticket_channel.send(embed=embed)
        await ctx.send(f"{config.TICK} Your ticket has been created: {ticket_channel.mention}")

        logger.info("Modmail ticket %s created by %s (%s).", ticket_channel.name, ctx.author, ctx.author.id)

    except discord.Forbidden:
        logger.exception("Missing permissions to create modmail ticket.")
        await ctx.send(f"{config.CROSS} I don't have permission to create a ticket channel.")
    except discord.HTTPException:
        logger.exception("Failed to create modmail ticket due to a Discord API error.")
        await ctx.send(f"{config.CROSS} Something went wrong while creating your ticket. Please try again.")


# ==========================================================
# EVENT CARDS
# ==========================================================

@bot.command(name="eventcard")
@commands.guild_only()
async def eventcard(ctx: commands.Context, title: str, *, description: str):
    """Create and post an event announcement card."""
    if config.OPERATIONS_ROLE_ID is not None:
        role = ctx.guild.get_role(config.OPERATIONS_ROLE_ID)
        if role is None or role not in ctx.author.roles:
            await ctx.send(f"{config.CROSS} You do not have permission to run this command.")
            return

    try:
        embed = discord.Embed(
            title=f"{config.ANNOUNCE} {title}",
            description=description,
            color=config.EMBED_COLOR,
        )
        embed.set_footer(text=config.FOOTER_TEXT)
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)
        logger.info("Event card '%s' posted by %s.", title, ctx.author)

    except discord.HTTPException:
        logger.exception("Failed to post event card '%s'.", title)
        await ctx.send(f"{config.CROSS} Failed to post the event card. Please try again.")


# ==========================================================
# SERVER UNLOCK
# ==========================================================

@bot.command(name="serverunlock")
@commands.guild_only()
async def serverunlock(ctx: commands.Context, server_name: str, *, notes: str = "No additional notes."):
    """Announce that a Roblox game server has unlocked."""
    if config.OPERATIONS_ROLE_ID is not None:
        role = ctx.guild.get_role(config.OPERATIONS_ROLE_ID)
        if role is None or role not in ctx.author.roles:
            await ctx.send(f"{config.CROSS} You do not have permission to run this command.")
            return

    try:
        embed = discord.Embed(
            title=f"{config.UNLOCK} Server Unlocked",
            description=f"**{server_name}** is now unlocked and open for join.",
            color=config.EMBED_COLOR,
        )
        embed.add_field(name="Notes", value=notes, inline=False)
        embed.set_footer(text=config.FOOTER_TEXT)
        embed.timestamp = discord.utils.utcnow()

        await ctx.send(embed=embed)
        logger.info("Server unlock announcement posted for '%s' by %s.", server_name, ctx.author)

    except discord.HTTPException:
        logger.exception("Failed to post server unlock announcement for '%s'.", server_name)
        await ctx.send(f"{config.CROSS} Failed to post the server unlock announcement. Please try again.")


# ==========================================================
# HEALTHCHECK SERVER
# ==========================================================
# Railway (and similar platforms) expect the process to stay alive and,
# optionally, respond to HTTP healthchecks. This lightweight server lets
# the deployment report healthy even while we are waiting for a valid
# DISCORD_TOKEN to be configured, or if the bot fails to log in.

class _HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format, *args):  # noqa: A002 - silence default logging
        pass


def _start_healthcheck_server():
    port = int(os.getenv("PORT", "8080"))
    try:
        server = HTTPServer(("0.0.0.0", port), _HealthCheckHandler)
    except OSError:
        logger.warning("Could not bind healthcheck server on port %s.", port)
        return

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info("Healthcheck server listening on port %s.", port)


def _wait_forever_for_token():
    """Keep the process alive so the deployment doesn't restart-loop."""
    logger.warning(
        "Waiting for DISCORD_TOKEN to be set. Set the DISCORD_TOKEN "
        "environment variable (Railway > Variables) and redeploy or "
        "restart the service to start the bot."
    )
    while not config.DISCORD_TOKEN:
        time.sleep(30)
        # Re-read in case the environment was updated without a restart.
        config.DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")

    logger.info("DISCORD_TOKEN detected. Starting bot.")
    _run_bot()


def _run_bot():
    try:
        bot.run(config.DISCORD_TOKEN, log_handler=None)
    except discord.LoginFailure:
        logger.error(
            "Failed to log in: DISCORD_TOKEN is invalid. The process will "
            "stay alive; update DISCORD_TOKEN with a valid value and "
            "restart the service."
        )
        while True:
            time.sleep(3600)
    except Exception:
        logger.exception("Bot crashed with an unexpected error.")
        raise


# ==========================================================
# ENTRYPOINT
# ==========================================================

def main():
    _start_healthcheck_server()

    if not config.DISCORD_TOKEN:
        _wait_forever_for_token()
        return

    _run_bot()


if __name__ == "__main__":
    main()
