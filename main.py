import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- واجهة Ráinbot الاحترافية (تحديث Wilked) ---
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
    # حل مشكلة Not Found - ريلواي يحتاج PORT المتغير
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run).start()

# --- إعدادات البوت (أوامر Wilked الجديدة) ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} جاهز للعمل!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # قائمة الأوامر المسموحة بدون علامات
    valid_commands = ['مساعدة', 'موقع', 'مسح', 'طرد', 'بنعالي', 'ر', 'قول']
    if message.content.split()[0] in valid_commands:
        await bot.process_commands(message)

# 1. مساعدة
@bot.command(name="مساعدة")
async def help_cmd(ctx):
    embed = discord.Embed(title="🌑 قائمة الأوامر", description="تطوير: **Wilked**", color=0xffffff)
    embed.add_field(name="🛡️ الإدارة", value="`مسح [عدد]`\n`طرد [@عضو]`\n`بنعالي [@عضو]`\n`ر [@عضو] [اسم الرتبة]`", inline=False)
    embed.add_field(name="🔗 عام", value="`موقع`\n`قول [نص]`", inline=False)
    await ctx.send(embed=embed)

# 2. موقع (يصلح مشكلة الرابط)
@bot.command(name="موقع")
async def site_link(ctx):
    url = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'system-rain-server-production.up.railway.app')}"
    await ctx.send(f"🔗 **رابط الموقع:** {url}")

# 3. مسح
@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ تم المسح.", delete_after=2)

# 4. طرد
@bot.command(name="طرد")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None):
    if member:
        await member.kick()
        await ctx.send(f"👤 تم الطرد.")
    else:
        await ctx.send("منشن الشخص يا وحش!")

# 5. بنعالي (الباند سابقاً)
@bot.command(name="بنعالي")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None):
    if member:
        await member.ban()
        await ctx.send(f"🚫 بنعالي.")
    else:
        await ctx.send("منشن الشخص اللي تبي تعطيه بنعالي!")

# 6. ر (إعطاء رتبة)
@bot.command(name="ر")
@commands.has_permissions(manage_roles=True)
async def give_role(ctx, member: discord.Member = None, *, role: discord.Role = None):
    if member and role:
        await member.add_roles(role)
        await ctx.send(f"✅ تم إعطاء رتبة {role.name} لـ {member.mention}")
    else:
        await ctx.send("الاستخدام: `ر @عضو @الرتبة`")

# 7. قول
@bot.command(name="قول")
async def say(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

bot.run(os.getenv('DISCORD_TOKEN'))
