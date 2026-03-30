import discord
from discord.ext import commands
from discord import ui
import os
import json
import asyncio

# --- الإعدادات الأساسية لعيون أبو مشاري ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="", intents=intents, help_command=None) # شلنا البريفكس تماماً

BLACK_COLOR = 0x000001
WELCOME_CHANNEL_ID = 1453704693770616904 
PERMS_FILE = "permissions.json"

# --- نظام حفظ الصلاحيات ---
def load_perms():
    if os.path.exists(PERMS_FILE):
        try:
            with open(PERMS_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_perms(perms):
    with open(PERMS_FILE, "w") as f: json.dump(perms, f)

def can_do(user, cmd_name):
    # الأدمن والاونر مسموح لهم دائماً
    if user.guild_permissions.administrator or user.id == user.guild.owner_id: return True
    perms = load_perms().get(str(user.guild.id), {})
    for rid, cmds in perms.items():
        if any(r.id == int(rid) for r in user.roles) and cmd_name in cmds: return True
    return False

# --- نافذة !قول (تفتح بمجرد كتابة "قول") ---
class SayModal(ui.Modal, title="رسالة البوت"):
    text = ui.TextInput(label="وش تبيني أقول؟", style=discord.TextStyle.paragraph)
    async def on_submit(self, inter):
        view = ui.View()
        sel = ui.ChannelSelect(placeholder="اختر الروم...")
        async def sel_cb(i):
            ch = i.guild.get_channel(int(i.data['values'][0]))
            await ch.send(self.text.value)
            await i.response.send_message("✅ تم الإرسال", ephemeral=True)
        sel.callback = sel_cb
        view.add_item(sel)
        await inter.response.send_message("الحين اختر الروم (مخفي):", view=view, ephemeral=True)

# --- لوحة التحكم (تفتح بمجرد كتابة "اداره") ---
class PermsView(ui.View):
    def __init__(self, role):
        super().__init__(timeout=None)
        self.role = role
        cmds = ["مسح", "بنعالي", "طرد", "ر", "قول", "اداره"]
        for c in cmds:
            btn = ui.Button(label=c, custom_id=c, style=discord.ButtonStyle.grey)
            btn.callback = self.btn_callback
            self.add_item(btn)

    async def btn_callback(self, inter):
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

# --- معالجة الكلمات (الأوامر بدون أي شرطة) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    content = message.content.split()
    if not content: return
    cmd = content[0]

    # 1. إدارة (تكتب: اداره @رتبه)
    if cmd == "اداره" and message.author.guild_permissions.administrator:
        await message.delete()
        if message.role_mentions:
            role = message.role_mentions[0]
            await message.channel.send(f"إعدادات {role.name} (مخفية):", view=PermsView(role), delete_after=30)
        else:
            await message.channel.send("منشن الرتبة يا أبو مشاري!", delete_after=5)

    # 2. قول (تكتب: قول)
    elif cmd == "قول" and can_do(message.author, "قول"):
        await message.delete()
        view = ui.View()
        btn = ui.Button(label="ابدأ الكتابة", style=discord.ButtonStyle.blurple)
        btn.callback = lambda i: i.response.send_modal(SayModal())
        view.add_item(btn)
        await message.channel.send("نافذة قول (مخفية):", view=view, delete_after=15)

    # 3. مسح (تكتب: مسح 10)
    elif cmd == "مسح" and can_do(message.author, "مسح"):
        await message.delete()
        num = int(content[1]) if len(content) > 1 else 10
        await message.channel.purge(limit=num)
        await message.channel.send(f"🧹 تم المسح لعيون فهد.", delete_after=2)

    # 4. بنعالي (تكتب: بنعالي @شخص)
    elif cmd == "بنعالي" and can_do(message.author, "بنعالي"):
        if message.mentions:
            await message.delete()
            await message.mentions[0].ban()
            await message.channel.send(f"💀 بنعالي لعيون فهد.", delete_after=3)

    # 5. طرد (تكتب: طرد @شخص)
    elif cmd == "طرد" and can_do(message.author, "طرد"):
        if message.mentions:
            await message.delete()
            await message.mentions[0].kick()
            await message.channel.send(f"🚪 طرد لعيون فهد.", delete_after=3)

    # 6. ر (تكتب: ر @شخص @رتبه)
    elif cmd == "ر" and can_do(message.author, "ر"):
        if message.mentions and message.role_mentions:
            await message.delete()
            m, r = message.mentions[0], message.role_mentions[0]
            if r in m.roles: await m.remove_roles(r)
            else: await m.add_roles(r)
            await message.channel.send(f"✅ تم تعديل الرتب لعيون فهد.", delete_after=3)

# --- ترحيب (منشن صامت) ---
@bot.event
async def on_member_join(member):
    ch = bot.get_channel(WELCOME_CHANNEL_ID)
    if ch:
        try:
            invites = await member.guild.invites()
            by = next((i.inviter.mention for i in invites if i.uses > 0), "غير معروف")
            await ch.send(f"*hey : {member.mention}*\n*by : {by}*", allowed_mentions=discord.AllowedMentions(users=[member]))
        except: pass

bot.run(os.getenv('TOKEN'))
