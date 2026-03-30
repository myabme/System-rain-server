import discord
from discord.ext import commands
import os
from flask import Flask, Thread, request

# --- واجهة التحكم المترابطة (White & Black) ---
app = Flask(__name__)
bot_instance = None # متغير لحفظ نسخة البوت للربط

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>Ráinbot</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;900&display=swap');
            body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: #000; overflow: hidden; font-family: 'Cairo', sans-serif; }
            .rain { position: absolute; width: 100%; height: 100%; z-index: 1; }
            .drop { position: absolute; background: rgba(255,255,255,0.1); width: 1px; height: 25px; top: -100px; animation: fall linear infinite; }
            @keyframes fall { to { transform: translateY(110vh); } }
            .container { position: relative; z-index: 10; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }
            h1 { font-size: 5rem; color: #fff; font-weight: 900; letter-spacing: 10px; margin: 0; }
            .btn { margin-top: 40px; padding: 12px 45px; background: transparent; color: #fff; border: 1px solid #fff; text-decoration: none; transition: 0.5s; cursor: pointer; }
            .btn:hover { background: #fff; color: #000; }
        </style>
    </head>
    <body>
        <audio autoplay loop id="rainAudio"><source src="https://www.soundjay.com/nature/rain-01.mp3" type="audio/mpeg"></audio>
        <div class="rain" id="rain"></div>
        <div class="container">
            <h1>RÁINBOT</h1>
            <a href="/dashboard" class="btn">OPEN DASHBOARD</a>
        </div>
        <script>
            const container = document.getElementById('rain');
            for (let i = 0; i < 30; i++) {
                const drop = document.createElement('div');
                drop.className = 'drop';
                drop.style.left = Math.random() * 100 + 'vw';
                drop.style.animationDuration = (Math.random() * 2 + 2) + 's';
                container.appendChild(drop);
            }
            document.body.addEventListener('click', () => { document.getElementById('rainAudio').play(); }, { once: true });
        </script>
    </body>
    </html>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
            body { background: #000; color: #fff; font-family: 'Cairo', sans-serif; display: flex; flex-direction: column; align-items: center; padding-top: 50px; }
            .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; width: 80%; max-width: 600px; margin-top: 50px; }
            .card { border: 1px solid #222; padding: 25px; text-align: center; cursor: pointer; transition: 0.3s; background: none; color: #fff; }
            .card:hover { border-color: #fff; background: #fff; color: #000; }
            .card h3 { margin: 0; font-size: 0.8rem; letter-spacing: 2px; }
            .header { border-bottom: 1px solid #111; width: 100%; text-align: center; padding-bottom: 20px; }
            .back { margin-top: 40px; color: #444; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="header"><h2>SYSTEM CONTROL</h2></div>
        <div class="grid">
            <div class="card" onclick="sendCommand('clear')"><h3>CLEAR CHAT</h3><p style="font-size: 0.6rem;">نظف آخر 10 رسائل</p></div>
            <div class="card" onclick="sendCommand('status')"><h3>BOT STATUS</h3><p style="font-size: 0.6rem;">تغيير الحالة</p></div>
            <div class="card" onclick="alert('قريباً: التحكم بالأعضاء')"><h3>MEMBERS</h3><p style="font-size: 0.6rem;">إدارة كاملة</p></div>
            <div class="card" onclick="alert('قريباً: السجلات')"><h3>LOGS</h3><p style="font-size: 0.6rem;">سجل الأحداث</p></div>
        </div>
        <a href="/" class="back">RETURN TO MAIN</a>

        <script>
            async function sendCommand(cmd) {
                const res = await fetch(`/api/control?cmd=${cmd}`);
                const data = await res.json();
                alert(data.message);
            }
        </script>
    </body>
    </html>
    """

# --- الـ API اللي يربط الموقع بالبوت ---
@app.route('/api/control')
def control():
    cmd = request.args.get('cmd')
    if not bot_instance or not bot_instance.is_ready():
        return {"status": "error", "message": "البوت غير متصل حالياً!"}
    
    if cmd == 'clear':
        # تنفيذ أمر مسح من المتصفح
        bot_instance.loop.create_task(execute_clear())
        return {"status": "success", "message": "جاري تنظيف الشات..."}
    
    return {"status": "unknown", "message": "أمر غير معروف"}

async def execute_clear():
    # يبحث عن أول قناة نصية يقدر يرسل فيها ويمسح
    for guild in bot_instance.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).manage_messages:
                await channel.purge(limit=10)
                await channel.send("🧹 تم تنظيف الشات عبر لوحة التحكم (Dashboard)", delete_after=5)
                return

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run).start()

# --- إعدادات البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='', intents=intents, help_command=None)
bot_instance = bot # ربط النسخة بمتغير الـ API

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} متصل وجاهز للربط!')

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    content = message.content.strip()
    if not content: return
    first_word = content.split()[0]
    if first_word in ['مساعدة', 'موقع', 'مسح', 'طرد', 'بنعالي', 'ر', 'قول']:
        await bot.process_commands(message)

# الأوامر (نفسها اللي طلبتها)
@bot.command(name="مساعدة")
async def help_cmd(ctx):
    embed = discord.Embed(title="🌑 قائمة الأوامر", color=0xffffff)
    embed.add_field(name="🛡️ الإدارة", value="`مسح` | `طرد` | `بنعالي` | `ر`", inline=False)
    embed.add_field(name="🔗 عام", value="`موقع` | `قول`", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear_cmd(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send("✅ تم المسح", delete_after=2)

@bot.command(name="طرد")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None):
    if member: await member.kick(); await ctx.send("👤 تم الطرد")
    else: await ctx.send("منشن الشخص!")

@bot.command(name="بنعالي")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None):
    if member: await member.ban(); await ctx.send("🚫 بنعالي")
    else: await ctx.send("منشن الشخص!")

@bot.command(name="ر")
@commands.has_permissions(manage_roles=True)
async def give_role(ctx, member: discord.Member = None, role: discord.Role = None):
    if member and role:
        await member.add_roles(role)
        await ctx.send(f"✅ تم إعطاء رتبة {role.name}")
    else: await ctx.send("الاستخدام: `ر @عضو @الرتبة`")

@bot.command(name="موقع")
async def site_link(ctx):
    await ctx.send(f"🔗 رابط الموقع: https://{os.environ.get('RAILWAY_STATIC_URL', 'rainbot.up.railway.app')}")

bot.run(os.getenv('DISCORD_TOKEN'))
