import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- إعدادات الموقع الفخم ---
app = Flask(__name__)

@app.route('/')
def home():
    # تصميم متوافق مع Safari والجوالات (Responsive)
    return """
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ráinbot Dashboard</title>
        <style>
            body { background-color: #000; color: #fff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .card { text-align: center; border: 1px solid #222; padding: 40px; border-radius: 15px; background: #0a0a0a; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
            h1 { color: #5865F2; font-size: 2.5rem; margin-bottom: 5px; letter-spacing: 2px; }
            p { color: #666; margin-bottom: 25px; }
            .status-btn { background: #5865F2; color: white; padding: 10px 25px; border-radius: 20px; font-weight: bold; text-decoration: none; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Ráinbot</h1>
            <p>The Black Dashboard is Active</p>
            <div class="status-btn">Online</div>
        </div>
    </body>
    </html>
    """

def run():
    # بورت Railway الإلزامي
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# تشغيل الويب سيرفر في الخلفية
Thread(target=run).start()

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ Ráinbot جاهز للاستخدام يا وحش!')

@bot.command(name="موقع")
async def dashboard(ctx):
    await ctx.message.delete()
    
    # جلب رابط المشروع من Railway
    # ملاحظة: تأكد من إضافة دومين في Railway (Settings -> Domains)
    raw_url = os.environ.get('RAILWAY_STATIC_URL', 'rainbot-production.up.railway.app')
    
    # التأكد من أن الرابط يبدأ بـ https عشان يفتح في Safari
    full_url = f"https://{raw_url}"
    
    # إرسال الرسالة بالشكل اللي طلبته
    await ctx.send(f"صفحة RáinBot : {full_url}")

@bot.command(name="مساعدة")
async def help_cmd(ctx):
    await ctx.message.delete()
    msg = (
        "**🌑 أوامر Ráinbot:**\n"
        "• `!موقع` : رابط لوحة التحكم.\n"
        "• `!قول [نص]` : إرسال رسالة.\n"
        "• `!مسح [عدد]` : تنظيف الشات."
    )
    await ctx.send(msg)

@bot.command(name="قول")
async def say(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

# تشغيل البوت
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
