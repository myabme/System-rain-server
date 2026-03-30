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

# --- فحص الصلاحيات (معدل لضمان عمل !اداره للأدمن) ---
def can_execute(user, command_name):
    # إذا كان الشخص "Owner" أو عنده صلاحية "Administrator" في الديسكورد يشتغل معه كل شيء فوراً
    if user.guild_permissions.administrator or user.id == user.guild.owner_id:
        return True
    
    perms = load_perms()
    guild_id = str(user.guild.id)
    guild_perms = perms.get(guild_id, {})
    
    for role_id, allowed_cmds in guild_perms.items():
        if any(role.id == int(role_id) for role in user.roles):
            if command_name in allowed_cmds: return True
    return False

# --- أوامر الإدارة وقول (Ephemeral مخفي) ---

class PermsView(ui.View):
    def __init__(self, role: discord.Role):
        super().__init__(timeout=None)
        self.role = role
        self.commands = ["مسح", "بنعالي", "طرد", "ر", "قول", "اداره"]
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        perms = load_perms()
        guild_id = str(self.role.guild.id)
        role_id = str(self.role.id)
        role_perms = perms.get(guild_id, {}).get(role_id, [])

        for cmd in self.commands:
            is_on = cmd in role_perms
            style = discord.ButtonStyle.green if is_on else discord.ButtonStyle.red
            button = ui.Button(label=cmd, style=style, custom_id=cmd)
            button.callback = self.button_callback
            self.add_item(button)

    async def button_callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("فقط الإدارة العليا تعدل الصلاحيات!", ephemeral=True)
            
        perms = load_perms()
        guild_id = str(interaction.guild.id)
        role_id = str(self.role.id)
        cmd = interaction.data['custom_id']

        if guild_id not in perms: perms[guild_id] = {}
        if role_id not in perms[guild_id]: perms[guild_id][role_id] = []

        if cmd in perms[guild_id][role_id]: perms[guild_id][role_id].remove(cmd)
        else: perms[guild_id][role_id].append(cmd)

        save_perms(perms)
        self.update_buttons()
        await interaction.response.edit_message(view=self)

class RoleSelectView(ui.View):
    @ui.select(cls=ui.RoleSelect, placeholder="اختر الرتبة...")
    async def select_role(self, interaction: discord.Interaction, select: ui.RoleSelect):
        role = select.values[0]
        embed = discord.Embed(title=f"إعدادات رتبة: {role.name}", color=BLACK_COLOR)
        await interaction.response.send_message(embed=embed, view=PermsView(role), ephemeral=True)

@client.command(name="اداره")
async def admin_panel(ctx):
    if not can_execute(ctx.author, "اداره"): return
    await ctx.message.delete()
    await ctx.send("لوحة تحكم Rain (مخفية):", view=RoleSelectView(), ephemeral=True, delete_after=60)

@client.command(name="قول")
async def say_cmd(ctx):
    if not can_execute(ctx.author, "قول"): return
    await ctx.message.delete()
    
    # نافذة قول مباشرة
    class SayModal(ui.Modal, title="رسالة البوت"):
        text = ui.TextInput(label="النص", style=discord.TextStyle.paragraph)
        async def on_submit(self, inter: discord.Interaction):
            view = ui.View()
            sel = ui.ChannelSelect(placeholder="اختر الروم...")
            async def ch_callback(i):
                ch = i.guild.get_channel(int(i.data['values'][0]))
                await ch.send(self.text.value)
                await i.response.send_message("✅ تم", ephemeral=True)
            sel.callback = ch_callback
            view.add_item(sel)
            await inter.response.send_message("اختر الروم:", view=view, ephemeral=True)

    await ctx.send("اضغط للبدء:", view=ui.View().add_item(ui.Button(label="Say", style=discord.ButtonStyle.blurple, custom_id="say_start")), ephemeral=True)

# --- باقي الأوامر والترحيب (نفس الكود السابق) ---
@client.event
async def on_interaction(interaction):
    if interaction.data.get('custom_id') == "say_start":
        await interaction.response.send_modal(SayModal())

# (أضف هنا دالة on_message والترحيب من الكود السابق)

token = os.getenv('DISCORD_TOKEN')
client.run(token)
