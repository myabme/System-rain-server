import discord
from discord.ext import commands
import datetime
import os

# --- الإعدادات ---
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

BLACK_COLOR = 0x000001
WELCOME_CHANNEL_ID = 1453704693770616904 

invites = {}

@client.event
async def on_ready():
    for guild in client.guilds:
        try: invites[guild.id] = await guild.invites()
        except: pass
    print(f"✅ سيستم Rain الخاص بـ أبو مشاري شغال!")

@client.event
async def on_member_join(member):
    channel = client.get_channel(WELCOME_CHANNEL_ID)
    if not channel: return
    invites_before = invites.get(member.guild.id, [])
    invites_after = await member.guild.invites()
    invites[member.guild.id] = invites_after
    inviter = "غير معروف"
    for invite in invites_before:
        for new_invite in invites_after:
            if invite.code == new_invite.code and invite.uses < new_invite.uses:
                inviter = invite.inviter.mention
                break
    embed = discord.Embed(description=f"**hey : {member.mention}**\n**by : {inviter}**", color=BLACK_COLOR)
    await channel.send(embed=embed)

# --- نظام الأوامر بدون بريفكس (تكتب الكلمة وبس) ---
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
        await message.channel.send(f"🧹 تم المسح لعيون أبو مشاري ({amount} رسالة).", delete_after=3)

    # بنعالي (بان)
    if cmd == "بنعالي" and message.author.guild_permissions.ban_members:
        member = message.mentions[0] if message.mentions else None
        if member:
            await member.ban()
            await message.channel.send(embed=discord.Embed(description=f"💀 تم إعطاء {member.mention} بنعالي.", color=BLACK_COLOR))

    # طرد (كيك)
    if cmd == "طرد" and message.author.guild_permissions.kick_members:
        member = message.mentions[0] if message.mentions else None
        if member:
            await member.kick()
            await message.channel.send(embed=discord.Embed(description=f"🚪 تم طرد {member.mention}.", color=BLACK_COLOR))

    # مزعج (تايم أوت)
    if cmd == "مزعج" and message.author.guild_permissions.moderate_members:
        member = message.mentions[0] if message.mentions else None
        time = int(content[2]) if len(content) > 2 else 10
        if member:
            await member.timeout(datetime.timedelta(minutes=time))
            await message.channel.send(embed=discord.Embed(description=f"⏳ {member.mention} صار مزعج ({time}د).", color=BLACK_COLOR))

    # انطق (فك التايم أوت)
    if cmd == "انطق" and message.author.guild_permissions.moderate_members:
        member = message.mentions[0] if message.mentions else None
        if member:
            await member.timeout(None)
            await message.channel.send(embed=discord.Embed(description=f"🔊 {member.mention} انطق يا بطل.", color=BLACK_COLOR))

    # ر (رتبة)
    if cmd == "ر" and message.author.guild_permissions.manage_roles:
        member = message.mentions[0] if message.mentions else None
        role = message.role_mentions[0] if message.role_mentions else None
        if member and role:
            if role in member.roles:
                await member.remove_roles(role)
                await message.channel.send(f"✅ سحبنا {role.name} من {member.display_name}")
            else:
                await member.add_roles(role)
                await message.channel.send(f"✅ عطينا {role.name} لـ {member.display_name}")

    await client.process_commands(message)

# --- أمر المساعدة المحدث ---
@client.command(name="مساعدة")
async def help_cmd(ctx):
    embed = discord.Embed(title="قائمة أوامر Rain 🏴", color=BLACK_COLOR)
    embed.add_field(name="الأوامر (بدون !)", value="""
`بنعالي @الشخص` - حظر نهائي
`طرد @الشخص` - طرد
`مزعج @الشخص الوقت` - إسكات مؤقت
`انطق @الشخص` - فك الإسكات
`مسح العدد` - مسح الشات
`ر @الشخص @الرتبة` - سحب أو إعطاء رتبة
    """, inline=False)
    # التوقيع الخاص بك يا wilked
    embed.set_footer(text="Developed by Wilked")
    await ctx.send(embed=embed)

token = os.getenv('DISCORD_TOKEN')
client.run(token)
