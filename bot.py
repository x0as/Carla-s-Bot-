import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
import threading
import os
import random
from dotenv import load_dotenv
import datetime

# 🌐 Flask Web Server
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=8080)

# 🔐 Load Token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 🤖 Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=",", intents=intents)
tree = bot.tree

# 🧵 Start Flask in a separate thread
threading.Thread(target=run_web).start()

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    await tree.sync()

# 🛡️ Admin Check
def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator
    return commands.check(predicate)

# ⚙️ Basic Commands
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
async def embed(ctx, title, *, description):
    em = discord.Embed(title=title, description=description, color=discord.Color.blue())
    await ctx.send(embed=em)

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
@app_commands.checks.has_permissions(administrator=True)
async def slash_say(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

@tree.command(name="embed", description="Send an embed")
@app_commands.checks.has_permissions(administrator=True)
async def slash_embed(interaction: discord.Interaction, title: str, description: str):
    em = discord.Embed(title=title, description=description, color=discord.Color.green())
    await interaction.response.send_message(embed=em)

# 🚀 Run Bot
bot.run(TOKEN)
