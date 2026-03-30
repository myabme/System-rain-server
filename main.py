import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- إعدادات الموقع السينمائي (Developed by Wilked) ---
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
            
            /* ضباب احترافي أسود وأبيض */
            .fog { position: absolute; width: 100%; height: 100%; z-index: 1; opacity: 0.15; background: url('https://cdn.pixabay.com/photo/2016/11/21/15/34/fog-1845173_960_720.png'); background-size: cover; animation: moveFog 100s linear infinite; }
            @keyframes moveFog { from { background-position: 0 0; } to { background-position: 10000px 0; } }

            /* تأثير المطر */
            .rain { position: absolute; width: 100%; height: 100%; z-index: 2; }
            .drop { position: absolute; background: rgba(255,255,255,0.1); width: 1px; height: 25px; top: -20px; animation: fall linear infinite; }
            @keyframes fall { to { transform: translateY(100vh); } }

            /* المحتوى */
            .main { position: relative; z-index: 3; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; color: #fff; text-align: center; background: radial-gradient(circle, rgba(0,0,0,0) 0%, rgba(0,0,0,0.8) 100%); }
            .dev { color: #5865F2; font-size: 0.9rem; font-weight: bold; letter-spacing: 5px; text-transform: uppercase; margin-bottom: 10px; text-shadow: 0 0 10px #5865F2; }
            h1 { font-size: 4rem; margin: 0; letter-spacing: 3px; font-weight: 900; }
            .glow { color: #fff; text-shadow: 0 0 20px #fff, 0 0 40px #5865F2; }
            p { color: #444; font-size: 1.2rem; margin-top: 15px; letter-spacing: 2px; }
            .status { margin-top: 30px; border: 1px solid #43b581; color: #43b581; padding: 8px 25px; border-radius: 50px; font-size: 0.8rem; font-weight: bold; background: rgba(67, 181, 129, 0.05); }
        </style>
    </head>
    <body>
        <div class="fog"></div>
        <div class="rain" id="rain"></div>
        <div class="main">
            <div class="dev">Developed by Wilked</div>
            <h1>Welcome to <span class="glow">Ráin Bot</span></h1>
            <p>EMBRACE THE STORM</p>
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

def run():
    # السطر ده هو اللي هيحل مشكلة الـ Not Found
    # بيخلي السيرفر يرد على أي بورت يفتحه Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# تشغيل الويب في الخلفية
Thread(target=run).start()

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ Ráinbot Online | Developed by Wilked')

@bot.command(name="موقع")
async def dashboard(ctx):
    await ctx.message.delete()
    # السكربت هيسحب الرابط تلقائياً من Railway
    url = os.environ.get('RAILWAY_STATIC_URL', 'rainbot.up.railway.app')
    await ctx.send(f"صفحة RáinBot : https://{url}")

@bot.command(name="مساعدة")
async def help_cmd(ctx):
    await ctx.message.delete()
    msg = (
        "**🌑 أوامر Ráinbot | Wilked Edition:**\n\n"
        "• `!موقع` : الدخول للوحة التحكم السينمائية.\n"
        "• `!قول [نص]` : إرسال رسالة مخفية بالبوت.\n"
        "• `!مسح [عدد]` : تنظيف الشات."
    )
    await ctx.send(msg)

@bot.command(name="قول")
async def say(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(message)

@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)

# تشغيل البوت بالتوكن
bot.run(os.getenv('DISCORD_TOKEN'))
