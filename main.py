import discord
import os
import asyncio
from flask import Flask, request
from threading import Thread

# --- إعدادات الواجهة (ProBot Black Edition) ---
app = Flask(__name__)
client = discord.Client(intents=discord.Intents.all())
admin_role_id = None 

@app.route('/')
def home():
    return """
    <body onclick="var a=document.getElementById('r');a.volume=0.1;a.play()" style="background:#000;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;margin:0;cursor:pointer;">
        <audio id="r" loop><source src="https://www.soundjay.com/nature/rain-01.mp3"></audio>
        <h1 style="letter-spacing:15px;font-size:3rem;margin:0;font-weight:900;">RÁINBOT PRO</h1>
        <p style="color:#333;letter-spacing:8px;margin-bottom:30px;">THE ULTIMATE ARABIC SYSTEM</p>
        <a href="/dashboard" style="color:#fff;border:1px solid #fff;padding:15px 60px;text-decoration:none;transition:0.5s;font-weight:bold;letter-spacing:2px;border-radius:2px;">DASHBOARD</a>
    </body>
    """

@app.route('/dashboard')
def dashboard():
    return """
    <body style="background:#080808;color:#fff;font-family:sans-serif;margin:0;display:flex;">
        <div style="width:250px;background:#000;height:100vh;border-right:1px solid #111;padding:20px;display:flex;flex-direction:column;">
            <h2 style="font-size:1.2rem;letter-spacing:2px;margin-bottom:40px;">RÁINBOT</h2>
            <div style="color:#fff;padding:10px;background:#111;border-radius:5px;margin-bottom:10px;cursor:pointer;">🏠 الرئيسية</div>
            <div style="color:#555;padding:10px;cursor:not-allowed;">⚙️ الإعدادات العامة</div>
            <div style="color:#555;padding:10px;cursor:not-allowed;">🛡️ الحماية التلقائية</div>
            <div style="margin-top:auto;color:#222;font-size:0.7rem;">PROBOT CLONE V2</div>
        </div>

        <div style="flex:1;padding:40px;overflow-y:auto;">
            <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #111;padding-bottom:20px;">
                <h1 style="font-size:1.5rem;">لوحة التحكم (Pro Style)</h1>
                <div style="background:#111;padding:5px 15px;border-radius:20px;font-size:0.8rem;color:#888;">Online</div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-top:40px;">
                <div style="background:#000;border:1px solid #151515;padding:25px;border-radius:8px;">
                    <h3 style="color:#666;font-size:0.8rem;letter-spacing:1px;margin-bottom:20px;">SETTINGS</h3>
                    <p style="font-size:0.8rem;color:#888;">آيدي رتبة الإدارة المستهدفة:</p>
                    <input type="text" id="rid" placeholder="Role ID" style="width:100%;padding:12px;background:#050505;border:1px solid #222;color:#fff;margin:10px 0;border-radius:4px;">
                    <button onclick="fetch('/api/set-role?id='+document.getElementById('rid').value).then(()=>alert('✅ تم الحفظ'))" style="width:100%;padding:12px;background:#fff;color:#000;border:none;cursor:pointer;font-weight:bold;border-radius:4px;">تحديث</button>
                </div>

                <div style="background:#000;border:1px solid #151515;padding:25px;border-radius:8px;">
                    <h3 style="color:#666;font-size:0.8rem;letter-spacing:1px;margin-bottom:20px;">ARABIC COMMANDS</h3>
                    <div style="display:grid;gap:10px;max-height:300px;overflow-y:auto;">
                        <div style="background:#0a0a0a;padding:12px;border-radius:4px;font-size:0.85rem;border-left:3px solid #fff;"><b>مسح</b> - تنظيف الرسائل</div>
                        <div style="background:#0a0a0a;padding:12px;border-radius:4px;font-size:0.85rem;border-left:3px solid #fff;"><b>طرد</b> - طرد عضو</div>
                        <div style="background:#0a0a0a;padding:12px;border-radius:4px;font-size:0.85rem;border-left:3px solid #fff;"><b>بنعالي</b> - باند نهائي</div>
                        <div style="background:#0a0a0a;padding:12px;border-radius:4px;font-size:0.85rem;border-left:3px solid #fff;"><b>سجن</b> - سجن العضو (ميوت)</div>
                        <div style="background:#0a0a0a;padding:12px;border-radius:4px;font-size:0.85rem;border-left:3px solid #fff;"><b>فك-سجن</b> - فك الميوت</div>
                        <div style="background:#0a0a0a;padding:12px;border-radius:4px;font-size:0.85rem;border-left:3px solid #fff;"><b>ر</b> - إعطاء رتبة</div>
                        <div style="background:#0a0a0a;padding:12px;border-radius:4px;font-size:0.85rem;border-left:3px solid #fff;"><b>قول</b> - كلام البوت</div>
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

# --- نظام الأوامر الاحترافي ---
@client.event
async def on_ready():
    print(f'✅ ProBot Clone Online: {client.user}')

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
        emb = discord.Embed(title="🛡️ أوامر رين بوت برو", color=0x000000)
        emb.add_field(name="الإدارة", value="`مسح` | `طرد` | `بنعالي` | `سجن` | `فك-سجن` | `ر`", inline=False)
        emb.add_field(name="عام", value="`قول` | `موقع`", inline=False)
        await message.channel.send(embed=emb)

    elif cmd == 'مسح' and auth:
        num = int(parts[1]) if len(parts) > 1 else 5
        await message.channel.purge(limit=num + 1)
        await message.channel.send(f"🧹 تم تنظيف {num} رسالة.", delete_after=2)

    elif cmd == 'طرد' and auth:
        if message.mentions:
            await message.mentions[0].kick()
            await message.channel.send(f"👤 تم طرد {message.mentions[0].mention}")

    elif cmd == 'بنعالي' and auth:
        if message.mentions:
            await message.mentions[0].ban()
            await message.channel.send(f"🚫 تم حظر {message.mentions[0].mention}")

    elif cmd == 'سجن' and auth:
        if message.mentions:
            role = discord.utils.get(message.guild.roles, name="Muted")
            if not role:
                role = await message.guild.create_role(name="Muted")
                for channel in message.guild.channels:
                    await channel.set_permissions(role, speak=False, send_messages=False)
            await message.mentions[0].add_roles(role)
            await message.channel.send(f"🔒 تم سجن {message.mentions[0].mention}")

    elif cmd == 'فك-سجن' and auth:
        if message.mentions:
            role = discord.utils.get(message.guild.roles, name="Muted")
            if role: await message.mentions[0].remove_roles(role)
            await message.channel.send(f"🔓 تم إخراج {message.mentions[0].mention} من السجن.")

    elif cmd == 'ر' and auth:
        if len(message.mentions) > 0 and len(message.role_mentions) > 0:
            await message.mentions[0].add_roles(message.role_mentions[0])
            await message.channel.send(f"✅ تم تسليم الرتبة بنجاح.")

    elif cmd == 'قول':
        await message.delete()
        await message.channel.send(" ".join(parts[1:]))

    elif cmd == 'موقع':
        await message.channel.send(f"🔗 رابط الداشبورد:\nhttps://{os.environ.get('RAILWAY_STATIC_URL', 'rainbot.up.railway.app')}")

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    Thread(target=run).start()
    client.run(os.getenv('DISCORD_TOKEN'))
