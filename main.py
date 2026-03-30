import discord
import os
from flask import Flask, request
from threading import Thread

# --- إعدادات الواجهة (ستايل بروبوت الأسود) ---
app = Flask(__name__)
client = discord.Client(intents=discord.Intents.all())
admin_role_id = None 

@app.route('/')
def home():
    return """
    <body onclick="var a=document.getElementById('r');a.volume=0.1;a.play()" style="background:#000;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;margin:0;cursor:pointer;">
        <audio id="r" loop><source src="https://www.soundjay.com/nature/rain-01.mp3"></audio>
        <h1 style="letter-spacing:15px;font-size:4rem;margin:0;">RÁINBOT</h1>
        <p style="color:#222;letter-spacing:10px;margin-bottom:30px;">PREMIUM DARK SYSTEM</p>
        <a href="/dashboard" style="color:#fff;border:1px solid #fff;padding:15px 60px;text-decoration:none;transition:0.5s;font-weight:bold;letter-spacing:2px;">ENTER DASHBOARD</a>
        <p style="color:#111;font-size:0.7rem;margin-top:20px;">CLICK ANYWHERE FOR RAIN SOUND</p>
    </body>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <body style="background:#050505;color:#fff;font-family:sans-serif;padding:40px;display:flex;flex-direction:column;align-items:center;margin:0;">
        <div style="width:100%;max-width:1100px;border-bottom:1px solid #111;padding-bottom:20px;display:flex;justify-content:space-between;align-items:center;">
            <h1 style="letter-spacing:3px;font-size:1.5rem;">CONTROL PANEL</h1>
            <a href="/" style="color:#444;text-decoration:none;">LOGOUT</a>
        </div>
        
        <div style="display:grid;grid-template-columns:1fr 1.5fr;gap:30px;width:100%;max-width:1100px;margin-top:40px;">
            <div style="background:#000;border:1px solid #151515;padding:30px;border-radius:8px;">
                <h2 style="font-size:0.9rem;color:#666;letter-spacing:2px;margin-bottom:25px;">SETTINGS (الإعدادات)</h2>
                <label style="font-size:0.8rem;color:#888;">آيدي رتبة الإدارة:</label>
                <input type="text" id="rid" placeholder="Paste Role ID" style="width:100%;padding:12px;background:#050505;border:1px solid #222;color:#fff;margin:10px 0 20px 0;border-radius:4px;text-align:center;">
                <button onclick="fetch('/api/set-role?id='+document.getElementById('rid').value).then(()=>alert('✅ تم الحفظ بنجاح'))" style="width:100%;padding:12px;background:#fff;color:#000;border:none;cursor:pointer;font-weight:bold;border-radius:4px;">حفظ الرتبة</button>
            </div>

            <div style="background:#000;border:1px solid #151515;padding:30px;border-radius:8px;">
                <h2 style="font-size:0.9rem;color:#666;letter-spacing:2px;margin-bottom:25px;">COMMANDS (الأوامر الشغالة)</h2>
                <div style="display:grid;gap:12px;">
                    <div style="background:#080808;padding:15px;border-left:4px solid #fff;display:flex;justify-content:space-between;align-items:center;">
                        <b style="color:#fff;">مسح [العدد]</b> <span style="color:#444;font-size:0.8rem;">مسح الرسائل</span>
                    </div>
                    <div style="background:#080808;padding:15px;border-left:4px solid #fff;display:flex;justify-content:space-between;align-items:center;">
                        <b style="color:#fff;">طرد [@عضو]</b> <span style="color:#444;font-size:0.8rem;">طرد من السيرفر</span>
                    </div>
                    <div style="background:#080808;padding:15px;border-left:4px solid #fff;display:flex;justify-content:space-between;align-items:center;">
                        <b style="color:#fff;">بنعالي [@عضو]</b> <span style="color:#444;font-size:0.8rem;">باند نهائي</span>
                    </div>
                    <div style="background:#080808;padding:15px;border-left:4px solid #fff;display:flex;justify-content:space-between;align-items:center;">
                        <b style="color:#fff;">ر [@عضو] [@رتبة]</b> <span style="color:#444;font-size:0.8rem;">إعطاء رتبة</span>
                    </div>
                    <div style="background:#080808;padding:15px;border-left:4px solid #fff;display:flex;justify-content:space-between;align-items:center;">
                        <b style="color:#fff;">قول [النص]</b> <span style="color:#444;font-size:0.8rem;">كلام البوت</span>
                    </div>
                    <div style="background:#080808;padding:15px;border-left:4px solid #fff;display:flex;justify-content:space-between;align-items:center;">
                        <b style="color:#fff;">مساعدة</b> <span style="color:#444;font-size:0.8rem;">قائمة الأوامر</span>
                    </div>
                </div>
            </div>
        </div>
    </body>
    """

@app.route('/api/set-role')
def set_role():
    global admin_role_id
    admin_role_id = request.args.get('id')
    return {"status": "ok"}

# --- نظام معالجة الأوامر الفوري ---
@client.event
async def on_ready():
    print(f'✅ Connected as: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user: return
    
    content = message.content.strip().split()
    if not content: return
    cmd = content[0]

    # فحص الإدارة
    is_admin = True
    if admin_role_id:
        user_roles = [str(r.id) for r in message.author.roles]
        if admin_role_id not in user_roles and not message.author.guild_permissions.administrator:
            is_admin = False

    # 1. مساعدة
    if cmd == 'مساعدة':
        embed = discord.Embed(title="🌑 Ráinbot Commands", description="الأوامر تعمل بدون بادئة", color=0x000000)
        embed.add_field(name="🛡️ إدارية", value="`مسح` | `طرد` | `بنعالي` | `ر`", inline=False)
        embed.add_field(name="🔗 عامة", value="`قول` | `موقع`", inline=False)
        await message.channel.send(embed=embed)

    # 2. مسح
    elif cmd == 'مسح' and is_admin:
        amount = int(content[1]) if len(content) > 1 else 5
        await message.channel.purge(limit=amount + 1)
        await message.channel.send(f"🧹 تم مسح {amount} رسالة", delete_after=2)

    # 3. طرد
    elif cmd == 'طرد' and is_admin:
        if message.mentions:
            await message.mentions[0].kick()
            await message.channel.send(f"👤 تم طرد {message.mentions[0].mention}")
        else: await message.channel.send("⚠️ منشن الشخص")

    # 4. بنعالي
    elif cmd == 'بنعالي' and is_admin:
        if message.mentions:
            await message.mentions[0].ban()
            await message.channel.send(f"🚫 تم بنعالي {message.mentions[0].mention}")
        else: await message.channel.send("⚠️ منشن الشخص")

    # 5. ر (رتبة)
    elif cmd == 'ر' and is_admin:
        if len(message.mentions) > 0 and len(message.role_mentions) > 0:
            user = message.mentions[0]
            role = message.role_mentions[0]
            await user.add_roles(role)
            await message.channel.send(f"✅ تم تسليم رتبة **{role.name}**")
        else: await message.channel.send("⚠️ الاستخدام: `ر @شخص @رتبة`")

    # 6. قول
    elif cmd == 'قول':
        await message.delete()
        await message.channel.send(" ".join(content[1:]))

    # 7. موقع
    elif cmd == 'موقع':
        url = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'rainbot.up.railway.app')}"
        await message.channel.send(f"🔗 {url}")

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    Thread(target=run).start()
    client.run(os.getenv('DISCORD_TOKEN'))
