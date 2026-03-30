import discord
from discord.ext import commands
from discord import ui
import datetime
import os
import asyncio
import json

# --- الإعدادات الأساسية لعيون أبو مشاري ---
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

# --- فحص الصلاحيات الذكي ---
def can_execute(user, command_name):
    # إذا كان الشخص عنده رتبة Administrator في السيرفر (أنت وفهد) يقدر يسوي كل شيء
    if user.guild_permissions.administrator: return True
    
    perms = load_perms()
    guild_id = str(user.guild.id)
    guild_perms = perms.get(guild_id, {})
    
    # فحص رتب المستخدم إذا كان مسموح لها بهذا الأمر المحدد
    for role_id, allowed_cmds in guild_perms.items():
        if any(role.id == int(role_id) for role in user.roles):
            if command_name in allowed_cmds: return True
    return False

# --- نظام الترحيب (منشن صامت للداعي) ---
@client.event
async def on_member_join(member):
    channel = client.get_channel(WELCOME_CHANNEL_ID)
    if not channel: return
    await asyncio.sleep(1)
    inviter_mention = "غير معروف"
    try:
        invites_after = await member.guild.invites()
        for invite in invites_after:
            if invite.uses > 0:
                inviter_mention = invite.inviter.mention
                break
    except: pass
    await channel.send(f"*hey : {member.mention}*\n*by : {inviter_mention}*", allowed_mentions=discord.AllowedMentions(users=[member]))

# --- لوحة التحكم الشاملة ---
class PermsView(ui.View):
    def __init__(self, role: discord.Role):
        super().__init__(timeout=60)
        self.role = role
        # هنا الأوامر اللي تقدر توزعها (بما فيها أوامر البوت نفسه)
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
    @ui.select(cls=ui.RoleSelect, placeholder="اختر الرتبة لتحديد صلاحياتها بالبوت...")
    async def select_role(self, interaction: discord.Interaction, select: ui.RoleSelect):
        role = select.values[0]
        embed = discord.Embed(title=f"صلاحيات رتبة: {role.name}", description="الأخضر: مسموح | الأحمر: ممنوع", color=BLACK_COLOR)
        await interaction.response.send_message(embed=embed, view=PermsView(role), ephemeral=True)

@client.command(name="اداره")
async def admin_panel(ctx):
    # فحص إذا الشخص مسموح له يفتح اللوحة
    if not can_execute(ctx.author, "اداره"): return
    
    await ctx.message.delete()
    embed = discord.Embed(title="لوحة تحكم Rain", description="اختر رتبة الإدارة اللي تبي تحدد مهامها (مخفية)", color=BLACK_COLOR)
    await ctx.send(embed=embed, view=RoleSelectView(), delete_after=60)

# --- نظام !قول المخفي ---
class SayModal(ui.Modal, title="رسالة البوت"):
    text_input = ui.TextInput(label="اكتب النص", style=discord.TextStyle.paragraph, required=True)
    async def on_submit(self, interaction: discord.Interaction):
        view = ui.View()
        select = ui.ChannelSelect(placeholder="اختر الروم...")
        async def ch_callback(inter):
            channel = inter.guild.get_channel(int(inter.data['values'][0]))
            await channel.send(self.text_input.value)
            await inter.response.send_message("✅ تم الإرسال", ephemeral=True)
        select.callback = ch_callback
        view.add_item(select)
        await interaction.response.send_message("اختر الروم (مخفي):", view=view, ephemeral=True)

class SayView(ui.View):
    @ui.button(label="Say", style=discord.ButtonStyle.grey)
    async def say_button(self, interaction, button):
        if can_execute(interaction.user, "قول"): await interaction.response.send_modal(SayModal())
        else: await interaction.response.send_message("ما عندك صلاحية!", ephemeral=True)

@client.command(name="قول")
async def say_cmd(ctx):
    if not can_execute(ctx.author, "قول"): return
    await ctx.message.delete()
    await ctx.send(embed=discord.Embed(description="اضغط للبدء (مخفي)", color=BLACK_COLOR), view=SayView(), delete_after=10)

# --- الأوامر المباشرة ---
@client.event
async def on_message(message):
    if message.author == client.user: return
    content = message.content.split()
    if not content: return
    cmd = content[0]

    # مسح
    if cmd == "مسح" and can_execute(message.author, "مسح"):
        amount = int(content[1]) if len(content) > 1 else 10
        await message.channel.purge(limit=amount + 1)
        await message.channel.send(f"🧹 تم المسح لعيون فهد.", delete_after=3)

    # بنعالي
    if cmd == "بنعالي" and can_execute(message.author, "بنعالي"):
        if message.mentions:
            await message.mentions[0].ban(reason="لعيون فهد")
            await message.channel.send(f"💀 تم الباند لعيون فهد.")

    # طرد
    if cmd == "طرد" and can_execute(message.author, "طرد"):
        if message.mentions:
            await message.mentions[0].kick(reason="لعيون فهد")
            await message.channel.send(f"🚪 تم الطرد لعيون فهد.")

    # ر (رتبة)
    if cmd == "ر" and can_execute(message.author, "ر"):
        if message.mentions and message.role_mentions:
            member, role = message.mentions[0], message.role_mentions[0]
            if role in member.roles: await member.remove_roles(role)
            else: await member.add_roles(role)
            await message.channel.send(f"✅ تم التعديل لعيون فهد.")

    await client.process_commands(message)

# --- أوامر المساعدة (تظهر للمستخدم حسب صلاحياته) ---
@client.command(name="اوامر")
async def my_commands(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title="أوامرك المتاحة في Rain", color=BLACK_COLOR)
    available = [f"`{c}`" for c in ["مسح", "بنعالي", "طرد", "ر", "قول", "اداره"] if can_execute(ctx.author, c)]
    embed.add_field(name="القائمة:", value=", ".join(available) if available else "لا يوجد")
    embed.set_footer(text="Developed by Wilked")
    await ctx.send(embed=embed, ephemeral=True)

token = os.getenv('DISCORD_TOKEN')
client.run(token)
