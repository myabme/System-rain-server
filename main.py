import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- واجهة Ráinbot الاحترافية (ضباب ومطر) ---
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ráinbot | Wilked</title>
        <style>
            body, html { margin: 0; padding: 0; width: 100%; height: 100%; background-color: #000; overflow: hidden; font-family: sans-serif; }
            .fog { position: absolute; width: 100%; height: 100%; z-index: 1; opacity: 0.15; background: url('https://cdn.pixabay.com/photo/2016/11/21/15/34/fog-1845173_960_720.png'); background-size: cover; animation: moveFog 100s linear infinite; }
            @keyframes moveFog { from { background-position: 0 0; } to { background-position: 10000px 0; } }
            .rain { position: absolute; width: 100%; height: 100%; z-index: 2; }
            .drop { position: absolute; background: rgba(255,255,255,0.1); width: 1px; height: 25px; top: -20px; animation: fall linear infinite; }
            @keyframes fall { to { transform: translateY(100vh); } }
            .main { position: relative; z-index: 3; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; color: #fff; text-align: center; }
            .dev { color: #5865F2; font-size: 0.8rem; font-weight: bold; letter-spacing: 5px; text-transform: uppercase; margin-bottom: 10px; }
            h1 { font-size: 3.5rem; margin: 0; letter-spacing: 3px; font-weight: 900; }
            .glow { color: #fff; text-shadow: 0 0 20px #fff, 0 0 40px #5865F2; }
            .status { margin-top: 30px; border: 1px solid #43b581; color: #43b581; padding: 8px 25px; border-radius: 50px; font-size: 0.8rem; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="fog"></div>
        <div class="rain" id="rain"></div>
        <div class="main">
            <div class="dev">Developed by Wilked</div>
            <h1>Welcome to <span class="glow">Ráin Bot</span></h1>
            <div class="status">● SYSTEM ACTIVE</div>
        </div>
        <script>
            const container = document.getElementById('rain');
            for (let i = 0; i < 120; i++) {
                const drop = document.createElement('div');
                drop.className = 'drop';
                drop.style.left = Math.random() * 100 + 'vw';
                drop.style.animationDuration = (Math.random() * 0.5 + 0.3) + 's';
                drop.style.animationDelay = Math.random() * 2 + 's';
                container.appendChild(drop);
            }
        </script>
    </body>
    </html>
    """

def run_web():
    # الحل الإجباري لريلواي: ربط البورت بشكل صحيح
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# تشغيل الموقع
Thread(target=run_web).start()

# --- إعدادات البوت (تعديل الأوامر) ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} Is Online!')

@bot.command(name="موقع")
async def dashboard(ctx):
    await ctx.message.delete()
    url = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'rainbot.up.railway.app')}"
    await ctx.send(f"صفحة RáinBot : {url}")

@bot.command(name="مساعدة")
async def help_cmd(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title="🌑 أوامر Ráinbot", color=0x000000)
    embed.add_field(name="!موقع", value="لوحة التحكم السينمائية", inline=False)
    embed.add_field(name="!قول [نص]", value="إرسال رسالة مخفية", inline=False)
    embed.add_field(name="!مسح [عدد]", value="تنظيف الشات", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="قول")
async def say(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)

# تشغيل البوت
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
