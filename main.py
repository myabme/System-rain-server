import discord
import os
from flask import Flask, request
from threading import Thread

# --- واجهة الموقع (التصميم الجديد 2026) ---
app = Flask(__name__)
client = discord.Client(intents=discord.Intents.all())
admin_role_id = None 

@app.route('/')
def home():
    return """
    <body onclick="var a=document.getElementById('r');a.volume=0.1;a.play()" style="background:#000;color:#fff;overflow:hidden;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;cursor:pointer;">
        <audio id="r" loop><source src="https://www.soundjay.com/nature/rain-01.mp3"></audio>
        <h1 style="letter-spacing:15px;font-size:4rem;">RÁINBOT</h1>
        <a href="/dashboard" style="color:#fff;border:1px solid #fff;padding:12px 50px;text-decoration:none;margin-top:20px;letter-spacing:2px;">ENTER DASHBOARD</a>
        <p style="color:#222;font-size:0.7rem;margin-top:20px;">CLICK FOR RAIN SOUND</p>
    </body>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <body style="background:#000;color:#fff;font-family:sans-serif;display:flex;flex-direction:column;align-items:center;padding:40px;">
        <h2 style="border-bottom:1px solid #111;width:100%;text-align:center;padding-bottom:20px;letter-spacing:5px;">SYSTEM TOOLS</h2>
        <div style="display:grid;gap:25px;width:90%;max-width:500px;margin-top:40px;">
            <div style="border:1px solid #222;padding:25px;text-align:center;">
                <h3 style="font-size:0.9rem;letter-spacing:2px;">1. تعيين رتب الإدارة</h3>
                <input type="text" id="rid" placeholder="ID الرتبة هنا" style="width:100%;padding:12px;background:#111;border:1px solid #333;color:#fff;margin-bottom:15px;text-align:center;">
                <button onclick="fetch('/api/set-role?id='+document.getElementById('rid').value).then(()=>alert('✅ تم الحفظ'))" style="width:100%;padding:12px;background:#fff;border:none;cursor:pointer;font-weight:bold;">SAVE</button>
            </div>
            <div style="border:1px solid #222;padding:25px;text-align:center;">
                <h3 style="font-size:0.9rem;letter-spacing:2px;">2. إضافة أوامر للسكربت</h3>
                <button style="width:100%;padding:12px;background:none;border:1px solid #333;color:#222;cursor:not-allowed;">BUILDER SOON</button>
            </div>
            <div style="border:1px solid #111;padding:20px;text-align:center;opacity:0.2;">
                <h3 style="letter-spacing:10px;font-size:0.8rem;">SOON...</h3>
            </div>
        </div>
        <a href="/" style="margin-top:40px;color:#333;text-decoration:none;font-size:0.8rem;">BACK TO SYSTEM</a>
    </body>
    """

@app.route('/api/set-role')
def set_role():
    global admin_role_id
    admin_role_id = request.args.get('id')
    return {"status": "ok"}

# --- نظام معالجة الأوامر (تصحيح شامل) ---
@client.event
async def on_ready():
    print(f'✅ {client.user} ONLINE')

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

    # 1. مساعدة
    if cmd == 'مساعدة':
        embed = discord.Embed(title="🌑 قائمة الأوامر", description="الأوامر تعمل بدون بادئة (!)", color=0xffffff)
        embed.add_field(name="🛡️ إدارة", value="`مسح` | `طرد` | `بنعالي` | `ر`", inline=False)
        embed.add_field(name="🔗 عام", value="`قول` | `موقع`", inline=False)
        await message.channel.send(embed=embed)

    # 2. مسح
    elif cmd == 'مسح':
        if not auth: return
        num = int(msg[1]) if len(msg) > 1 else 5
        await message.channel.purge(limit=num + 1)
        await message.channel.send(f"🧹 تم تنظيف {num} رسائل", delete_after=2)

    # 3. طرد (تم الإصلاح)
    elif cmd == 'طرد':
        if not auth: return
        if message.mentions:
            await message.mentions[0].kick()
            await message.channel.send(f"👤 تم طرد {message.mentions[0].mention}")
        else: await message.channel.send("⚠️ منشن الشخص!")

    # 4. بنعالي (تم الإصلاح)
    elif cmd == 'بنعالي':
        if not auth: return
        if message.mentions:
            await message.mentions[0].ban()
            await message.channel.send(f"🚫 تم بنعالي {message.mentions[0].mention}")
        else: await message.channel.send("⚠️ منشن الشخص!")

    # 5. ر (تم الإصلاح الجذري)
    elif cmd == 'ر':
        if not auth: return
        if len(message.mentions) > 0 and len(message.role_mentions) > 0:
            user = message.mentions[0]
            role = message.role_mentions[0]
            await user.add_roles(role)
            await message.channel.send(f"✅ تم تسليم رتبة **{role.name}** لـ {user.mention}")
        else: await message.channel.send("⚠️ اكتب: `ر @فلان @رتبة`")

    # 6. قول
    elif cmd == 'قول':
        await message.delete()
        await message.channel.send(" ".join(msg[1:]))

    # 7. موقع
    elif cmd == 'موقع':
        url = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'rainbot.up.railway.app')}"
        await message.channel.send(f"🔗 {url}")

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    Thread(target=run).start()
    client.run(os.getenv('DISCORD_TOKEN'))
