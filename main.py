import discord
import os
from flask import Flask, request
from threading import Thread

# --- واجهة الموقع (التصميم الواسع والمريح) ---
app = Flask(__name__)
client = discord.Client(intents=discord.Intents.all())
admin_role_id = None 

@app.route('/')
def home():
    return """
    <body onclick="var a=document.getElementById('r');a.volume=0.1;a.play()" style="background:#121217;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;margin:0;cursor:pointer;">
        <audio id="r" loop><source src="https://www.soundjay.com/nature/rain-01.mp3"></audio>
        <h1 style="letter-spacing:15px;font-size:5rem;font-weight:900;margin:0;text-shadow: 0 0 20px rgba(255,255,255,0.1);">RÁIN PRO</h1>
        <p style="color:#4e4e5e;letter-spacing:10px;margin-bottom:40px;font-size:1.2rem;">ULTIMATE DASHBOARD</p>
        <a href="/dashboard" style="color:#fff;border:2px solid #fff;padding:20px 80px;text-decoration:none;font-weight:bold;letter-spacing:3px;font-size:1.1rem;transition:0.3s;border-radius:5px;">ENTER SYSTEM</a>
    </body>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <body style="background:#0e0e12;color:#fff;font-family:sans-serif;margin:0;display:flex;height:100vh;">
        <div style="width:320px;background:#16161d;border-right:1px solid #1f1f27;display:flex;flex-direction:column;padding:30px;box-sizing:border-box;">
            <h2 style="font-size:1.8rem;letter-spacing:4px;margin-bottom:50px;color:#fff;font-weight:900;">RÁIN.</h2>
            
            <div style="margin-bottom:30px;">
                <p style="color:#4e4e5e;font-size:0.8rem;font-weight:bold;margin-bottom:15px;">MODULES</p>
                <div style="padding:15px;background:#1f1f27;border-radius:10px;margin-bottom:10px;cursor:pointer;font-weight:bold;">⚙️ الإعدادات العامة</div>
                <div style="padding:15px;color:#6d6d7e;cursor:pointer;">🛡️ نظام الحماية</div>
                <div style="padding:15px;color:#6d6d7e;cursor:pointer;">📜 السجلات (Logs)</div>
            </div>

            <div style="margin-top:auto;">
                <div style="padding:15px;background:rgba(255,255,255,0.05);border-radius:10px;text-align:center;">
                    <p style="font-size:0.8rem;color:#4e4e5e;margin:0;">Abu Meshari Version</p>
                </div>
            </div>
        </div>

        <div style="flex:1;padding:50px;overflow-y:auto;background:#0e0e12;">
            <div style="width:95%;margin:0 auto;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:50px;">
                    <h1 style="font-size:2.5rem;font-weight:900;">لوحة التحكم الشاملة</h1>
                    <div style="background:#16161d;padding:15px 25px;border-radius:12px;display:flex;gap:15px;border:1px solid #1f1f27;">
                        <input type="text" id="rid" placeholder="Admin Role ID" style="background:none;border:none;color:#fff;outline:none;font-size:1rem;width:250px;">
                        <button onclick="fetch('/api/set-role?id='+document.getElementById('rid').value).then(()=>alert('✅ تم الحفظ'))" style="background:#fff;border:none;padding:10px 25px;border-radius:8px;cursor:pointer;font-weight:bold;font-size:1rem;">تحديث</button>
                    </div>
                </div>

                <div style="display:grid;grid-template-columns: repeat(2, 1fr);gap:30px;">
                    <div style="background:#16161d;padding:35px;border-radius:15px;border:1px solid #1f1f27;">
                        <h3 style="color:#fff;font-size:1.3rem;margin-bottom:25px;border-bottom:1px solid #1f1f27;padding-bottom:15px;">🛡️ أوامر الإدارة (Moderation)</h3>
                        <div style="display:grid;gap:15px;color:#8e8e9e;">
                            <div style="background:#1f1f27;padding:15px;border-radius:8px;"><b>مسح [عدد]</b> - تنظيف شات السيرفر</div>
                            <div style="background:#1f1f27;padding:15px;border-radius:8px;"><b>طرد [@عضو]</b> - إخراج عضو من السيرفر</div>
                            <div style="background:#1f1f27;padding:15px;border-radius:8px;"><b>بنعالي [@عضو]</b> - حظر نهائي من السيرفر</div>
                            <div style="background:#1f1f27;padding:15px;border-radius:8px;"><b>سجن [@عضو]</b> - كتم العضو عن الكتابة</div>
                        </div>
                    </div>

                    <div style="background:#16161d;padding:35px;border-radius:15px;border:1px solid #1f1f27;">
                        <h3 style="color:#fff;font-size:1.3rem;margin-bottom:25px;border-bottom:1px solid #1f1f27;padding-bottom:15px;">⚙️ أوامر الخدمات (Utility)</h3>
                        <div style="display:grid;gap:15px;color:#8e8e9e;">
                            <div style="background:#1f1f27;padding:15px;border-radius:8px;"><b>ر [@عضو] [@رتبة]</b> - تسليم رتبة فورية</div>
                            <div style="background:#1f1f27;padding:15px;border-radius:8px;"><b>قول [نص]</b> - التحدث بلسان البوت</div>
                            <div style="background:#1f1f27;padding:15px;border-radius:8px;"><b>صورتي</b> - إظهار صورة حسابك</div>
                            <div style="background:#1f1f27;padding:15px;border-radius:8px;"><b>سيرفر</b> - معلومات وإحصائيات السيرفر</div>
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

# --- نظام معالجة الأوامر ---
@client.event
async def on_ready():
    print(f'✅ Pro System Active: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user: return
    parts = message.content.strip().split()
    if not parts: return
    cmd = parts[0]

    # فحص الصلاحية
    auth = True
    if admin_role_id:
        if admin_role_id not in [str(r.id) for r in message.author.roles] and not message.author.guild_permissions.administrator:
            auth = False

    # تنفيذ الأوامر
    if cmd == 'مساعدة':
        emb = discord.Embed(title="🛡️ أوامر رين برو", color=0x2f3136)
        emb.add_field(name="⚖️ الإدارة", value="`مسح`, `طرد`, `بنعالي`, `سجن`", inline=True)
        emb.add_field(name="⚙️ خدمات", value="`ر`, `قول`, `صورتي`, `سيرفر`", inline=True)
        await message.channel.send(embed=emb)

    elif cmd == 'مسح' and auth:
        num = int(parts[1]) if len(parts) > 1 else 5
        await message.channel.purge(limit=num + 1)
        await message.channel.send(f"🧹 تم مسح {num}", delete_after=2)

    elif cmd == 'ر' and auth:
        if len(message.mentions) > 0 and len(message.role_mentions) > 0:
            await message.mentions[0].add_roles(message.role_mentions[0])
            await message.channel.send("✅ تم")

    elif cmd == 'صورتي':
        u = message.mentions[0] if message.mentions else message.author
        await message.channel.send(u.avatar.url if u.avatar else "لا يوجد صورة")

    elif cmd == 'قول':
        await message.delete()
        await message.channel.send(" ".join(parts[1:]))

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    Thread(target=run).start()
    client.run(os.getenv('DISCORD_TOKEN'))
