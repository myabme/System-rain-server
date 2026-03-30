import discord
from discord.ext import commands
import datetime
import os
import asyncio

# --- الإعدادات الأساسية لعيون فهد ---
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

BLACK_COLOR = 0x000001
WELCOME_CHANNEL_ID = 1453704693770616904 
ADMIN_ROLE_ID = 123456789012345678  # <--- حط هنا آيدي الرتبة اللي تبيها تستخدم الأوامر

invites = {}

@client.event
async def on_ready():
    print(f"✅ سيستم Rain جاهز لعيون فهد!")

# --- نظام الأوامر المطور ---
@client.event
async def on_message(message):
    if message.author == client.user: return
    
    content = message.content.split()
    if not content: return
    cmd = content[0]
    
    # التحقق هل العضو إداري أو عنده الرتبة الخاصة
    is_admin = message.author.guild_permissions.administrator or discord.utils.get(message.author.roles, id=ADMIN_ROLE_ID)

    # 1. أمر بنعالي (بان)
    if cmd == "بنعالي":
        if not is_admin: return
        if not message.mentions:
            return await message.reply("⚠️ **لازم تمنشن الشخص!**\nمثال: `بنعالي @user`")
        
        member = message.mentions[0]
        try:
            await member.ban(reason="بنعالي لعيون فهد")
            await message.channel.send(f"💀 تم إعطاء {member.mention} بنعالي لعيون فهد.")
        except:
            await message.channel.send("❌ ما أقدر أطرد هذا الشخص (رتبته أعلى مني).")

    # 2. أمر طرد (كيك)
    if cmd == "طرد":
        if not is_admin: return
        if not message.mentions:
            return await message.reply("⚠️ **لازم تمنشن الشخص!**\nمثال: `طرد @user`")
        
        member = message.mentions[0]
        try:
            await member.kick()
            await message.channel.send(f"🚪 تم طرد {member.mention} لعيون فهد.")
        except:
            await message.channel.send("❌ فشل الطرد، تأكد من الصلاحيات.")

    # 3. أمر ر (رتبة)
    if cmd == "ر":
        if not is_admin: return
        if not message.mentions or not message.role_mentions:
            return await message.reply("⚠️ **نقص في الأمر!**\nمثال: `ر @user @role`")
        
        member = message.mentions[0]
        role = message.role_mentions[0]
        try:
            if role in member.roles:
                await member.remove_roles(role)
                await message.channel.send(f"✅ سحبنا {role.name} من {member.mention} لعيون فهد.")
            else:
                await member.add_roles(role)
                await message.channel.send(f"✅ عطينا {role.name} لـ {member.mention} لعيون فهد.")
        except:
            await message.channel.send("❌ ما أقدر أعدل رتب هذا الشخص.")

    # 4. أمر مزعج (تايم أوت)
    if cmd == "مزعج":
        if not message.author.guild_permissions.moderate_members: return
        if not message.mentions:
            return await message.reply("⚠️ **يا غالي منشن الشخص!**\nمثال: `مزعج @user 10` (الرقم هو الدقائق)")
        
        member = message.mentions[0]
        time_mins = int(content[2]) if len(content) > 2 and content[2].isdigit() else 10
        try:
            await member.timeout(datetime.timedelta(minutes=time_mins))
            await message.channel.send(f"⏳ {member.mention} انصك مزعج لعيون فهد لمدة {time_mins} دقيقة.")
        except:
            await message.channel.send("❌ ما أقدر أعطي تايم أوت لهذا الشخص.")

    await client.process_commands(message)

token = os.getenv('DISCORD_TOKEN')
client.run(token)
