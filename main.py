import discord
import os
from flask import Flask, request
from threading import Thread

# --- واجهة الموقع (التصميم الواسع الفخم) ---
app = Flask(__name__)
client = discord.Client(intents=discord.Intents.all())
admin_role_id = None 

@app.route('/')
def home():
    return """
    <body onclick="var a=document.getElementById('r');a.volume=0.1;a.play()" style="background:#0e0e12;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;margin:0;cursor:pointer;">
        <audio id="r" loop><source src="https://www.soundjay.com/nature/rain-01.mp3"></audio>
        <h1 style="letter-spacing:15px;font-size:5rem;font-weight:900;margin:0;">RÁIN PRO</h1>
        <p style="color:#4e4e5e;letter-spacing:10px;margin-bottom:40px;">ULTIMATE SYSTEM CONTROL</p>
        <a href="/dashboard" style="color:#fff;border:2px solid #fff;padding:20px 80px;text-decoration:none;font-weight:bold;letter-spacing:3px;font-size:1.2rem;border-radius:5px;">ENTER DASHBOARD</a>
    </body>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <body style="background:#08080a;color:#fff;font-family:sans-serif;margin:0;display:flex;height:100vh;">
        <div style="width:350px;background:#111116;border-right:1px solid #1a1a20;display:flex;flex-direction:column;padding:40px;box-sizing:border-box;">
            <h2 style="font-size:2rem;letter-spacing:5px;margin-bottom:60px;font-weight:900;">RÁIN.</h2>
            <div style="margin-bottom:40px;">
                <p style="color:#444;font-size:0.9rem;font-weight:bold;margin-bottom:20px;letter-spacing:2px;">MODULES</p>
                <div style="padding:18px;background:#1a1a20;border-radius:12px;margin-bottom:12px;cursor:pointer;font-weight:bold;">⚙️ الإعدادات العامة</div>
                <div style="padding:18px;color:#555;cursor:pointer;">🛡️ الإشراف والرقابة</div>
                <div style="padding:18px;color:#555;cursor:pointer;">📜 سجلات النظام</div>
            </div>
            <div style="margin-top:auto;padding:20px;background:rgba(255,255,255,0.02);border-radius:10px;text-align:center;">
                <p style="font-size:0.8rem;color:#333;">V3.0 FULL WIDE SCREEN</p>
            </div>
        </div>

        <div style="flex:1;padding:60px;overflow-y:auto;">
            <div style="width:98%;margin:0 auto;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:60px;">
                    <h1 style="font-size:3rem;font-weight:900;">التحكم الكامل</h1>
                    <div style="background:#111116;padding:20px 30px;border-radius:15px;display:flex;gap:20px;border:1px solid #1a1a20;">
                        <input type="text" id="rid" placeholder="ID رتبة الإدارة هنا" style="background:none;border:none;color:#fff;outline:none;font-size:1.1rem;width:300px;">
                        <button onclick="fetch('/api/set-role?id='+document.getElementById('rid').value).then(()=>alert('✅ تم الحفظ'))" style="background:#fff;border:none;padding:12px 30px;border-radius:10px;cursor:pointer;font-weight:bold;font-size:1.1rem;">تحديث</button>
                    </div>
                </div>

                <div style="display:grid;grid-template-columns: repeat(2, 1fr);gap:40px;">
                    <div style="background:#111116;padding:45px;border-radius:20px;border:1px solid #1a1a20;">
                        <h3 style="font-size:1.5rem;margin-bottom:30px;border-bottom:1px solid #1a1a20;padding-bottom:20px;">🛡️ أوامر الإدارة</h3>
                        <div style="display:grid;gap:20px;color:#888;font-size:1.1rem;">
                            <div style="background:#1a1a20;padding:20px;border-radius:10px;"><b>مسح [عدد]</b> - تنظيف المحادثة</div>
                            <div style="background:#1a1a20;padding:20px;border-radius:10px;"><b>طرد [@عضو]</b> - طرد الشخص</div>
                            <div style="background:#1a1a20;padding:20px;border-radius:10px;"><b>بنعالي [@عضو]</b> - حظر الشخص</div>
                            <div style="background:#1a1a20;padding:20px;border-radius:10px;"><b>سجن [@عضو]</b> - كتم (ميوت)</div>
                        </div>
                    </div>

                    <div style="background:#111116;padding:45px;border-radius:20px;border:1px solid #1a1a20;">
                        <h3 style="font-size:1.5rem;margin-bottom:30px;border-bottom:1px solid #1a1a20;padding-bottom:20px;">⚙️ أوامر عامة</h3>
                        <div style="display:grid;gap:20px;color:#888;font-size:1.1rem;">
                            <div style="background:#1a1a20;padding:20px;border-radius:10px;"><b>ر [@عضو] [@رتبة]</b> - إعطاء رتبة</div>
                            <div style="background:#1a1a20;padding:20px;border-radius:10px;"><b>قول [نص]</b> - كلام البوت</div>
                            <div style="background:#1a1a20;padding:20px;border-radius:10px;"><b>صورتي</b> - صورة حسابك</div>
                            <div style="background:#1a1a20;padding:20px;border-radius:10px;"><b>مساعدة</b> - قائمة الأوامر</div>
                        </div>
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

# --- نظام الأوامر المصحح ---
@client.event
async def on_ready():
    print(f'✅ {client.user} ONLINE')

@client.event
async def on_message(message):
    if message.author == client.user: return
    
    parts = message.content.strip().split()
    if not parts: return
    cmd = parts[0]

    # فحص الإدارة: لو أنت صاحب السيرفر أو معك الرتبة المحددة
    is_admin = False
    if message.author.guild_permissions.administrator:
        is_admin = True
    elif admin_role_id and admin_role_id in [str(r.id) for r in message.author.roles]:
        is_admin = True

    # الأوامر الشغالة غصب (بدون بادئة)
    if cmd == 'مساعدة':
        emb = discord.Embed(title="🌑 أوامر رين برو", description="تعمل مباشرة بدون بادئة (!)", color=0x000000)
        emb.add_field(name="🛡️ إدارية", value="`مسح` `طرد` `بنعالي` `سجن` `ر`", inline=False)
        emb.add_field(name="⚙️ عامة", value="`قول` `صورتي` `موقع`", inline=False)
        await message.channel.send(embed=emb)

    elif cmd == 'مسح' and is_admin:
        try:
            num = int(parts[1]) if len(parts) > 1 else 5
            await message.channel.purge(limit=num + 1)
            await message.channel.send(f"🧹 تم تنظيف **{num}** رسائل", delete_after=3)
        except: pass

    elif cmd == 'طرد' and is_admin:
        if message.mentions:
            await message.mentions[0].kick()
            await message.channel.send(f"👤 تم طرد {message.mentions[0].mention}")

    elif cmd == 'بنعالي' and is_admin:
        if message.mentions:
            await message.mentions[0].ban()
            await message.channel.send(f"🚫 تم حظر {message.mentions[0].mention} بنعالي")

    elif cmd == 'ر' and is_admin:
        if len(message.mentions) > 0 and len(message.role_mentions) > 0:
            await message.mentions[0].add_roles(message.role_mentions[0])
            await message.channel.send(f"✅ تم إعطاء الرتبة لـ {message.mentions[0].mention}")

    elif cmd == 'قول':
        await message.delete()
        await message.channel.send(" ".join(parts[1:]))

    elif cmd == 'صورتي':
        u = message.mentions[0] if message.mentions else message.author
        await message.channel.send(u.avatar.url if u.avatar else "ماعندك صورة")

    elif cmd == 'موقع':
        url = f"https://{os.environ.get('RAILWAY_STATIC_URL', 'rainbot.up.railway.app')}"
        await message.channel.send(f"🔗 الداشبورد:\n{url}")

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    Thread(target=run).start()
    client.run(os.getenv('DISCORD_TOKEN'))
