import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- واجهة Ráinbot الاحترافية (تعديل أبو مشاري) ---
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
            .rain { position: absolute; width: 100%; height: 100%; z-index: 1; }
            .drop { position: absolute; background: rgba(255,255,255,0.08); width: 1px; height: 40px; top: -100px; animation: fall linear infinite; }
            @keyframes fall { to { transform: translateY(115vh); } }
            .container { position: relative; z-index: 10; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; text-align: center; }
            h1 { font-size: 5.5rem; margin: 0; color: #fff; text-shadow: 0 0 10px #fff; font-weight: 900; letter-spacing: 6px; }
            .dev-tag { color: #888; font-size: 0.65rem; font-weight: bold; letter-spacing: 6px; text-transform: uppercase; margin-top: -5px; opacity: 0.5; }
            .btn-dashboard { margin-top: 55px; padding: 10px 32px; background: transparent; color: #fff; border: 1px solid rgba(255,255,255,0.4); border-radius: 50px; font-size: 0.95rem; font-weight: bold; cursor: pointer; text-decoration: none; transition: 0.4s; }
            .btn-dashboard:hover { background: #fff; color: #000; box-shadow: 0 0 20px #fff; }
        </style>
    </head>
    <body>
        <audio autoplay loop id="rainAudio"><source src="https://www.soundjay.com/nature/rain-01.mp3" type="audio/mpeg"></audio>
        <div class="rain" id="rain"></div>
        <div class="container">
            <h1>RÁINBOT</h1>
            <div class="dev-tag">DEVELOPED BY WILKED</div>
            <a href="/dashboard" class="btn-dashboard">دخول لوحة التحكم</a>
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

@app.route('/dashboard')
def dashboard():
    return """
    <body style="background:#000; color:#fff; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <div style="text-align:center; border:1px solid #333; padding:50px; border-radius:20px; box-shadow: 0 0 20px rgba(255,255,255,0.05);">
            <h2 style="text-shadow: 0 0 10px #fff; letter-spacing:3px; font-size:1.5rem;">WILKED DASHBOARD</h2>
            <p style="color:#666; font-size:0.9rem;">قريباً: التحكم الكامل في إعدادات السيرفر</p>
            <br>
            <a href="/" style="color:#fff; text-decoration:none; border:1px solid rgba(255,255,255,0.5); padding:6px 18px; border-radius:50px; font-size:0.75rem;">رجوع للرئيسية</a>
        </div>
    </body>
    """

def run():
    # هذا السطر يحل مشكلة Not Found في ريلواي
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run).start()

# --- إعدادات البوت (بدون بادئة وبدون كلمة زاحف) ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} متصل الآن!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # معالجة الأوامر ككلمات عادية
    valid_commands = ['مساعدة', 'موقع', 'مسح', 'طرد', 'بند', 'قول']
    if message.content.split()[0] in valid_commands:
        await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="❌ خطأ في الاستخدام", color=0xffffff)
        embed.description = f"تأكد من كتابة الأمر بشكل صحيح ومنشن العضو.\n\n**مثال:** `{ctx.command.name} @عضو`"
        await ctx.send(embed=embed, delete_after=10)

@bot.command(name="مساعدة")
async def help_cmd(ctx):
    embed = discord.Embed(title="🌑 قائمة الأوامر", description="إدارة السيرفر بواسطة **Wilked**", color=0xffffff)
    embed.add_field(name="🛡️ الإدارة", value="`مسح [عدد]`\n`طرد [@عضو]`\n`بند [@عضو]`", inline=False)
    embed.add_field(name="🔗 عام", value="`موقع`\n`قول [نص]`", inline=False)
    embed.set_footer(text="Developed by Wilked")
    await ctx.send(embed=embed)

@bot.command(name="موقع")
async def site_link(ctx):
    await ctx.send("🔗 **رابط لوحة التحكم:** https://system-rain-server-production.up.railway.app")

@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ تم مسح `{amount}` رسالة.", delete_after=3)

@bot.command(name="طرد")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None):
    if member:
        await member.kick()
        await ctx.send(f"👤 تم طرد {member.mention}")
    else:
        await ctx.send("منشن العضو اللي تبي تطرده")

@bot.command(name="بند")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None):
    if member:
        await member.ban()
        await ctx.send(f"🚫 تم تبنيد {member.mention}")
    else:
        await ctx.send("منشن العضو اللي تبي تبنده")

@bot.command(name="قول")
async def say(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

bot.run(os.getenv('DISCORD_TOKEN'))
