import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask, request
from threading import Thread

# --- واجهة الداشبورد (أبيض وأسود) ---
app = Flask(__name__)
bot = None 

@app.route('/')
def home():
    return """
    <body style="background:#000; color:#fff; font-family:sans-serif; display:flex; flex-direction:column; justify-content:center; align-items:center; height:100vh; margin:0;">
        <h1 style="font-size:5rem; letter-spacing:10px;">RÁINBOT</h1>
        <a href="/dashboard" style="margin-top:40px; padding:12px 45px; background:transparent; color:#fff; border:1px solid #fff; text-decoration:none;">OPEN DASHBOARD</a>
    </body>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <body style="background:#000; color:#fff; font-family:sans-serif; display:flex; flex-direction:column; align-items:center; padding-top:50px;">
        <h2>SYSTEM CONTROL</h2>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; width:80%; max-width:500px; margin-top:40px;">
            <button onclick="sendCmd('clear')" style="background:none; border:1px solid #333; color:#fff; padding:20px; cursor:pointer;">CLEAR CHAT</button>
            <button onclick="alert('قريباً')" style="background:none; border:1px solid #333; color:#fff; padding:20px; cursor:pointer;">STATS</button>
        </div>
        <script>
            async function sendCmd(c) {
                const r = await fetch(`/api/control?cmd=${c}`);
                const d = await r.json();
                alert(d.message);
            }
        </script>
    </body>
    """

@app.route('/api/control')
def control():
    cmd = request.args.get('cmd')
    if bot is None or not bot.is_ready():
        return {"status": "error", "message": "البوت لسه بيجهز!"}
    if cmd == 'clear':
        asyncio.run_coroutine_threadsafe(execute_dashboard_clear(), bot.loop)
        return {"status": "success", "message": "تم تنظيف الشات"}
    return {"status": "error", "message": "أمر مجهول"}

async def execute_dashboard_clear():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).manage_messages:
                await channel.purge(limit=10)
                await channel.send("🧹 **تم المسح عبر الداشبورد**", delete_after=5)
                return

# --- إعدادات البوت (إصلاح شامل لجميع الأوامر) ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} جاهز وجميع الأوامر مفعلة!')

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    # قائمة الأوامر المتاحة
    cmd_list = ['مساعدة', 'مسح', 'طرد', 'بنعالي', 'ر', 'قول', 'موقع']
    
    # تنظيف الرسالة وأخذ أول كلمة فقط للتأكد من أنها أمر
    msg_content = message.content.strip().split()
    if not msg_content: return
    
    first_word = msg_content[0]
    
    if first_word in cmd_list:
        await bot.process_commands(message)

# نظام تصحيح الأخطاء الذكي
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="❌ خطأ في الاستخدام", color=0xffffff)
        if ctx.command.name == 'ر':
            embed.description = "الاستخدام الصحيح: `ر @عضو @الرتبة`"
        elif ctx.command.name in ['طرد', 'بنعالي']:
            embed.description = f"الاستخدام الصحيح: `{ctx.command.name} @عضو`"
        else:
            embed.description = "تأكد من كتابة الأمر والمنشن بشكل صحيح."
        await ctx.send(embed=embed, delete_after=10)

# --- الأوامر المباشرة ---

@bot.command(name="مساعدة")
async def help_cmd(ctx):
    embed = discord.Embed(title="🌑 قائمة الأوامr", color=0xffffff)
    embed.add_field(name="🛡️ الإدارة", value="`مسح [عدد]`\n`طرد [@عضو]`\n`بنعالي [@عضو]`\n`ر [@عضو] [@الرتبة]`", inline=False)
    embed.add_field(name="🔗 عام", value="`موقع`\n`قول [نص]`", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear_cmd(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ تم مسح {amount} رسالة", delete_after=3)

@bot.command(name="طرد")
@commands.has_permissions(kick_members=True)
async def kick_cmd(ctx, member: discord.Member = None):
    if member:
        await member.kick()
        await ctx.send(f"👤 تم طرد {member.mention}")
    else: raise commands.MissingRequiredArgument(None)

@bot.command(name="بنعالي")
@commands.has_permissions(ban_members=True)
async def ban_cmd(ctx, member: discord.Member = None):
    if member:
        await member.ban()
        await ctx.send(f"🚫 تم إعطاء بنعالي لـ {member.mention}")
    else: raise commands.MissingRequiredArgument(None)

@bot.command(name="ر")
@commands.has_permissions(manage_roles=True)
async def role_cmd(ctx, member: discord.Member = None, role: discord.Role = None):
    if member and role:
        await member.add_roles(role)
        await ctx.send(f"✅ تم إعطاء رتبة **{role.name}** لـ {member.mention}")
    else: raise commands.MissingRequiredArgument(None)

@bot.command(name="قول")
async def say_cmd(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

@bot.command(name="موقع")
async def site_cmd(ctx):
    await ctx.send("🔗 **رابط الداشبورد:** https://system-rain-server-production.up.railway.app")

# تشغيل Flask
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(os.getenv('DISCORD_TOKEN'))
