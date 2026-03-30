import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- واجهة Ráinbot (أبيض وأسود - مطر خفيف) ---
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ráinbot Dashboard</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;900&display=swap');
            
            body, html { 
                margin: 0; padding: 0; width: 100%; height: 100%; 
                background-color: #000; overflow: hidden; 
                font-family: 'Cairo', sans-serif; color: #fff;
            }

            /* مطر خفيف جداً */
            .rain { position: absolute; width: 100%; height: 100%; z-index: 1; }
            .drop { 
                position: absolute; background: rgba(255,255,255,0.15); 
                width: 1px; height: 20px; top: -100px; 
                animation: fall linear infinite; 
            }
            @keyframes fall { to { transform: translateY(110vh); } }

            .container { 
                position: relative; z-index: 10; display: flex; 
                flex-direction: column; align-items: center; 
                justify-content: center; height: 100vh; text-align: center; 
            }

            h1 { 
                font-size: 5rem; margin: 0; color: #fff; 
                text-shadow: 0 0 15px rgba(255,255,255,0.4); 
                font-weight: 900; letter-spacing: 8px;
            }

            .status { font-size: 1rem; color: #666; margin-top: 10px; }

            /* زر دخول الداشبورد */
            .btn-enter {
                margin-top: 40px; padding: 12px 40px; 
                background: transparent; color: #fff; 
                border: 1px solid #fff; border-radius: 0px; 
                font-size: 1rem; cursor: pointer; 
                text-decoration: none; transition: 0.5s;
                letter-spacing: 2px;
            }
            .btn-enter:hover { background: #fff; color: #000; }
        </style>
    </head>
    <body>
        <audio autoplay loop id="rainAudio">
          <source src="https://www.soundjay.com/nature/rain-01.mp3" type="audio/mpeg">
        </audio>

        <div class="rain" id="rain"></div>
        
        <div class="container">
            <h1>RÁINBOT</h1>
            <p class="status">STATUS: ONLINE & READY</p>
            <a href="/dashboard" class="btn-enter">ENTER DASHBOARD</a>
        </div>

        <script>
            // إنشاء مطر خفيف (عدد قطرات أقل)
            const container = document.getElementById('rain');
            for (let i = 0; i < 30; i++) {
                const drop = document.createElement('div');
                drop.className = 'drop';
                drop.style.left = Math.random() * 100 + 'vw';
                drop.style.animationDuration = (Math.random() * 2 + 2) + 's';
                drop.style.animationDelay = Math.random() * 5 + 's';
                container.appendChild(drop);
            }

            // تشغيل الصوت عند أول لمسة للشاشة (ضروري للمتصفحات)
            document.body.addEventListener('click', () => {
                const audio = document.getElementById('rainAudio');
                audio.play();
                audio.volume = 0.2; // صوت هادئ جداً
            }, { once: true });
        </script>
    </body>
    </html>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <body style="background:#000; color:#fff; font-family:sans-serif; display:flex; flex-direction:column; justify-content:center; align-items:center; height:100vh; margin:0;">
        <h2 style="letter-spacing:5px; border-bottom:1px solid #333; padding-bottom:10px;">DASHBOARD CONTROL</h2>
        <p style="color:#444;">قريباً: جميع أدوات التحكم بالسيرفر هنا</p>
        <a href="/" style="color:#666; text-decoration:none; margin-top:20px; font-size:0.8rem;">BACK TO HOME</a>
    </body>
    """

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run).start()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} is online!')

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    valid_commands = ['مساعدة', 'موقع', 'مسح', 'طرد', 'بنعالي', 'ر', 'قول']
    if message.content.split()[0] in valid_commands:
        await bot.process_commands(message)

# أوامر البوت
@bot.command(name="مساعدة")
async def help_cmd(ctx):
    embed = discord.Embed(title="🌑 قائمة الأوامر", color=0xffffff)
    embed.add_field(name="الإدارة", value="`مسح` | `طرد` | `بنعالي` | `ر`", inline=False)
    embed.add_field(name="عام", value="`موقع` | `قول`", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="موقع")
async def site_link(ctx):
    await ctx.send(f"🔗 رابط الموقع: https://{os.environ.get('RAILWAY_STATIC_URL', 'rainbot.up.railway.app')}")

bot.run(os.getenv('DISCORD_TOKEN'))
