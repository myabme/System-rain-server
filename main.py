import discord
from discord.ext import commands
import json
import os
import datetime

# --- الإعدادات ---
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

# ملف حفظ الصلاحيات
DATA_FILE = "permissions.json"

def load_perms():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {"admin_roles": [], "can_purge": [], "can_ban": [], "can_role": []}

def save_perms(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

perms = load_perms()

@client.event
async def on_ready():
    # تغيير حالة البوت لـ Ráin Bot
    await client.change_presence(activity=discord.Game(name="Ráin Bot | لعيون فهد"))
    print(f"✅ {client.user.name} جاهز للتحكم الكامل!")

# --- أمر الموقع (باسم Ráin Bot) ---
@client.command(name="موقع")
async def site_link(ctx):
    embed = discord.Embed(
        title="🌐 Ráin Bot Dashboard",
        description="أهلاً بك في لوحة تحكم راين بوت\n\n[اضغط هنا لزيارة الموقع](https://example.com)", # استبدل الرابط برابط موقعك
        color=0x000001
    )
    embed.set_footer(text="Ráin Bot - Powered by Abu Meshari")
    await ctx.send(embed=embed)

# --- أمر الإدارة ---
@client.command(name="ادارة")
@commands.has_permissions(administrator=True)
async def admin_control(ctx, action=None, role: discord.Role=None, power=None):
    if not action or not role or not power:
        embed = discord.Embed(title="⚙️ Ráin Bot | لوحة التحكم", color=0x000001)
        embed.add_field(name="الأوامر:", value="`!ادارة اضافة @الرتبة النوع`", inline=False)
        embed.add_field(name="الأنواع:", value="`مسح` | `بند` | `رتب` | `كلها`", inline=False)
        embed.set_footer(text="Ráin Bot Management System")
        return await ctx.send(embed=embed)

    role_id = str(role.id)
    if action == "اضافة":
        if power == "مسح": perms["can_purge"].append(role_id)
        elif power == "بند": perms["can_ban"].append(role_id)
        elif power == "رتب": perms["can_role"].append(role_id)
        elif power == "كلها": perms["admin_roles"].append(role_id)
        save_perms(perms)
        await ctx.send(f"✅ **Ráin Bot:** تم إعطاء رتبة {role.name} صلاحية ({power})")

# --- نظام الأوامر السريعة (بدون !) ---
@client.event
async def on_message(message):
    if message.author == client.user: return
    
    content = message.content.split()
    if not content: return
    cmd = content[0]
    
    user_roles = [str(r.id) for r in message.author.roles]
    is_super_admin = any(r in perms["admin_roles"] for r in user_roles) or message.author.guild_permissions.administrator

    # أمر مسح
    if cmd == "مسح":
        if is_super_admin or any(r in perms["can_purge"] for r in user_roles):
            amount = int(content[1]) if len(content) > 1 and content[1].isdigit() else 10
            await message.channel.purge(limit=amount + 1)
            await message.channel.send(f"🧹 **Ráin Bot:** تم تنظيف الشات لعيون فهد.", delete_after=3)

    # أمر بنعالي
    if cmd == "بنعالي":
        if is_super_admin or any(r in perms["can_ban"] for r in user_roles):
            if not message.mentions:
                return await message.reply("⚠️ **Ráin Bot:** منشن الشخص! مثال: `بنعالي @user`")
            member = message.mentions[0]
            try:
                await member.ban(reason="بنعالي - Ráin Bot")
                await message.channel.send(f"💀 **Ráin Bot:** {member.mention} أكل بنعالي!")
            except: pass

    await client.process_commands(message)

token = os.getenv('DISCORD_TOKEN')
client.run(token)
