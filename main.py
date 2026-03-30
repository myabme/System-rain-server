import discord
from discord.ext import commands
from discord import ui
import os
import json
import asyncio

# --- الإعدادات الأساسية لعيون أبو مشاري ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents, help_command=None)

BLACK_COLOR = 0x000001
WELCOME_CHANNEL_ID = 1453704693770616904 
PERMS_FILE = "permissions.json"

# --- نظام حفظ الصلاحيات بأمان ---
def load_perms():
    if not os.path.exists(PERMS_FILE):
        with open(PERMS_FILE, "w") as f: json.dump({}, f)
        return {}
    try:
        with open(PERMS_FILE, "r") as f: return json.load(f)
    except: return {}

def save_perms(perms):
    try:
        with open(PERMS_FILE, "w") as f: json.dump(perms, f)
    except: pass

def can_do(user, cmd_name):
    if user.guild_permissions.administrator or user.id == user.guild.owner_id: return True
    perms = load_perms().get(str(user.guild.id), {})
    for rid, cmds in perms.items():
        if any(r.id == int(rid) for r in user.roles) and cmd_name in cmds: return True
    return False

# --- نافذة !قول (تكتب: قول) ---
class SayModal(ui.Modal, title="رسالة البوت"):
    text = ui.TextInput(label="وش تبيني أقول؟", style=discord.TextStyle.paragraph)
    async def on_submit(self, inter):
        try:
            view = ui.View()
            sel = ui.ChannelSelect(placeholder="اختر الروم...", channel_types=[discord.ChannelType.text])
            async def sel_cb(i):
                ch = i.guild.get_channel(int(i.data['values'][0]))
                if ch:
                    await ch.send(self.text.value)
                    await i.response.send_message("✅ تم الإرسال", ephemeral=True)
            sel.callback = sel_cb
            view.add_item(sel)
            await inter.response.send_message("الحين اختر الروم (مخفي):", view=view, ephemeral=True)
        except: pass

# --- لوحة التحكم (تكتب: اداره @رتبه) ---
class PermsView(ui.View):
    def __init__(self, role):
        super().__init__(timeout=None)
        self.role = role
        for c in ["مسح", "بنعالي", "طرد", "ر", "قول", "اداره"]:
            btn = ui.Button(label=c, custom_id=c, style=discord.ButtonStyle.grey)
            btn.callback = self.btn_callback
            self.add_item(btn)

    async def btn_callback(self, inter):
        try:
            if not inter.user.guild_permissions.administrator: return
            cmd = inter.data['custom_id']
            perms = load_perms()
            gid, rid = str(inter.guild.id), str(self.role.id)
            if gid not in perms: perms[gid] = {}
            if rid not in perms[gid]: perms[gid][rid] = []
            if cmd in perms[gid][rid]: perms[gid][rid].remove(cmd)
            else: perms[gid][rid].append(cmd)
            save_perms(perms)
            await inter.response.send_message(f"✅ تم تحديث {cmd} لـ {self.role.name}", ephemeral=True)
        except: pass

# --- معالجة الكلمات المباشرة ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    content = message.content.split()
    if not content: return
    cmd = content[0]

    try:
        if cmd == "اداره" and message.author.guild_permissions.administrator:
            await message.delete()
            if message.role_mentions:
                role = message.role_mentions[0]
                await message.channel.send(f"إعدادات {role.name} (مخفية):", view=PermsView(role), delete_after=30)

        elif cmd == "قول" and can_do(message.author, "قول"):
            await message.delete()
            view = ui.View()
            btn = ui.Button(label="ابدأ الكتابة", style=discord.ButtonStyle.blurple)
            btn.callback = lambda i: i.response.send_modal(SayModal())
            view.add_item(btn)
            await message.channel.send("نافذة قول (مخفية):", view=view, delete_after=15)

        elif cmd == "مسح" and can_do(message.author, "مسح"):
            await message.delete()
            num = int(content[1]) if len(content) > 1 else 10
            await message.channel.purge(limit=num)
            await message.channel.send(f"🧹 تم المسح لعيون فهد.", delete_after=2)

        elif cmd == "بنعالي" and can_do(message.author, "بنعالي"):
            if message.mentions:
                await message.delete()
                await message.mentions[0].ban(reason="لعيون فهد")
                await message.channel.send(f"💀 بنعالي لعيون فهد.", delete_after=3)

        elif cmd == "طرد" and can_do(message.author, "طرد"):
            if message.mentions:
                await message.delete()
                await message.mentions[0].kick(reason="لعيون فهد")
                await message.channel.send(f"🚪 طرد لعيون فهد.", delete_after=3)

        elif cmd == "ر" and can_do(message.author, "ر"):
            if message.mentions and message.role_mentions:
                await message.delete()
                m, r = message.mentions[0], message.role_mentions[0]
                if r in m.roles: await m.remove_roles(r)
                else: await m.add_roles(r)
                await message.channel.send(f"✅ تم تعديل الرتب لعيون فهد.", delete_after=3)

    except Exception as e:
        print(f"خطأ في التنفيذ: {e}")

    await bot.process_commands(message)

# --- ترحيب ---
@bot.event
async def on_member_join(member):
    try:
        ch = bot.get_channel(WELCOME_CHANNEL_ID)
        if ch:
            await ch.send(f"*hey : {member.mention}*\n*by : <@{member.guild.owner_id}>*", allowed_mentions=discord.AllowedMentions(users=[member]))
    except: pass

# السطر اللي كان يسبب الكراش عدلته لعيونك
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
