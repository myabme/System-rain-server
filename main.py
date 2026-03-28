import discord
from discord.ext import commands
import json
import os
import datetime

# --- الإعدادات ---
intents = discord.Intents.all() # لازم تفعل الـ Intents من صفحة المطورين (Discord Developer Portal)
client = commands.Bot(command_prefix="!", intents=intents)

BLACK_COLOR = 0x000001 # لون أسود فخم

# ملف لحفظ بيانات الترحيب
DATA_FILE = "welcome_data.json"

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# --- أوامر الإدارة (بالعربي) ---

@client.command(name="باند")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    embed = discord.Embed(description=f"✅ تم طرد {member.mention} نهائياً (باند).", color=BLACK_COLOR)
    await ctx.send(embed=embed)

@client.command(name="كيك")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    embed = discord.Embed(description=f"✅ تم طرد {member.mention} من السيرفر.", color=BLACK_COLOR)
    await ctx.send(embed=embed)

@client.command(name="اسكت") # ميوت (إخفاء الشات عنه)
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
    overwrite = ctx.channel.overwrites_for(member)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(member, overwrite=overwrite)
    embed = discord.Embed(description=f"🔇 {member.mention} صار عليه ميوت في هذا الروم.", color=BLACK_COLOR)
    await ctx.send(embed=embed)

@client.command(name="تكلم") # فك الميوت
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    overwrite = ctx.channel.overwrites_for(member)
    overwrite.send_messages = None
    await ctx.channel.set_permissions(member, overwrite=overwrite)
    embed = discord.Embed(description=f"🔊 {member.mention} يقدر يتكلم الحين.", color=BLACK_COLOR)
    await ctx.send(embed=embed)

@client.command(name="تايم_اوت")
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int, *, reason=None):
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    embed = discord.Embed(description=f"⏳ تم إعطاء {member.mention} وقت مستقطع لمدة {minutes} دقيقة.", color=BLACK_COLOR)
    await ctx.send(embed=embed)

@client.command(name="تغيير_اسم")
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, new_name):
    await member.edit(nick=new_name)
    embed = discord.Embed(description=f"✅ تم تغيير اسم {member.mention} إلى **{new_name}**", color=BLACK_COLOR)
    await ctx.send(embed=embed)

@client.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    embed = discord.Embed(description=f"🧹 تم مسح {amount} رسالة.", color=BLACK_COLOR)
    await ctx.send(embed=embed, delete_after=5)

# --- نظام الترحيب المطور ---

@client.command(name="ترحيب")
@commands.has_permissions(administrator=True)
async def set_welcome(ctx, *, message):
    data = load_data()
    data[str(ctx.guild.id)] = {
        "message": message,
        "channel_id": ctx.channel.id
    }
    save_data(data)
    embed = discord.Embed(description=f"✅ تم تعيين رسالة الترحيب في هذا الروم:\n**{message}**", color=BLACK_COLOR)
    await ctx.send(embed=embed)

@client.event
async def on_member_join(member):
    data = load_data()
    guild_data = data.get(str(member.guild.id))
    if guild_data:
        channel = member.guild.get_channel(guild_data["channel_id"])
        if channel:
            msg = guild_data["message"].replace("[user]", member.mention).replace("[server]", member.guild.name)
            embed = discord.Embed(title="ترحيب جديد", description=msg, color=BLACK_COLOR)
            embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
            await channel.send(embed=embed)

@client.event
async def on_ready():
    print(f"✅ سيستم الإدارة جاهز باسم: {client.user}")

token = os.getenv('DISCORD_TOKEN')
client.run(token)
