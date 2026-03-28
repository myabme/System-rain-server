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

# قاموس لحفظ الدعوات
invites = {}

@client.event
async def on_ready():
    # تحديث كاش الدعوات لكل السيرفرات عند التشغيل
    for guild in client.guilds:
        try:
            invites[guild.id] = await guild.invites()
        except:
            pass
    print(f"✅ سيستم Rain جاهز وشغال لعيون فهد!")

@client.event
async def on_member_join(member):
    channel = client.get_channel(WELCOME_CHANNEL_ID)
    if not channel: return

    # ننتظر ثانية وحدة عشان الديسكورد يحدّث بيانات الـ Invite
    await asyncio.sleep(1)
    
    inviter_mention = "غير معروف"
    
    try:
        # إذا كان اللي دخل "بوت"، فاللي دخله هو الشخص اللي سوى له أيزورايز
        if member.bot:
            async for entry in member.guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1):
                inviter_mention = entry.user.mention
        else:
            # إذا كان شخص عادي، نقارن الدعوات القديمة بالجديدة
            invites_before = invites.get(member.guild.id, [])
            invites_after = await member.guild.invites()
            invites[member.guild.id] = invites_after

            for invite in invites_before:
                for new_invite in invites_after:
                    if invite.code == new_invite.code and invite.uses < new_invite.uses:
                        inviter_mention = invite.inviter.mention
                        break
    except Exception as e:
        print(f"خطأ في التتبع: {e}")

    # رسالة الترحيب العادية لعيون فهد
    welcome_msg = f"*hey : {member.mention}*\n*by : {inviter_mention}*"
    await channel.send(welcome_msg)

# --- نظام الأوامر بدون ! (تكتب الكلمة وبس) ---
@client.event
async def on_message(message):
    if message.author == client.user: return
    
    content = message.content.split()
    if not content: return
    cmd = content[0]

    # مسح الشات
    if cmd == "مسح" and message.author.guild_permissions.manage_messages:
        amount = int(content[1]) if len(content) > 1 else 10
        await message.channel.purge(limit=amount + 1)
        await message.channel.send(f"🧹 تم المسح لعيون فهد.", delete_after=3)

    # بنعالي (بان)
    if cmd == "بنعالي" and message.author.guild_permissions.ban_members:
        member = message.mentions[0] if message.mentions else None
        if member:
            await member.ban()
            await message.channel.send(f"💀 تم إعطاء {member.mention} بنعالي لعيون فهد.")

    # طرد (كيك)
    if cmd == "طرد" and message.author.guild_permissions.kick_members:
        member = message.mentions[0] if message.mentions else None
        if member:
            await member.kick()
            await message.channel.send(f"🚪 تم طرد {member.mention} لعيون فهد.")

    # مزعج (تايم أوت)
    if cmd == "مزعج" and message.author.guild_permissions.moderate_members:
        member = message.mentions[0] if message.mentions else None
        time = int(content[2]) if len(content) > 2 else 10
        if member:
            await member.timeout(datetime.timedelta(minutes=time))
            await message.channel.send(f"⏳ {member.mention} صار مزعج لعيون فهد.")

    # انطق (فك التايم أوت)
    if cmd == "انطق" and message.author.guild_permissions.moderate_members:
        member = message.mentions[0] if message.mentions else None
        if member:
            await member.timeout(None)
            await message.channel.send(f"🔊 {member.mention} انطق لعيون فهد.")

    # ر (رتبة)
    if cmd == "ر" and message.author.guild_permissions.manage_roles:
        member = message.mentions[0] if message.mentions else None
        role = message.role_mentions[0] if message.role_mentions else None
        if member and role:
            if role in member.roles:
                await member.remove_roles(role)
                await message.channel.send(f"✅ سحبنا {role.name} من {member.display_name} لعيون فهد.")
            else:
                await member.add_roles(role)
                await message.channel.send(f"✅ عطينا {role.name} لـ {member.display_name} لعيون فهد.")

    await client.process_commands(message)

# --- أمر المساعدة ---
@client.command(name="مساعدة")
async def help_cmd(ctx):
    embed = discord.Embed(title="قائمة أوامر Rain", color=BLACK_COLOR)
    embed.add_field(name="الأوامر (بدون !)", value="""
`بنعالي @الشخص` - حظر نهائي
`طرد @الشخص` - طرد
`مزعج @الشخص الوقت` - إسكات مؤقت
`انطق @الشخص` - فك الإسكات
`مسح العدد` - مسح الشات
`ر @الشخص @الرتبة` - سحب أو إعطاء رتبة
    """, inline=False)
    embed.set_footer(text="Developed by Wilked")
    await ctx.send(embed=embed)

# تشغيل البوت بالتوكن اللي في ريلوي
token = os.getenv('DISCORD_TOKEN')
client.run(token)
