import discord
from discord.ext import commands
from discord import ui
import os
import json
import asyncio

# --- الإعدادات ---
intents = discord.Intents.all()
# جعلنا البريفكس فارغ تماماً عشان الكلمات تشتغل مباشرة
bot = commands.Bot(command_prefix="", intents=intents, help_command=None)

WELCOME_CHANNEL_ID = 1453704693770616904 
PERMS_FILE = "permissions.json"

def load_perms():
    if not os.path.exists(PERMS_FILE): return {}
    try:
        with open(PERMS_FILE, "r") as f: return json.load(f)
    except: return {}

def save_perms(perms):
    with open(PERMS_FILE, "w") as f: json.dump(perms, f)

def can_do(user, cmd_name):
    if user.guild_permissions.administrator: return True
    perms = load_perms().get(str(user.guild.id), {})
    for rid, cmds in perms.items():
        if any(r.id == int(rid) for r in user.roles) and cmd_name in cmds: return True
    return False

# --- نظام "قول" (مخفي وبدون ايمبد) ---
class SayModal(ui.Modal, title="اكتب رسالتك"):
    msg_content = ui.TextInput(label="الرسالة", style=discord.TextStyle.paragraph, required=True)
    async def on_submit(self, inter: discord.Interaction):
        view = ui.View()
        select = ui.ChannelSelect(placeholder="اختر الروم المراد الإرسال فيها...", channel_types=[discord.ChannelType.text])
        async def ch_callback(i: discord.Interaction):
            target = i.guild.get_channel(int(i.data['values'][0]))
            if target:
                await target.send(self.msg_content.value)
                await i.response.send_message(f"✅ أرسلتها في {target.mention}", ephemeral=True)
        select.callback = ch_callback
        view.add_item(select)
        await inter.response.send_message("ألحين حدد الروم من القائمة:", view=view, ephemeral=True)

# --- معالجة الأوامر (السرعة القصوى) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    content = message.content.strip().split()
    if not content: return
    cmd = content[0]

    # 1. قول
    if cmd == "قول" and can_do(message.author, "قول"):
        await message.delete()
        view = ui.View()
        btn = ui.Button(label="اضغط هنا لكتابة الرسالة", style=discord.ButtonStyle.secondary)
        async def s_cb(i): await i.response.send_modal(SayModal())
        btn.callback = s_cb
        view.add_item(btn)
        await message.channel.send("أمر قول (مخفي):", view=view, delete_after=10)

    # 2. اداره (اداره @رتبه)
    elif cmd == "اداره" and message.author.guild_permissions.administrator:
        await message.delete()
        if message.role_mentions:
            role = message.role_mentions[0]
            view = ui.View()
            for c in ["مسح", "بنعالي", "طرد", "ر", "قول", "اداره"]:
                b = ui.Button(label=c, custom_id=c, style=discord.ButtonStyle.primary)
                async def b_cb(i):
                    p = load_perms()
                    gid, rid = str(i.guild.id), str(role.id)
                    if gid not in p: p[gid] = {}
                    if rid not in p[gid]: p[gid][rid] = []
                    clicked = i.data['custom_id']
                    if clicked in p[gid][rid]: p[gid][rid].remove(clicked)
                    else: p[gid][rid].append(clicked)
                    save_perms(p)
                    await i.response.send_message(f"✅ تم تحديث {clicked} لـ {role.name}", ephemeral=True)
                b.callback = b_cb
                view.add_item(b)
            await message.channel.send(f"صلاحيات {role.name} (أزرار مخفية):", view=view, delete_after=20)

    # 3. مسح (مسح 10)
    elif cmd == "مسح" and can_do(message.author, "مسح"):
        await message.delete()
        try:
            limit = int(content[1]) if len(content) > 1 else 10
            await message.channel.purge(limit=limit)
            await message.channel.send(f"تم مسح {limit} رسالة.", delete_after=2)
        except: pass

    # 4. بنعالي (@منشن)
    elif cmd == "بنعالي" and can_do(message.author, "بنعالي"):
        if message.mentions:
            await message.delete()
            await message.mentions[0].ban(reason="لعيون فهد")
            await message.channel.send("تم الباند لعيون فهد.", delete_after=3)

    # 5. ر (@شخص @رتبه)
    elif cmd == "ر" and can_do(message.author, "ر"):
        if message.mentions and message.role_mentions:
            await message.delete()
            m, r = message.mentions[0], message.role_mentions[0]
            if r in m.roles: await m.remove_roles(r)
            else: await m.add_roles(r)
            await message.channel.send("تم تعديل الرتبة.", delete_after=2)

# --- ترحيب سريع ---
@bot.event
async def on_member_join(member):
    ch = bot.get_channel(WELCOME_CHANNEL_ID)
    if ch: await ch.send(f"hey : {member.mention}\nby : <@{member.guild.owner_id}>")

# تشغيل البوت
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
