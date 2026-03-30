import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- إعدادات الواجهة الاحترافية (Ráinbot Dashboard) ---
app = Flask(__name__)

@app.route('/')
def home():
    # تصميم أسود ملكي فخم مع تأثيرات مطر وضباب Developed by Wilked
    return """
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ráinbot | Welcome</title>
        <style>
            body, html { margin: 0; padding: 0; width: 100%; height: 100%; background-color: #000; overflow: hidden; font-family: sans-serif; }
            
            /* طبقة الضباب (Fog) */
            .fog-wrapper { position: absolute; width: 100%; height: 100%; overflow: hidden; z-index: 1; opacity: 0.1; }
            .fog { position: absolute; top: 0; left: 0; width: 300%; height: 100%; background: url('https://cdn.pixabay.com/photo/2016/11/21/15/34/fog-1845173_960_720.png') repeat-x; background-size: contain; animation: fog-move 80s linear infinite; }
            @keyframes fog-move { from { transform: translateX(0); } to { transform: translateX(-50%); } }

            /* طبقة المطر (Rain) */
            .rain { position: absolute; width: 100%; height: 100%; z-index: 2; }
            .drop { position: absolute; background-color: rgba(255, 255, 255, 0.15); width: 1px; height: 20px; top: -20px; animation: fall linear infinite; }
            @keyframes fall { to { transform: translateY(100vh); } }

            /* المحتوى (Content) */
            .content { position: relative; z-index: 3; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; color: #fff; text-align: center; }
            .dev-name { position: absolute; top: 40px; font-size: 0.75rem; color: #5865F2; letter-spacing: 4px; text-transform: uppercase; font-weight: bold; }
            
            h1 { font-size: 3.5rem; margin: 0; letter-spacing: 2px; font-weight: 900; }
            .highlight { color: #fff; text-shadow: 0 0 15px #5865F2, 0 0 30px #5865F2; }
            
            p { color: #555; font-size: 1.1rem; margin-top: 10px; }
            .status { margin-top: 35px; color: #43b581; font-size: 0.8rem; font-weight: bold; border: 1px solid #43b581; padding: 6px 20px; border-radius: 50px; background: rgba(67, 181, 129, 0.05); }
        </style>
    </head>
    <body>
        <div class="fog-wrapper"><div class="fog"></div></div>
        <div class="rain" id="rain"></div>
        <div class="content">
            <div class="dev-name">Developed by Wilked</div>
            <h1>Welcome to <span class="highlight">Ráin Bot</span></h1>
            <p>Advanced Discord Management. Embrace the Storm.</p>
            <div class="status">● System Online</div>
        </div>
        <script>
            function makeItRain() {
                const container = document.getElementById('rain');
                for (let i = 0; i < 120; i++) {
                    const drop = document.createElement('div');
                    drop.className = 'drop';
                    drop.style.left = Math.random() * 100 + 'vw';
                    drop.style.animationDuration = (Math.random() * 0.5 + 0.4) + 's';
                    drop.style.animationDelay = Math.random() * 2 + 's';
                    container.appendChild(drop);
                }
            }
            window.onload = makeItRain;
        </script>
    </body>
    </html>
    """

def run_site():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# تشغيل الموقع في الخلفية
Thread(target=run_site).start()

# --- إعدادات البوت (Ráinbot) ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ Ráinbot Is Live | Developed by Wilked')
    await bot.change_presence(activity=discord.Game(name="Ráinbot | !مساعدة"))

@bot.command(name="موقع")
async def dashboard(ctx):
    await ctx.message.delete()
    domain = os.environ.get('RAILWAY_STATIC_URL', 'rainbot.up.railway.app')
    await ctx.send(f"صفحة RáinBot : https://{domain}")

@bot.command(name="مساعدة")
async def help_cmd(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title="🌑 قائمة أوامر Ráinbot", description="نظام إدارة متطور بواسطة Wilked", color=0x000000)
    embed.add_field(name="!موقع", value="رابط لوحة التحكم السينمائية", inline=False)
    embed.add_field(name="!قول [نص]", value="إرسال رسالة باسم البوت (مخفية)", inline=False)
    embed.add_field(name="!مسح [عدد]", value="تنظيف الشات من الرسائل المزعجة", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="قول")
async def say(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(message)

@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)

# تشغيل البوت
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
