import discord
from discord.ext import commands
import random
import asyncio
import os
from datetime import datetime, timezone
import io
import time

start_time = time.time()
last_gif_user = "None"

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)

######################################################

# Change the "Configuration" section below to customize the bot's behavior, including cooldowns, logging, and database management. 
# The bot is designed to be modular and easily adaptable to various use cases. 
# Make sure to replace placeholder IDs and links with your actual values for proper functionality.

#######################################################

# Configuration
ROLE_BYPASS_ID = 1234567891234567891 # Role ID that allows users to bypass the global cooldown
LOG_CHANNEL_ID = 12345678912345678912 # Channel ID for logging new GIF additions
COOLDOWN_TIME = 1500  # Change this to change global cooldown time (in seconds) - currently set to 25 minutes
GIF_FILE = "gif.txt" # Path to the GIF database file

last_global_use = {}

def get_gif_list():
    if not os.path.exists(GIF_FILE):
        with open(GIF_FILE, "w") as f: pass
        return []
    with open(GIF_FILE, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

class LinkButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="Official Website", url="https://exemple.com", style=discord.ButtonStyle.link))

@bot.event
async def on_ready():
    print(f'>>> System Status: ONLINE | Database: {len(get_gif_list())} GIFs')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=".help"))

@bot.command()
async def help(ctx):
    gif_count = len(get_gif_list())
    embed = discord.Embed(
        title="🛰️ System Control Center",
        description="Advanced Management Interface. Global cooldown is active.",
        color=0x2b2d31
    )
    embed.add_field(name="🛡️ `Admin`", value="`.say <text>` | `.clear <#>` | `.addgif <link>` | `.giflist`", inline=False)
    embed.add_field(name="🌐 `Info`", value=f"`.status` | `.socials`", inline=False)
    embed.add_field(name="🖼️ `Media`", value=f"`.gif` - Deploy random media\n*(Database: **{gif_count}** GIFs)*", inline=False)
    embed.set_footer(text="Bypass role users ignore the global 25m cooldown.")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def addgif(ctx, link: str):
    await ctx.message.delete()
    
    with open(GIF_FILE, "a") as f:
        f.write(f"\n{link}")
    
    current_gifs = len(get_gif_list())
    
    await ctx.send(embed=discord.Embed(description="✅ Media added to database.", color=0x43b581), delete_after=5)
    
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_embed = discord.Embed(
            title="📥 New GIF Added",
            description=f"A new GIF has been successfully indexed into the system.",
            color=0x5865f2,
            timestamp=datetime.now(timezone.utc)
        )
        log_embed.add_field(name="Total GIFs in Database", value=f"**{current_gifs}**", inline=True)
        log_embed.add_field(name="Added by", value=ctx.author.mention, inline=True)
        log_embed.set_footer(text="System Update")
        await log_channel.send(embed=log_embed)

@bot.command()
async def gif(ctx):
    global last_global_use
    
    try:
        await ctx.message.delete()
    except:
        pass

    has_bypass = any(role.id == ROLE_BYPASS_ID for role in ctx.author.roles)
    current_time = datetime.now(timezone.utc).timestamp()
    
    if not has_bypass and "global" in last_global_use:
        remaining = last_global_use["global"] + COOLDOWN_TIME - current_time
        if remaining > 0:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            err = discord.Embed(
                title="⏳ Global Cooldown Active",
                description=f"The system is recharging. Available in **{minutes}m {seconds}s** for standard users.",
                color=0xfaa61a
            )
            return await ctx.send(embed=err, delete_after=10)

    gifs = get_gif_list()
    if not gifs:
        return await ctx.send("⚠️ Database empty.", delete_after=5)

    async with ctx.typing():
        if not has_bypass:
            last_global_use["global"] = current_time

        selected_gif = random.choice(gifs)
        
        main_embed = discord.Embed(
            title="✨ Media Sequence Initiated",
            description=f"🖼️ [GIF not loading? (Click to view)]({selected_gif})",
            color=discord.Color.random(),
            timestamp=datetime.now(timezone.utc)
        )
        main_embed.set_image(url=selected_gif)
        main_embed.set_footer(text=f"Sequence initiated by {ctx.author.name}")
        
        await ctx.send(embed=main_embed)

        info_embed = discord.Embed(
            title="🌐 Media Hosting Information",
            description=(
                "This media sequence is powered by **exemple.com**.\n\n"
                "• **Provider:** exemple Cloud Services\n"
                "• **Status:** Secured & Encrypted\n"
                "• **Access:** Public Data Stream"
            ),
            color=0x0099ff
        )
        info_embed.set_footer(text="Data source: Internal Database")
        
        temp_msg = await ctx.send(embed=info_embed, view=LinkButton())
        
        await asyncio.sleep(10)
        try:
            await temp_msg.delete()
        except:
            pass

@bot.command()
@commands.has_permissions(administrator=True)
async def say(ctx, *, text: str):
    await ctx.message.delete()
    embed = discord.Embed(description=text, color=0x5865f2, timestamp=datetime.now(timezone.utc))
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, amount: int):
    await ctx.message.delete()
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(embed=discord.Embed(description=f"✅ Purged {len(deleted)} messages.", color=0x43b581), delete_after=3)

@bot.command()
async def giflist(ctx):
    has_bypass = any(role.id == ROLE_BYPASS_ID for role in ctx.author.roles)
    
    if not has_bypass:
        return await ctx.send("❌ You don't have permission to use this command.", delete_after=5)

    gifs = get_gif_list()
    if not gifs:
        return await ctx.send("⚠️ The database is empty.", delete_after=5)

    try:
        gif_content = "\n".join(gifs)
        file_data = io.BytesIO(gif_content.encode())
        file = discord.File(file_data, filename="gif_database.txt")
        
        embed = discord.Embed(
            title="📂 Full GIF Database",
            description=f"Attached is the complete list of your **{len(gifs)}** indexed GIFs.",
            color=0x5865f2,
            timestamp=datetime.now(timezone.utc)
        )
        
        await ctx.author.send(embed=embed, file=file)
        await ctx.send(f"✅ {ctx.author.mention}, I've sent the list to your DMs.", delete_after=5)
        
    except discord.Forbidden:
        await ctx.send(f"❌ {ctx.author.mention}, I can't send you DMs. Check your privacy settings.", delete_after=10)
        
@bot.command()
async def socials(ctx):
    embed = discord.Embed(
        title="🌐 Server Connect",
        description="Check out my official social media and projects below!",
        color=0x5865f2
    )
    embed.add_field(name="🔗 Website", value="[example.com](https://example.com)", inline=False)
    embed.add_field(name="🎬 YouTube", value="[@username](https://youtube.com/@username)", inline=True)
    embed.add_field(name="📱 TikTok", value="[@username](https://tiktok.com/@username)", inline=True)
    embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
    embed.set_footer(text="Stay connected for more updates!")
    await ctx.send(embed=embed)

@bot.command()
async def status(ctx):
    current_time = time.time()
    difference = int(current_time - start_time)
    hours, remainder = divmod(difference, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"

    gif_count = len(get_gif_list())
    
    embed = discord.Embed(
        title="📊 Bot System Analytics",
        color=0x2ecc71,
        timestamp=datetime.now(timezone.utc)
    )
    embed.add_field(name="📂 Database", value=f"**{gif_count}** GIFs Loaded", inline=True)
    embed.add_field(name="👤 Last Interaction", value=f"User: **{last_gif_user}**", inline=True)
    embed.add_field(name="⚡ Uptime", value=f"`{uptime_str}`", inline=False)
    embed.add_field(name="📡 Latency", value=f"`{round(bot.latency * 1000)}ms`", inline=True)
    embed.add_field(name="⚙️ Version", value="`v1.2-stable`", inline=True)
    
    embed.set_footer(text=f"System powered by {ctx.guild.name}")
    await ctx.send(embed=embed)

bot.run("YOUR_BOT_TOKEN_HERE") # CHANGE THIS TO YOUR BOT TOKEN
