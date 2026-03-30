import discord
from discord.ext import commands
import os
import asyncio

# --- الإعدادات الأساسية لعيون أبو مشاري ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents, help_command=None)

WELCOME_CHANNEL_ID = 1453704693770616904 

# --- معالجة الأوامر بالكلمات المباشرة ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    msg = message.content.strip().split()
    if not msg: return
    cmd = msg[0]

    # 1. مسح (مسح 10)
    if cmd == "مسح":
        if message.author.guild_permissions.manage_messages:
            await message.delete()
            num = int(msg[1]) if len(msg) > 1 else 10
            await message.channel.purge(limit=num)
            await message.channel.send(f"🧹 تم مسح {num} رسالة لعيون فهد.", delete_after=2)

    # 2. بنعالي (@منشن)
    elif cmd == "بنعالي":
        if message.author.guild_permissions.ban_members:
            if message.mentions:
                user = message.mentions[0]
                await message.delete()
                await user.ban(reason="بنعالي لعيون فهد")
                await message.channel.send(f"💀 {user.mention} بنعالي لعيون فهد.", delete_after=3)

    # 3. طرد (@منشن)
    elif cmd == "طرد":
        if message.author.guild_permissions.kick_members:
            if message.mentions:
                user = message.mentions[0]
                await message.delete()
                await user.kick(reason="طرد لعيون فهد")
                await message.channel.send(f"🚪 {user.mention} طرد لعيون فهد.", delete_after=3)

    # 4. ر (@شخص @رتبه)
    elif cmd == "ر":
        if message.author.guild_permissions.manage_roles:
            if message.mentions and message.role_mentions:
                await message.delete()
                member, role = message.mentions[0], message.role_mentions[0]
                if role in member.roles:
                    await member.remove_roles(role)
                    await message.channel.send(f"✅ تم سحب رتبة {role.name} من {member.mention}", delete_after=2)
                else:
                    await member.add_roles(role)
                    await message.channel.send(f"✅ تم إعطاء رتبة {role.name} لـ {member.mention}", delete_after=2)

    # 5. قفل (قفل الروم)
    elif cmd == "قفل":
        if message.author.guild_permissions.manage_channels:
            await message.delete()
            overwrite = message.channel.overwrites_for(message.guild.default_role)
            overwrite.send_messages = False
            await message.channel.set_permissions(message.guild.default_role, overwrite=overwrite)
            await message.channel.send("🔒 تم قفل الروم لعيون فهد.", delete_after=5)

    # 6. فتح (فتح الروم)
    elif cmd == "فتح":
        if message.author.guild_permissions.manage_channels:
            await message.delete()
            overwrite = message.channel.overwrites_for(message.guild.default_role)
            overwrite.send_messages = True
            await message.channel.set_permissions(message.guild.default_role, overwrite=overwrite)
            await message.channel.send("🔓 تم فتح الروم لعيون فهد.", delete_after=5)

    await bot.process_commands(message)

# --- نظام الترحيب ---
@bot.event
async def on_member_join(member):
    ch = bot.get_channel(WELCOME_CHANNEL_ID)
    if ch:
        await ch.send(f"hey : {member.mention}\nby : <@{member.guild.owner_id}>")

# تشغيل البوت بالتوكن حقك
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
