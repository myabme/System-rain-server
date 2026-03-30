import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import asyncio

# --- الإعدادات الأساسية ---
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        self.perms_file = "permissions.json"

    async def setup_hook(self):
        # مزامنة الأوامر المخفية (Slash Commands)
        await self.tree.sync()
        print(f"✅ تم مزامنة الأوامر المخفية لعيون أبو مشاري")

bot = MyBot()
WELCOME_CHANNEL_ID = 1453704693770616904 

# --- نظام حفظ الصلاحيات ---
def load_perms():
    if os.path.exists(bot.perms_file):
        try:
            with open(bot.perms_file, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_perms(perms):
    with open(bot.perms_file, "w") as f: json.dump(perms, f)

def can_do(interaction, cmd_name):
    if interaction.user.guild_permissions.administrator: return True
    perms = load_perms()
    guild_id = str(interaction.guild.id)
    for role_id, cmds in perms.get(guild_id, {}).items():
        if any(r.id == int(role_id) for r in interaction.user.roles):
            if cmd_name in cmds: return True
    return False

# --- 1. أمر !قول المتطور (مخفي وسريع) ---
class SayModal(discord.ui.Modal, title="وش تبي البوت يقول؟"):
    text = discord.ui.TextInput(label="الرسالة", style=discord.TextStyle.paragraph)
    
    async def on_submit(self, interaction: discord.Interaction):
        view = discord.ui.View()
        select = discord.ui.ChannelSelect(placeholder="اختر الروم...", channel_types=[discord.ChannelType.text])
        
        async def ch_callback(inter):
            ch = inter.guild.get_channel(int(inter.data['values'][0]))
            await ch.send(self.text.value)
            await inter.response.send_message("✅ تم الإرسال بنجاح.", ephemeral=True)
        
        select.callback = ch_callback
        view.add_item(select)
        await interaction.response.send_message("الحين اختر الروم:", view=view, ephemeral=True)

@bot.tree.command(name="قول", description="إرسال رسالة باسم البوت (مخفي)")
async def say(interaction: discord.Interaction):
    if not can_do(interaction, "قول"):
        return await interaction.response.send_message("ما عندك صلاحية!", ephemeral=True)
    await interaction.response.send_modal(SayModal())

# --- 2. أمر !اداره (التحكم بالرتب بضغطة زر مخفية) ---
class PermsControl(discord.ui.View):
    def __init__(self, role):
        super().__init__()
        self.role = role
        cmds = ["مسح", "بنعالي", "طرد", "ر", "قول", "اداره"]
        for c in cmds:
            self.add_item(discord.ui.Button(label=c, custom_id=c, style=discord.ButtonStyle.grey))

    async def interaction_check(self, inter):
        if not inter.user.guild_permissions.administrator: return False
        cmd = inter.data['custom_id']
        perms = load_perms()
        gid, rid = str(inter.guild.id), str(self.role.id)
        if gid not in perms: perms[gid] = {}
        if rid not in perms[gid]: perms[gid][rid] = []
        
        if cmd in perms[gid][rid]: perms[gid][rid].remove(cmd)
        else: perms[gid][rid].append(cmd)
        
        save_perms(perms)
        await inter.response.send_message(f"✅ تم تحديث {cmd} لـ {self.role.name}", ephemeral=True)
        return True

@bot.tree.command(name="اداره", description="تحديد صلاحيات الرتب بالبوت (مخفي)")
@app_commands.describe(role="الرتبة اللي تبي تعدلها")
async def admin(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("للأدمن فقط!", ephemeral=True)
    await interaction.response.send_message(f"لوحة تحكم {role.name}:", view=PermsControl(role), ephemeral=True)

# --- 3. الأوامر العادية (بدون بريفكس) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    content = message.content.split()
    if not content: return
    cmd = content[0]

    # دالة مساعدة للفحص السريع
    def check(u, c):
        if u.guild_permissions.administrator: return True
        p = load_perms().get(str(message.guild.id), {})
        for rid, cmds in p.items():
            if any(r.id == int(rid) for r in u.roles) and c in cmds: return True
        return False

    if cmd == "مسح" and check(message.author, "مسح"):
        num = int(content[1]) if len(content) > 1 else 10
        await message.delete() # حذف كلمة "مسح"
        await message.channel.purge(limit=num)
        await message.channel.send(f"🧹 تم المسح لعيون فهد.", delete_after=2)

    if cmd == "بنعالي" and check(message.author, "بنعالي"):
        if message.mentions:
            await message.delete()
            await message.mentions[0].ban()
            await message.channel.send(f"💀 بنعالي لعيون فهد.", delete_after=3)

    # (طرد ور) بنفس الطريقة...
    await bot.process_commands(message)

# --- ترحيب (منشن صامت) ---
@bot.event
async def on_member_join(member):
    ch = bot.get_channel(WELCOME_CHANNEL_ID)
    if ch:
        invites = await member.guild.invites()
        by = next((i.inviter.mention for i in invites if i.uses > 0), "غير معروف")
        await ch.send(f"*hey : {member.mention}*\n*by : {by}*", allowed_mentions=discord.AllowedMentions(users=[member]))

bot.run(os.getenv('TOKEN'))
