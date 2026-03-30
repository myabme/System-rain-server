import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- واجهة الموقع (مطر وضباب Developed by Wilked) ---
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>Ráinbot | Wilked</title>
        <style>
            body { margin: 0; background: #000; overflow: hidden; color: #fff; text-align: center; font-family: sans-serif; }
            .fog { position: absolute; width: 100%; height: 100%; opacity: 0.1; background: url('https://cdn.pixabay.com/photo/2016/11/21/15/34/fog-1845173_960_720.png'); animation: move 60s infinite; }
            @keyframes move { from { background-position: 0; } to { background-position: 1000px; } }
            .rain { position: absolute; width: 1px; height: 20px; background: rgba(255,255,255,0.2); animation: fall 0.5s linear infinite; }
            @keyframes fall { to { transform: translateY(100vh); } }
            .content { position: relative; z-index: 10; padding-top: 20vh; }
            h1 { font-size: 3rem; text-shadow: 0 0 20px #5865F2; }
        </style>
    </head>
    <body>
        <div class="fog"></div>
        <div class="content">
            <p style="letter-spacing: 5px; color: #5865F2;">DEVELOPED BY WILKED</p>
            <h1>Welcome to Ráin Bot</h1>
            <p>Status: Online & Ready</p>
        </div>
        <script>
            for(let i=0; i<100; i++) {
                let drop = document.createElement('div');
                drop.className = 'rain';
                drop.style.left = Math.random() * 100 + 'vw';
                drop.style.animationDelay = Math.random() * 2 + 's';
                document.body.appendChild(drop);
            }
        </script>
    </body>
    </html>
    """

def run():
    # Railway بيحتاج يسمع للبورت ده عشان يشيل Not Found
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run).start()

# --- إعدادات البوت (أوامر Wilked) ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is ready!')

@bot.command(name="مساعدة")
async def help_cmd(ctx):
    await ctx.send("**🌑 أوامر Ráinbot:**\n\n• `!موقع` : رابط لوحة التحكم.\n• `!قول [نص]` : البوت يتكلم.\n• `!مسح [عدد]` : تنظيف الشات.")

@bot.command(name="موقع")
async def site(ctx):
    url = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'rainbot.up.railway.app')}"
    await ctx.send(f"🔗 رابط الموقع: {url}")

@bot.command(name="قول")
async def say(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)

bot.run(os.getenv('DISCORD_TOKEN'))
