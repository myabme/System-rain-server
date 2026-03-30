import discord
import os
import asyncio
from flask import Flask, request
from threading import Thread

# --- واجهة الموقع (التصميم اللي طلبته: أبيض وأسود + مطر) ---
app = Flask(__name__)
client = discord.Client(intents=discord.Intents.all())
admin_role_id = None 

@app.route('/')
def home():
    return """
    <body onclick="var a=document.getElementById('r');a.volume=0.1;a.play()" style="background:#000;color:#fff;overflow:hidden;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;cursor:pointer;">
        <audio id="r" loop><source src="https://www.soundjay.com/nature/rain-01.mp3"></audio>
        <h1 style="letter-spacing:15px;font-size:4rem;">RÁINBOT</h1>
        <a href="/dashboard" style="color:#fff;border:1px solid #fff;padding:10px 40px;text-decoration:none;margin-top:20px;">ENTER DASHBOARD</a>
        <p style="color:#222;font-size:0.7rem;margin-top:20px;">CLICK FOR RAIN SOUND</p>
    </body>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <body style="background:#000;color:#fff;font-family:sans-serif;display:flex;flex-direction:column;align-items:center;padding:40px;">
        <h2 style="border-bottom:1px solid #111;width:100%;text-align:center;padding-bottom:20px;letter-spacing:5px;">SYSTEM TOOLS</h2>
        
        <div style="display:grid;gap:20px;width:90%;max-width:500px;margin-top:30px;">
            <div style="border:1px solid #222;padding:20px;text-align:center;">
                <h3 style="font-size:0.9rem;">تحديد رتب الإدارة</h3>
                <input type="text" id="rid" placeholder="ID الرتبة هنا" style="width:80%;padding:10px;background:#111;border:1px solid #333;color:#fff;">
                <button onclick="fetch('/api/set-role?id='+document.getElementById('rid').value).then(()=>alert('✅ تم حفظ الرتبة'))" style="padding:10px 20px;margin-top:10px;background:#fff;border:none;cursor:pointer;font-weight:bold;">SAVE ROLE</button>
            </div>

            <div style="border:1px solid #222;padding:20px;text-align:center;">
                <h3 style="font-size:0.9rem;">إضافة أوامر للسكربت</h3>
                <button style="width:80%;padding:10px;background:none;border:1px solid #333;color:#333;cursor:not-allowed;">BUILDER SOON</button>
            </div>

            <div style="border:1px solid #111;padding:20px;text-align:center;opacity:0.3;">
                <h3 style="letter-spacing:10px;font-size:0.8rem;">SOON...</h3>
            </div>
        </div>
        <a href="/" style="margin-top:40px;color:#333;text-decoration:none;">BACK</a>
    </body>
    """

@app.route('/api/set-role')
def set_role():
    global admin_role_id
    admin_role_id = request.args.get('id')
    return {"status": "ok"}

# --- نظام معالجة الأوامر (الآن صار حديد) ---
@client.event
async def on_ready():
    print(f'✅ {client.user} متصل')

@client.event
async def on_message(message):
    if message.author == client.user: return
    
    parts = message.content.strip().split()
    if not parts: return
    cmd = parts[0]

    # فحص الصلاحية (الإدارة فقط)
    is_admin = True
    if admin_role_id:
        if admin_role_id not in [str(r.id) for r in message.author.roles] and not message.author.guild_permissions.administrator:
            is_admin = False

    # 1. أمر مسح
    if cmd == 'مسح':
        if not is_admin: return await message.channel.send("❌ للإدارة فقط")
        num = int(parts[1]) if len(parts) > 1 else 5
        await message.channel.purge(limit=num + 1)
        await message.channel.send(f"🧹 تم مسح {num}", delete_after=2)

    # 2. أمر طرد (Kick)
    elif cmd == 'طرد':
        if not is_admin: return await message.channel.send("❌ للإدارة فقط")
        if message.mentions:
            await message.mentions[0].kick()
            await message.channel.send(f"👤 تم طرد العضو {message.mentions[0].mention}")
        else: await message.channel.send("⚠️ منشن الشخص!")

    # 3. أمر بنعالي (Ban)
    elif cmd == 'بنعالي':
        if not is_admin: return await message.channel.send("❌ للإدارة فقط")
        if message.mentions:
            await message.mentions[0].ban()
            await message.channel.send(f"🚫 بنعالي لـ {message.mentions[0].mention}")
        else: await message.channel.send("⚠️ منشن الشخص!")

    # 4. أمر ر (Role) - تم ضبطه بدقة
    elif cmd == 'ر':
        if not is_admin: return await message.channel.send("❌ للإدارة فقط")
        if len(message.mentions) > 0 and len(message.role_mentions) > 0:
            user = message.mentions[0]
            role = message.role_mentions[0]
            await user.add_roles(role)
            await message.channel.send(f"✅ تم تسليم رتبة **{role.name}** لـ {user.mention}")
        else: await message.channel.send("⚠️ الاستخدام: `ر @فلان @رتبة`")

    # 5. أمر قول
    elif cmd == 'قول':
        await message.delete()
        await message.channel.send(" ".join(parts[1:]))

    # 6. أمر موقع
    elif cmd == 'موقع':
        url = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'Railway')}"
        await message.channel.send(f"🔗 {url}")

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    Thread(target=run).start()
    client.run(os.getenv('DISCORD_TOKEN'))
