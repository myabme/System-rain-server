import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
import logging

# إيقاف رسائل التنبيه المزعجة في الكونسول
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <body style="background-color: #000; color: #5865F2; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0;">
        <div style="text-align: center; border: 2px solid #111; padding: 50px; border-radius: 20px; background: #050505; box-shadow: 0 0 20px #5865f233;">
            <h1 style="font-size: 4em; margin-bottom: 10px;">Ráinbot</h1>
            <p style="color: #888; font-size: 1.2em;">اللوحة السوداء قيد التشغيل..</p>
            <div style="background: #5865F2; color: white; padding: 10px 20px; border-radius: 5px; display: inline-block; margin-top: 20px;">Online</div>
        </div>
    </body>
    """

def run():
    # Railway محتاج يسمع للبورت هذا عشان ما يعطي Crash
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# تشغيل السيرفر في الخلفية
Thread(target=run).start()

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} Is Running!')
    await bot.change_presence(activity=discord.Game(name="Ráinbot | !مساعدة"))

@bot.command(name="مساعدة")
async def help_cmd(ctx):
    embed = discord.Embed(title="🌑 قائمة أوامر Ráinbot", color=0x000000)
    embed.add_field(name="!موقع", value="يفتح لك لوحة التحكم السوداء", inline=False)
    embed.add_field(name="!قول [نص]", value="يرسل كلامك باسم البوت", inline=False)
    embed.add_field(name="!مسح [عدد]", value="ينظف الشات", inline=False)
    await ctx.message.delete()
    await ctx.send(embed=embed)

@bot.command(name="موقع")
async def dashboard(ctx):
    await ctx.message.delete()
    # Railway بيعطيك الرابط في المتغير هذا تلقائياً
    url = os.environ.get('RAILWAY_STATIC_URL', 'انتظر ربط الدومين..')
    await ctx.send(f"🔗 **لوحة تحكم Ráinbot السوداء:**\nhttps://{url}")

@bot.command(name="قول")
async def say(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)

# تشغيل البوت بالتوكن
token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ وين التوكن؟ ضيف DISCORD_TOKEN في Variables حقت Railway")
