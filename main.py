import discord
import os
from flask import Flask, request
from threading import Thread

# --- واجهة الموقع (ستايل بروبوت - أسود ملكي) ---
app = Flask(__name__)
client = discord.Client(intents=discord.Intents.all())
admin_role_id = None 

@app.route('/')
def home():
    return """
    <body onclick="var a=document.getElementById('r');a.volume=0.1;a.play()" style="background:#000;color:#fff;overflow:hidden;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;cursor:pointer;">
        <audio id="r" loop><source src="https://www.soundjay.com/nature/rain-01.mp3"></audio>
        <h1 style="letter-spacing:15px;font-size:4rem;margin:0;">RÁINBOT</h1>
        <p style="color:#444;letter-spacing:5px;margin-bottom:30px;">PREMIUM DISCORD SYSTEM</p>
        <a href="/dashboard" style="color:#fff;border:1px solid #fff;padding:12px 60px;text-decoration:none;transition:0.5s;letter-spacing:2px;">DASHBOARD</a>
    </body>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <body style="background:#0a0a0a;color:#fff;font-family:sans-serif;padding:40px;display:flex;flex-direction:column;align-items:center;">
        <h1 style="letter-spacing:5px;border-bottom:1px solid #1a1a1a;width:100%;text-align:center;padding-bottom:20px;">CONTROL PANEL</h1>
        
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;width:95%;max-width:1000px;margin-top:40px;">
            
            <div style="background:#000;border:1px solid #1a1a1a;padding:30px;border-radius:5px;">
                <h2 style="font-size:1rem;color:#555;letter-spacing:2px;margin-bottom:20px;">SETTINGS</h2>
                <p style="font-size:0.8rem;color:#888;">تحديد رتبة الإدارة (ID):</p>
                <input type="text" id="rid" placeholder="Role ID" style="width:100%;padding:12px;background:#0a0a0a;border:1px solid #222;color:#fff;margin-bottom:15px;">
                <button onclick="fetch('/api/set-role?id='+document.getElementById('rid').value).then(()=>alert('✅ Saved'))" style="width:100%;padding:12px;background:#fff;color:#000;border:none;cursor:pointer;font-weight:bold;">CONFIRM ROLE</button>
                <div style="margin-top:30px;opacity:0.2;">
                    <p style="font-size:0.7rem;">ADD COMMANDS (SOON)</p>
                </div>
            </div>

            <div style="background:#000;border:1px solid #1a1a1a;padding:30px;border-radius:5px;">
                <h2 style="font-size:1rem;color:#555;letter-spacing:2px;margin-bottom:20px;">COMMANDS LIST</h2>
                <div style="display:grid;gap:10px;max-height:400px;overflow-y:auto;padding-right:10px;">
                    <div style="background:#0a0a0a;padding:15px;border-left:3px solid #fff;">
                        <b style="font-size:0.9rem;">مسح</b> <span style="color:#444;font-size:0.7rem;">- مسح الرسائل</span>
                    </div>
                    <div style="background:#0a0a0a;padding:15px;border-left:3px solid #fff;">
                        <b style="font-size:0.9rem;">طرد</b> <span style="color:#444;font-size:0.7rem;">- طرد عضو من السيرفر</span>
                    </div>
                    <div style="background:#0a0a0a;padding:15px;border-left:3px solid #fff;">
                        <b style="font-size:0.9rem;">بنعالي</b> <span style="color:#444;font-size:0.7rem;">- حظر نهائي (بان)</span>
                    </div>
                    <div style="background:#0a0a0a;padding:15px;border-left:3px solid #fff;">
                        <b style="font-size:0.9rem;">ر</b> <span style="color:#444;font-size:0.7rem;">- إعطاء رتبة (@عضو @رتبة)</span>
                    </div>
                    <div style="background:#0a0a0a;padding:15px;border-left:3px solid #fff;">
                        <b style="font-size:0.9rem;">قول</b> <span style="color:#444;font-size:0.7rem;">- إرسال رسالة باسم البوت</span>
                    </div>
                    <div style="background:#0a0a0a;padding:15px;border-left:3px solid #fff;">
                        <b style="font-size:0.9rem;">مساعدة</b> <span style="color:#444;font-size:0.7rem;">- عرض القائمة في الديسكورد</span>
                    </div>
                    <div style="background:#0a0a0a;padding:15px;border-left:3px solid #fff;">
                        <b style="font-size:0.9rem;">موقع</b> <span style="color:#444;font-size:0.7rem;">- رابط الداشبورد</span>
                    </div>
                </div>
            </div>
        </div>
        <a href="/" style="margin-top:50px;color:#222;text-decoration:none;font-size:0.8rem;letter-spacing:3px;">BACK TO HOME</a>
    </body>
    """

@app.route('/api/set-role')
def set_role():
    global admin_role_id
    admin_role_id = request.args.get('id')
    return {"status": "ok"}

# --- نظام معالجة الأوامر ---
@client.event
async def on_ready():
    print(f'✅ {client.user} Connected')

@client.event
async def on_message(message):
    if message.author == client.user: return
    
    msg = message.content.strip().split()
    if not msg: return
    cmd = msg[0]

    # فحص الإدارة
    auth = True
    if admin_role_id:
        if admin_role_id not in [str(r.id) for r in message.author.roles] and not message.author.guild_permissions.administrator:
            auth = False

    # الأوامر
    if cmd == 'مساعدة':
        embed = discord.Embed(title="🌑 Commands List", color=0x000000)
        embed.add_field(name="Admin", value="`مسح` `طرد` `بنعالي` `ر`", inline=False)
        embed.add_field(name="General", value="`قول` `موقع`", inline=False)
        await message.channel.send(embed=embed)

    elif cmd == 'مسح' and auth:
        num = int(msg[1]) if len(msg) > 1 else 5
        await message.channel.purge(limit=num + 1)
        await message.channel.send(f"✅ Cleared {num}", delete_after=2)

    elif cmd == 'طرد' and auth:
        if message.mentions:
            await message.mentions[0].kick()
            await message.channel.send(f"👤 Kicked {message.mentions[0].mention}")

    elif cmd == 'بنعالي' and auth:
        if message.mentions:
            await message.mentions[0].ban()
            await message.channel.send(f"🚫 Banned {message.mentions[0].mention}")

    elif cmd == 'ر' and auth:
        if len(message.mentions) > 0 and len(message.role_mentions) > 0:
            await message.mentions[0].add_roles(message.role_mentions[0])
            await message.channel.send(f"✅ Role Added")

    elif cmd == 'قول':
        await message.delete()
        await message.channel.send(" ".join(msg[1:]))

    elif cmd == 'موقع':
        await message.channel.send(f"🔗 https://{os.environ.get('RAILWAY_STATIC_URL', 'rainbot.up.railway.app')}")

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    Thread(target=run).start()
    client.run(os.getenv('DISCORD_TOKEN'))
 
