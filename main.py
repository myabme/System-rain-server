import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask, request
from threading import Thread

# --- واجهة الموقع (مطر + صوت + أبيض وأسود) ---
app = Flask(__name__)
bot = None
admin_role_id = None 

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>Ráinbot</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@900&display=swap');
            body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: #000; overflow: hidden; font-family: 'Cairo', sans-serif; cursor: pointer; }
            .rain { position: absolute; width: 100%; height: 100%; z-index: 1; pointer-events: none; }
            .drop { position: absolute; background: rgba(255,255,255,0.1); width: 1px; height: 20px; top: -100px; animation: fall linear infinite; }
            @keyframes fall { to { transform: translateY(110vh); } }
            .container { position: relative; z-index: 10; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }
            h1 { font-size: 5rem; color: #fff; letter-spacing: 12px; margin: 0; text-shadow: 0 0 20px rgba(255,255,255,0.3); }
            .btn { margin-top: 30px; padding: 12px 45px; background: transparent; color: #fff; border: 1px solid #fff; text-decoration: none; transition: 0.4s; }
            .btn:hover { background: #fff; color: #000; }
            .hint { color: #222; font-size: 0.7rem; margin-top: 15px; letter-spacing: 2px; }
        </style>
    </head>
    <body onclick="playRain()">
        <audio id="rainAudio" loop><source src="https://www.soundjay.com/nature/rain-01.mp3" type="audio/mpeg"></audio>
        <div class="rain" id="rain"></div>
        <div class="container">
            <h1>RÁINBOT</h1>
            <a href="/dashboard" class="btn">OPEN DASHBOARD</a>
            <div class="hint">CLICK ANYWHERE FOR SOUND</div>
        </div>
        <script>
            function playRain() { 
                var audio = document.getElementById('rainAudio');
                audio.volume = 0.15; audio.play(); 
            }
            const container = document.getElementById('rain');
            for (let i = 0; i < 40; i++) {
                const drop = document.createElement('div');
                drop.className = 'drop';
                drop.style.left = Math.random() * 100 + 'vw';
                drop.style.animationDuration = (Math.random() * 2 + 2) + 's';
                container.appendChild(drop);
            }
        </script>
    </body>
    </html>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <body style="background:#000; color:#fff; font-family:sans-serif; display:flex; flex-direction:column; align-items:center; padding:50px;">
        <h2 style="letter-spacing:5px; border-bottom:1px solid #111; width:100%; text-align:center; padding-bottom:20px;">DASHBOARD TOOLS</h2>
        
        <div style="width:90%; max-width:600px; margin-top:30px; display:grid; gap:20px;">
            <div style="border:1px solid #222; padding:20px;">
                <h3 style="font-size:0.8rem; letter-spacing:2px;">تعيين رتب الإدارة</h3>
                <input type="text" id="rid" placeholder="Paste Role ID Here" style="width:100%; padding:10px; background:#111; border:1px solid #333; color:#fff; margin:10px 0;">
                <button onclick="save()" style="width:100%; padding:10px; background:#fff; color:#000; border:none; cursor:pointer; font-weight:bold;">CONFIRM ROLE</button>
            </div>

            <div style="border:1px solid #222; padding:20px;">
                <h3 style="font-size:0.8rem; letter-spacing:2px;">إضافة أوامر جديدة</h3>
                <p style="color:#333; font-size:0.7rem;">سيتم ربطها بالسكربت تلقائياً</p>
                <button style="width:100%; padding:10px; background:none; border:1px solid #333; color:#444; cursor:not-allowed;">BUILDER SOON</button>
            </div>

            <div style="border:1px solid #111; padding:20px; text-align:center;">
                <h3 style="font-size:0.8rem; letter-spacing:8px; color:#222;">SOON...</h3>
            </div>
        </div>

        <script>
            async function save() {
                const id = document.getElementById('rid').value;
                const r = await fetch(`/api/set-role?id=${id}`);
                const d = await r.json();
                alert(d.message);
            }
        </script>
    </body>
    """

@app.route('/api/set-role')
def set_role():
    global admin_role_id
    admin_role_id = request.args.get('id')
    return {"status": "success", "message": "تم تحديد رتبة الإدارة بنجاح"}

# --- إعدادات البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} Ready!')

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    
    cmds = ['مسح', 'طرد', 'بنعالي', 'ر', 'قول', 'موقع', 'مساعدة']
    content = message.content.strip().split()
    if not content: return
    
    if content[0] in cmds:
        # فحص رتبة الإدارة
        if admin_role_id:
            user_roles = [str(r.id) for r in message.author.roles]
            if admin_role_id not in user_roles and not message.author.guild_permissions.administrator:
                return await message.channel.send("❌ رتبتك ما تسمح لك!")
        
        await bot.process_commands(message)

# الأوامر المباشرة
@bot.command(name="مسح")
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send("🧹 تم التنظيف", delete_after=2)

@bot.command(name="بنعالي")
async def ban(ctx, member: discord.Member = None):
    if member: await member.ban(); await ctx.send("🚫 بنعالي.")

@bot.command(name="ر")
async def role(ctx, member: discord.Member = None, role: discord.Role = None):
    if member and role:
        await member.add_roles(role)
        await ctx.send(f"✅ تم إعطاء رتبة **{role.name}**")

@bot.command(name="قول")
async def say(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

@bot.command(name="موقع")
async def site(ctx):
    await ctx.send(f"🔗 رابط الموقع:\nhttps://{os.environ.get('RAILWAY_STATIC_URL', 'check-railway')}")

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.run(os.getenv('DISCORD_TOKEN'))
