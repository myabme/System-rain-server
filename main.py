import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- إعدادات الموقع الفخم ---
app = Flask(__name__)

@app.route('/')
def home():
    # تصميم أسود ملكي متوافق مع Safari مع إضافة Developed by Wilked
    return """
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ráinbot Dashboard</title>
        <style>
            body { background-color: #000; color: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; overflow: hidden; }
            .dev-tag { position: absolute; top: 20px; font-size: 0.8rem; color: #5865F2; letter-spacing: 2px; text-transform: uppercase; font-weight: bold; }
            .main-box { text-align: center; border: 1px solid #111; padding: 50px; border-radius: 30px; background: #050505; box-shadow: 0 0 50px rgba(88, 101, 242, 0.05); }
            h1 { color: #fff; font-size: 3.5rem; margin: 0; letter-spacing: 4px; }
            p { color: #444; font-size: 1rem; margin-top: 10px; font-weight: 300; }
            .status { margin-top: 20px; color: #43b581; font-size: 0.9rem; font-weight: bold; text-transform: uppercase; border: 1px solid #43b581; padding: 5px 15px; border-radius: 50px; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="dev-tag">Developed by Wilked</div>
        <div class="main-box">
            <h1>Ráinbot</h1>
            <p>Advanced Discord Management System</p>
            <div class="status">● System Active</div>
        </div>
    </body>
    </html>
    """

def run_server():
    # تشغيل السيرفر على بورت Railway التلقائي
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# تشغيل الويب في خيط منفصل
Thread(target=run_server).start()

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ Ráinbot Is Online | Developed by Wilked')

@bot.command(name="موقع")
async def send_link(ctx):
    await ctx.message.delete()
    # جلب رابط الدومين من إعدادات ريلواي
    domain = os.environ.get('RAILWAY_STATIC_URL', 'rainbot-production.up.railway.app')
    # إرسال الرسالة المطلوبة تماماً
    await ctx.send(f"صفحة RáinBot : https://{domain}")

@bot.command(name="مساعدة")
async def help_cmd(ctx):
    await ctx.message.delete()
    msg = (
        "**🌑 أوامر Ráinbot العربية:**\n\n"
        "• `!موقع` : رابط لوحة التحكم الفخمة.\n"
        "• `!قول [نص]` : إرسال رسالة مخفية.\n"
        "• `!مسح [عدد]` : تنظيف الشات."
    )
    await ctx.send(msg)

@bot.command(name="قول")
async def say(ctx, *, message):
    await ctx.message.delete()
    await ctx.send(message)

# تشغيل البوت باستخدام التوكن المخفي
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
