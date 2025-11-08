import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
import threading
import os
import random
import datetime
import requests
import time

# 🌐 Flask Web Server
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/favicon.ico")
def favicon():
    return '', 204  # Prevent 404 spam

def run_web():
    app.run(host="0.0.0.0", port=8080)

# 🔁 Keepalive Ping to Render
def keep_alive():
    def ping():
        while True:
            try:
                requests.get("https://carla-s-bot.onrender.com")
            except:
                pass
            time.sleep(600)  # every 10 minutes
    threading.Thread(target=ping).start()

# 🔐 Load Token from environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

# 🤖 Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=",", intents=intents)
tree = bot.tree

# 🧵 Start Flask and Keepalive Threads
threading.Thread(target=run_web).start()
keep_alive()

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    tree.clear_commands(guild=None)
    await tree.sync()
    print("Slash commands refreshed.")

# 🛡️ Admin Check (includes user ID 843061674378002453)
def is_admin():
    async def predicate(ctx):
        return (
            ctx.author.guild_permissions.administrator
            or ctx.author.id == 843061674378002453
        )
    return commands.check(predicate)

def slash_admin_check(interaction: discord.Interaction):
    return (
        interaction.user.guild_permissions.administrator
        or interaction.user.id == 843061674378002453
    )

# ⚠️ Global Error Handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Unknown command. Type `,help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Missing arguments. Check `,help` for correct usage.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("🚫 You don't have permission to use this command.")
    else:
        await ctx.send("⚠️ An error occurred while processing the command.")
        raise error

# 📘 Help Command
@bot.command()
async def help(ctx):
    help_text = """
**📘 Bot Commands Guide**

**General Commands:**
- `,ping` — Check bot latency
- `,afk` — Mark yourself as AFK
- `,eightball <question>` — Ask the magic 8-ball
- `,say <message>` — Make the bot say something (admin only)
- `,embed <title> <message>` — Send an embed (admin only)
- `,status <type> <message>` — Change bot status (admin only)

**Moderation Commands (admin only):**
- `,kick <@user> [reason]` — Kick a user
- `,ban <@user> [reason]` — Ban a user
- `,timeout <@user> <seconds>` — Timeout a user

**Role Management (admin only):**
- `,addrole <@user> <@role>` — Add a role to a user
- `,removerole <@user> <@role>` — Remove a role from a user

**Slash Commands:**
All of the above are also available as `/commands` with autocomplete and cleaner UI.
"""
    await ctx.send(help_text)

# ⚙️ Basic Prefix Commands
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command()
async def afk(ctx):
    await ctx.send(f"{ctx.author.mention} is now AFK.")

@bot.command()
async def eightball(ctx, *, question):
    responses = ["Yes", "No", "Maybe", "Definitely", "Ask again later"]
    await ctx.send(f"🎱 {random.choice(responses)}")

@bot.command()
@is_admin()
async def say(ctx, *, message):
    await ctx.send(message)

@bot.command()
@is_admin()
async def embed(ctx, title: str, *, description: str):
    try:
        em = discord.Embed(title=title, description=description, color=discord.Color.blue())
        await ctx.send(embed=em)
    except Exception as e:
        await ctx.send("⚠️ Failed to send embed. Check your formatting and permissions.")
        print(f"Embed error: {e}")

@bot.command()
@is_admin()
async def status(ctx, type: str, *, message: str):
    type = type.lower()
    activity = None
    if type == "playing":
        activity = discord.Game(name=message)
    elif type == "watching":
        activity = discord.Activity(type=discord.ActivityType.watching, name=message)
    elif type == "listening":
        activity = discord.Activity(type=discord.ActivityType.listening, name=message)
    elif type == "competing":
        activity = discord.Activity(type=discord.ActivityType.competing, name=message)
    else:
        await ctx.send("❌ Invalid type. Use: playing, watching, listening, or competing.")
        return
    await bot.change_presence(activity=activity)
    await ctx.send(f"✅ Status updated to **{type.title()} {message}**")

# 🔨 Role Management
@bot.command()
@is_admin()
async def addrole(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"✅ Added {role.name} to {member.mention}")

@bot.command()
@is_admin()
async def removerole(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"❌ Removed {role.name} from {member.mention}")

# 🚫 Moderation
@bot.command()
@is_admin()
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} was kicked. Reason: {reason}")

@bot.command()
@is_admin()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} was banned. Reason: {reason}")

@bot.command()
@is_admin()
async def timeout(ctx, member: discord.Member, seconds: int):
    until = discord.utils.utcnow() + datetime.timedelta(seconds=seconds)
    await member.timeout(until)
    await ctx.send(f"{member.mention} is timed out for {seconds} seconds.")

# 🧵 Slash Commands
@tree.command(name="ping", description="Check bot latency")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")

@tree.command(name="say", description="Say something as the bot")
@app_commands.check(slash_admin_check)
async def slash_say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

@tree.command(name="embed", description="Send an embed")
@app_commands.check(slash_admin_check)
async def slash_embed(interaction: discord.Interaction, title: str, description: str):
    try:
        em = discord.Embed(title=title, description=description, color=discord.Color.green())
        await interaction.response.send_message(embed=em)
    except Exception as e:
        await interaction.response.send_message("⚠️ Failed to send embed.", ephemeral=True)
        print(f"Slash embed error: {e}")

@tree.command(name="status", description="Change the bot's status")
@app_commands.describe(type="Type: playing, watching, listening, competing", message="Status message")
@app_commands.check(slash_admin_check)
async def slash_status(interaction: discord.Interaction, type: str, message: str):
    type = type.lower()
    activity = None
    if type == "playing":
        activity = discord.Game(name=message)
    elif type == "watching":
        activity = discord.Activity(type=discord.ActivityType.watching, name=message)
    elif type == "listening":
        activity = discord.Activity(type=discord.ActivityType.listening, name=message)
    elif type == "competing":
        activity = discord.Activity(type=discord.ActivityType.competing, name=message)
    else:
        await interaction.response.send_message("❌ Invalid type. Use: playing, watching, listening, or competing.", ephemeral=True)
        return
    await bot.change_presence(activity=activity)
    await interaction.response.send_message(f"✅ Status updated to **{type.title()} {message}**")

# 🚀 Run Bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ DISCORD_TOKEN environment variable not set.")
