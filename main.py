import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask, request
from threading import Thread

# --- واجهة الداشبورد (تصميم السينما: أبيض وأسود + مطر وصوت هادئ) ---
app = Flask(__name__)
bot = None
admin_roles = [] 

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>Ráinbot | Home</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;900&display=swap');
            body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: #000; overflow: hidden; font-family: 'Cairo', sans-serif; color: #fff; }
            
            /* المطر الخفيف */
            .rain { position: absolute; width: 100%; height: 100%; z-index: 1; }
            .drop { position: absolute; background: rgba(255,255,255,0.1); width: 1px; height: 20px; top: -100px; animation: fall linear infinite; }
            @keyframes fall { to { transform: translateY(110vh); } }

            .container { position: relative; z-index: 10; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; text-align: center; }
            h1 { font-size: 5rem; font-weight: 900; letter-spacing: 12px; margin: 0; text-shadow: 0 0 20px rgba(255,255,255,0.2); }
            .btn { margin-top: 40px; padding: 12px 50px; background: transparent; color: #fff; border: 1px solid #fff; text-decoration: none; transition: 0.5s; letter-spacing: 2px; cursor: pointer; }
            .btn:hover { background: #fff; color: #000; box-shadow: 0 0 30px #fff; }
            .mute-hint { position: absolute; bottom: 20px; font-size: 0.7rem; color: #333; }
        </style>
    </head>
    <body>
        <audio autoplay loop id="rainAudio">
            <source src="https://www.soundjay.com/nature/rain-01.mp3" type="audio/mpeg">
        </audio>

        <div class="rain" id="rain"></div>
        <div class="container">
            <h1>RÁINBOT</h1>
            <a href="/dashboard" class="btn">ENTER SYSTEM</a>
            <div class="mute-hint">CLICK ANYWHERE TO ACTIVATE SOUND</div>
        </div>

        <script>
            // إنشاء قطرات المطر (خفيفة)
            const container = document.getElementById('rain');
            for (let i = 0; i < 40; i++) {
                const drop = document.createElement('div');
                drop.className = 'drop';
                drop.style.left = Math.random() * 100 + 'vw';
                drop.style.animationDuration = (Math.random() * 2 + 2) + 's';
                drop.style.animationDelay = Math.random() * 5 + 's';
                container.appendChild(drop);
            }

            // تشغيل الصوت بهدوء عند أول ضغطة
            document.body.addEventListener('click', () => {
                const audio = document.getElementById('rainAudio');
                audio.volume = 0.15; // مستوى الصوت 15% (هادئ جداً)
                audio.play();
            }, { once: true });
        </script>
    </body>
    </html>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <body style="background:#000; color:#fff; font-family:'Cairo', sans-serif; display:flex; flex-direction:column; align-items:center; padding-top:50px;">
        <h2 style="letter-spacing:5px; border-bottom:1px solid #111; width:100%; text-align:center; padding-bottom:20px;">DASHBOARD</h2>
        <div style="display:grid; grid-template-columns:1fr; gap:25px; width:90%; max-width:500px; margin-top:40px;">
            <div style="border:1px solid #222; padding:20px; text-align:center;">
                <h3 style="font-size:0.8rem; letter-spacing:2px;">ADMIN ROLE ID</h3>
                <input type="text" id="roleId" placeholder="Enter ID" style="background:#111; border:1px solid #333; color:#fff; padding:10px; width:80%; text-align:center; margin-bottom:15px;">
                <button onclick="saveRole()" style="background:#fff; color:#000; border:none; padding:10px 30px; cursor:pointer; width:85%; font-weight:bold;">CONFIRM ROLE</button>
            </div>
            <div style="border:1px solid #111; padding:20px; text-align:center; opacity:0.3;">
                <h3 style="font-size:0.7rem; letter-spacing:4px;">CUSTOM COMMANDS SOON</h3>
            </div>
        </div>
        <script>
            async function saveRole() {
                const id = document.getElementById('roleId').value;
                if(!id) return alert("حط الآيدي أولاً");
                const r = await fetch(`/api/set-role?id=${id}`);
                const d = await r.json();
                alert(d.message);
            }
        </script>
        <a href="/" style="margin-top:50px; color:#333; text-decoration:none; font-size:0.8rem;">BACK TO HOME</a>
    </body>
    """

@app.route('/api/set-role')
def set_role():
    role_id = request.args.get('id')
    if role_id:
        global admin_roles
        admin_roles = [int(role_id)]
        return {"status": "success", "message": "تم اعتماد رتبة الإدارة بنجاح"}
    return {"status": "error", "message": "الآيدي غير صحيح"}

# --- إعدادات البوت (التحكم الكامل) ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='', intents=intents, help_command=None)

def is_admin(ctx):
    if not admin_roles: return True
    return any(r.id in admin_roles for r in ctx.author.roles)

@bot.event
async def on_ready():
    print(f'✅ Ráinbot is up and running!')

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    # نظام التعرف على الأوامر بدون بادئة
    valid_cmds = ['مساعدة', 'مسح', 'طرد', 'بنعالي', 'ر', 'قول', 'موقع']
    content = message.content.strip().split()
    if content and content[0] in valid_cmds:
        await bot.process_commands(message)

# الأوامر المباشرة
@bot.command(name="مسح")
async def clear(ctx, amount: int = 5):
    if is_admin(ctx):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send("✅ تم تنظيف الشات", delete_after=2)

@bot.command(name="بنعالي")
async def ban(ctx, member: discord.Member = None):
    if is_admin(ctx) and member:
        await member.ban()
        await ctx.send("🚫 تم إعطاء بنعالي بنجاح.")

@bot.command(name="ر")
async def role(ctx, member: discord.Member = None, role: discord.Role = None):
    if is_admin(ctx) and member and role:
        await member.add_roles(role)
        await ctx.send(f"✅ تم إعطاء رتبة **{role.name}** لـ {member.mention}")

@bot.command(name="قول")
async def say(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

@bot.command(name="موقع")
async def site(ctx):
    url = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'system-rain-server-production.up.railway.app')}"
    await ctx.send(f"🔗 **لوحة التحكم:**\n{url}")

# تشغيل الفلاسك والبوت
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(os.getenv('DISCORD_TOKEN'))
