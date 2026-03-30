import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- واجهة Ráinbot (الموقع الزاحف) ---
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ráinbot Dashboard | Wilked</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;900&display=swap');
            body, html { margin: 0; padding: 0; width: 100%; height: 100%; background-color: #050505; overflow: hidden; font-family: 'Cairo', sans-serif; }
            .ocean { height: 5%; width: 100%; position: absolute; bottom: 0; left: 0; background: #01579b; z-index: 5; }
            .wave { background: url(https://s3-us-west-2.amazonaws.com/s.cdpn.io/85486/wave.svg) repeat-x; position: absolute; top: -198px; width: 6400px; height: 198px; animation: wave 7s cubic-bezier( 0.36, 0.45, 0.63, 0.53) infinite; }
            @keyframes wave { 0% { margin-left: 0; } 100% { margin-left: -1600px; } }
            .rain { position: absolute; width: 100%; height: 100%; z-index: 1; }
            .drop { position: absolute; background: rgba(255,255,255,0.08); width: 1px; height: 40px; top: -100px; animation: fall linear infinite; }
            @keyframes fall { to { transform: translateY(115vh); } }
            .container { position: relative; z-index: 10; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; text-align: center; }
            h1 { font-size: 5.5rem; margin: 0; color: #fff; text-shadow: 0 0 10px #fff; font-weight: 900; letter-spacing: 6px; }
            .dev-tag { color: #888; font-size: 0.65rem; font-weight: bold; letter-spacing: 6px; text-transform: uppercase; margin-top: -5px; opacity: 0.5; }
        </style>
    </head>
    <body>
        <audio autoplay loop id="rainAudio"><source src="https://www.soundjay.com/nature/rain-01.mp3" type="audio/mpeg"></audio>
        <div class="rain" id="rain"></div>
        <div class="container">
            <h1>RÁINBOT</h1>
            <div class="dev-tag">DEVELOPED BY WILKED</div>
        </div>
        <div class="ocean"><div class="wave"></div></div>
        <script>
            const container = document.getElementById('rain');
            for (let i = 0; i < 60; i++) {
                const drop = document.createElement('div');
                drop.className = 'drop';
                drop.style.left = Math.random() * 100 + 'vw';
                drop.style.animationDuration = (Math.random() * 1.5 + 1.0) + 's';
                drop.style.animationDelay = Math.random() * 3 + 's';
                container.appendChild(drop);
            }
            document.body.addEventListener('click', () => {
                const audio = document.getElementById('rainAudio');
                audio.play(); audio.volume = 0.3;
            }, { once: true });
        </script>
    </body>
    </html>
    """

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run).start()

# --- إعدادات البوت (بدون بادئة !) ---
intents = discord.Intents.all()
# خليت الـ Prefix فاضي عشان الأوامر تشتغل ككلمات عادية
bot = commands.Bot(command_prefix='', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} Is Online!')

# --- نظام تصحيح الأخطاء الذكي ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
        if ctx.command.name == "طرد" or ctx.command.name == "بند":
            embed = discord.Embed(title="❌ خطأ في الاستخدام", color=0xff0000)
            embed.description = f"يا وحش، لازم تمنشن الشخص عشان أقدر أسوي {ctx.command.name}.\n\n**مثال:** `{ctx.command.name} @عضو`"
            await ctx.send(embed=embed, delete_after=10)
    elif isinstance(error, commands.CommandNotFound):
        # هنا ممكن نضيف نظام اقتراح الأوامر لو كتب كلمة قريبة
        pass

# 1. أمر مساعدة
@bot.command(name="مساعدة")
async def help_cmd(ctx):
    embed = discord.Embed(title="🌑 أوامر Ráinbot", description="تحكم كامل بدون علامات - بواسطة **Wilked**", color=0xffffff)
    embed.add_field(name="🛡️ الإدارة", value="`مسح [عدد]`\n`طرد [@عضو]`\n`بند [@عضو]`", inline=False)
    embed.add_field(name="🔗 عام", value="`موقع`\n`قول [نص]`", inline=False)
    embed.set_footer(text="Developed by Wilked")
    await ctx.send(embed=embed)

# 2. أمر موقع (معدل عشان يشتغل غصب)
@bot.command(name="موقع")
async def site_link(ctx):
    # بيجيب الرابط اللي أنت حددته في Railway
    url = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'rainbot-production.up.railway.app')}"
    await ctx.send(f"🔗 **رابط الداشبورد الخاص بك:** {url}")

# 3. أمر مسح
@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ تم تنظيف `{amount}` رسالة.", delete_after=3)

# 4. أمر طرد
@bot.command(name="طرد")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None):
    if member is None:
        raise commands.MissingRequiredArgument(param=None)
    await member.kick()
    await ctx.send(f"👤 تم طرد {member.mention}")

# 5. أمر بند
@bot.command(name="بند")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None):
    if member is None:
        raise commands.MissingRequiredArgument(param=None)
    await member.ban()
    await ctx.send(f"🚫 تم تبنيد {member.mention}")

# 6. أمر قول
@bot.command(name="قول")
async def say(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

bot.run(os.getenv('DISCORD_TOKEN'))
