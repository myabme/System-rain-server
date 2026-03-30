import discord
from discord.ext import commands
from discord import ui
import datetime
import os
import asyncio
import json

# --- الإعدادات ---
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

BLACK_COLOR = 0x000001
WELCOME_CHANNEL_ID = 1453704693770616904 
PERMS_FILE = "permissions.json"

def load_perms():
    if os.path.exists(PERMS_FILE):
        try:
            with open(PERMS_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_perms(perms):
    with open(PERMS_FILE, "w") as f: json.dump(perms, f)

def can_execute(user, command_name):
    if user.guild_permissions.administrator or user.id == user.guild.owner_id:
        return True
    perms = load_perms()
    guild_id = str(user.guild.id)
    guild_perms = perms.get(guild_id, {})
    for role_id, allowed_cmds in guild_perms.items():
        if any(role.id == int(role_id) for role in user.roles):
            if command_name in allowed_cmds: return True
    return False

# --- نافذة كتابة الرسالة (Modal) ---
class SayModal(ui.Modal, title="وش تبي البوت يقول؟"):
    text_input = ui.TextInput(label="اكتب نصك هنا", style=discord.TextStyle.paragraph, required=True, placeholder="اكتب الكلام اللي تبيه يظهر باسم البوت...")

    async def on_submit(self, interaction: discord.Interaction):
        # بعد ما يكتب النص، نطلع له قائمة الرومات
        view = ui.View()
        select = ui.ChannelSelect(placeholder="اختر الروم اللي أرسل فيها...", channel_types=[discord.ChannelType.text])
        
        async def channel_callback(inter: discord.Interaction):
            channel_id = inter.data['values'][0]
            target_channel = inter.guild.get_channel(int(channel_id))
            if target_channel:
                await target_channel.send(self.text_input.value)
                await inter.response.send_message(f"✅ تم الإرسال في {target_channel.mention} لعيون فهد.", ephemeral=True)
            else:
                await inter.response.send_message("❌ تعذر العثور على الروم.", ephemeral=True)

        select.callback = channel_callback
        view.add_item(select)
        await interaction.response.send_message("الحين اختر الروم (مخفي):", view=view, ephemeral=True)

# --- زر البدء لأمر قول ---
class SayStartView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Say", style=discord.ButtonStyle.blurple, custom_id="start_say_proc")
    async def say_button(self, interaction: discord.Interaction, button: ui.Button):
        if can_execute(interaction.user, "قول"):
            await interaction.response.send_modal(SayModal())
        else:
            await interaction.response.send_message("ما عندك صلاحية تستخدم هذا الأمر!", ephemeral=True)

@client.command(name="قول")
async def say_cmd(ctx):
    if not can_execute(ctx.author, "قول"): return
    await ctx.message.delete()
    embed = discord.Embed(description="اضغط على الزر تحت عشان تفتح نافذة الكتابة.", color=BLACK_COLOR)
    await ctx.send(embed=embed, view=SayStartView(), delete_after=30)

# --- لوحة التحكم (اداره) ---
# (نفس الكود السابق مع التأكد من استدعاء can_execute)
@client.command(name="اداره")
async def admin_panel(ctx):
    if not can_execute(ctx.author, "اداره"): return
    await ctx.message.delete()
    from RoleSelectView import RoleSelectView # تأكد أنها معرفة
    await ctx.send("لوحة تحكم Rain (مخفية):", view=RoleSelectView(), delete_after=60)

# --- معالجة الرسائل (مسح، بنعالي، الخ) ---
@client.event
async def on_message(message):
    if message.author == client.user: return
    content = message.content.split()
    if not content: return
    cmd = content[0]

    if cmd == "مسح" and can_execute(message.author, "مسح"):
        amount = int(content[1]) if len(content) > 1 else 10
        await message.channel.purge(limit=amount + 1)
        await message.channel.send(f"🧹 تم المسح لعيون فهد.", delete_after=3)
    
    # ... (باقي أوامر بنعالي وطرد ور) ...
    await client.process_commands(message)

token = os.getenv('DISCORD_TOKEN')
client.run(token)
