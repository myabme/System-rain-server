import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask, request
from threading import Thread

# --- إعدادات الداشبورد (تصميم فخم وأسود) ---
app = Flask(__name__)
bot = None 

@app.route('/')
def home():
    return """
    <body style="background:#000; color:#fff; font-family:sans-serif; display:flex; flex-direction:column; justify-content:center; align-items:center; height:100vh; margin:0;">
        <h1 style="font-size:5rem; letter-spacing:10px; text-shadow: 0 0 20px rgba(255,255,255,0.2);">RÁINBOT</h1>
        <p style="color:#444; letter-spacing:3px;">SYSTEM ONLINE</p>
        <a href="/dashboard" style="margin-top:40px; padding:12px 45px; background:transparent; color:#fff; border:1px solid #fff; text-decoration:none; transition:0.5s;" onmouseover="this.style.background='#fff'; this.style.color='#000'" onmouseout="this.style.background='transparent'; this.style.color='#fff'">OPEN DASHBOARD</a>
    </body>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <body style="background:#000; color:#fff; font-family:sans-serif; display:flex; flex-direction:column; align-items:center; padding-top:50px;">
        <h2 style="letter-spacing:5px; border-bottom:1px solid #111; width:100%; text-align:center; padding-bottom:20px;">CONTROL PANEL</h2>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; width:80%; max-width:500px; margin-top:40px;">
            <button onclick="sendCmd('clear')" style="background:none; border:1px solid #333; color:#fff; padding:25px; cursor:pointer; transition:0.3s;" onmouseover="this.style.borderColor='#fff'">CLEAR CHAT</button>
            <button onclick="alert('قريباً: إدارة الرتب')" style="background:none; border:1px solid #333; color:#fff; padding:25px; cursor:pointer; transition:0.3s;" onmouseover="this.style.borderColor='#fff'">ROLES MGMT</button>
        </div>
        <script>
            async function sendCmd(c) {
                try {
                    const r = await fetch(`/api/control?cmd=${c}`);
                    const d = await r.json();
                    alert(d.message);
                } catch(e) { alert("خطأ في الاتصال بالبوت"); }
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
        return {"status": "success", "message": "تم إرسال أمر المسح"}
    return {"status": "error", "message": "أمر مجهول"}

async def execute_dashboard_clear():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).manage_messages:
                await channel.purge(limit=10)
                await channel.send("🧹 **تم تنظيف الشات عبر لوحة التحكم**", delete_after=5)
                return

# --- إعدادات البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} جاهز!')

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    cmd_list = ['مساعدة', 'مسح', 'طرد', 'بنعالي', 'ر', 'قول', 'موقع']
    msg_content = message.content.strip().split()
    if not msg_content: return
    if msg_content[0] in cmd_list:
        await bot.process_commands(message)

# الأوامر
@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear_cmd(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ تم مسح {amount} رسالة", delete_after=3)

@bot.command(name="ر")
@commands.has_permissions(manage_roles=True)
async def role_cmd(ctx, member: discord.Member = None, role: discord.Role = None):
    if member and role:
        await member.add_roles(role)
        await ctx.send(f"✅ تم إعطاء رتبة **{role.name}** لـ {member.mention}")
    else: await ctx.send("الاستخدام: `ر @عضو @الرتبة`")

@bot.command(name="موقع")
async def site_cmd(ctx):
    # كود يجيب الرابط الجديد تلقائياً
    url = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'تحقق من لوحة تحكم ريلواي')}"
    await ctx.send(f"🔗 **رابط الموقع الجديد:**\n{url}")

# تشغيل Flask
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(os.getenv('DISCORD_TOKEN'))
