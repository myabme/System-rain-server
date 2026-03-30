import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask, render_template_string, request
from threading import Thread

# --- إعدادات الواجهة (أبيض وأسود) ---
app = Flask(__name__)
bot = None # سيتم تعريفه لاحقاً

@app.route('/')
def home():
    return """
    <body style="background:#000; color:#fff; font-family:sans-serif; display:flex; flex-direction:column; justify-content:center; align-items:center; height:100vh; margin:0; overflow:hidden;">
        <div style="position:absolute; width:100%; height:100%; pointer-events:none; opacity:0.1; background: repeating-linear-gradient(0deg, transparent, transparent 1px, #fff 1px, #fff 2px); background-size: 100% 4px;"></div>
        <h1 style="font-size:5rem; letter-spacing:10px; margin:0; z-index:2;">RÁINBOT</h1>
        <a href="/dashboard" style="margin-top:40px; padding:12px 45px; background:transparent; color:#fff; border:1px solid #fff; text-decoration:none; z-index:2; transition:0.4s;" onmouseover="this.style.background='#fff'; this.style.color='#000'" onmouseout="this.style.background='transparent'; this.style.color='#fff'">OPEN DASHBOARD</a>
    </body>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <body style="background:#000; color:#fff; font-family:sans-serif; display:flex; flex-direction:column; align-items:center; padding-top:50px;">
        <h2 style="letter-spacing:5px;">SYSTEM CONTROL</h2>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; width:80%; max-width:500px; margin-top:40px;">
            <button onclick="sendCmd('clear')" style="background:none; border:1px solid #333; color:#fff; padding:20px; cursor:pointer; transition:0.3s;" onmouseover="this.style.borderColor='#fff'">CLEAR CHAT</button>
            <button onclick="sendCmd('status')" style="background:none; border:1px solid #333; color:#fff; padding:20px; cursor:pointer; transition:0.3s;" onmouseover="this.style.borderColor='#fff'">BOT STATUS</button>
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
    # التأكد أن البوت يعمل قبل إرسال الأمر
    if bot is None or not bot.is_ready():
        return {"status": "error", "message": "انتظر ثواني.. البوت لسه يشغل محركاته!"}
    
    if cmd == 'clear':
        # استخدام asyncio.run_coroutine_threadsafe للربط الآمن بين Flask والبوت
        asyncio.run_coroutine_threadsafe(execute_dashboard_clear(), bot.loop)
        return {"status": "success", "message": "تم إرسال أمر المسح بنجاح"}
    
    return {"status": "error", "message": "أمر مجهول"}

async def execute_dashboard_clear():
    # يبحث عن أول قناة نصية متاحة لمسح الرسائل فيها
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).manage_messages:
                await channel.purge(limit=10)
                await channel.send("🧹 **تم تنظيف الشات بواسطة لوحة تحكم Ráinbot**", delete_after=5)
                return

# --- إعدادات البوت (بدون علامات) ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} متصل الآن بدون كراشات!')

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    # معالجة الأوامر بالكلمات المباشرة
    cmd_list = ['مساعدة', 'مسح', 'طرد', 'بنعالي', 'ر', 'قول', 'موقع']
    if any(message.content.startswith(c) for c in cmd_list):
        await bot.process_commands(message)

# الأوامر الأساسية
@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear_cmd(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send("✅ تم المسح", delete_after=2)

@bot.command(name="بنعالي")
@commands.has_permissions(ban_members=True)
async def ban_cmd(ctx, member: discord.Member = None):
    if member:
        await member.ban()
        await ctx.send("🚫 بنعالي.")
    else: await ctx.send("منشن الشخص!")

@bot.command(name="ر")
@commands.has_permissions(manage_roles=True)
async def role_cmd(ctx, member: discord.Member = None, role: discord.Role = None):
    if member and role:
        await member.add_roles(role)
        await ctx.send(f"✅ تم إعطاء رتبة {role.name}")
    else: await ctx.send("الاستخدام: `ر @عضو @الرتبة`")

# تشغيل السيرفر في الخلفية
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    bot.run(os.getenv('DISCORD_TOKEN'))
