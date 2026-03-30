import discord
import os
from flask import Flask, request, jsonify
from threading import Thread

# --- إعدادات الواجهة (واسعة وصغيرة - إدارة فقط) ---
app = Flask(__name__)
client = discord.Client(intents=discord.Intents.all())

# قاعدة بيانات مؤقتة (رتبة + صلاحيات + ترحيب)
config = {
    "admin_role": "",
    "perms": {
        "clear": True,
        "kick": False,
        "ban": False,
        "role_mgmt": False,
        "mute": False
    },
    "welcome_channel": "",
    "welcome_msg": "يا هلا بك، نورت السيرفر!"
}

@app.route('/')
def home():
    return """
    <body style="background:#050505;color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;margin:0;">
        <h1 style="letter-spacing:10px;font-size:3rem;margin:0;">RÁIN ADMIN PRO</h1>
        <a href="/dashboard" style="color:#fff;border:1px solid #fff;padding:12px 50px;text-decoration:none;margin-top:20px;font-weight:bold;">ENTER DASHBOARD</a>
    </body>
    """

@app.route('/dashboard')
def dashboard():
    # ستايل الـ Checkboxes
    perms_html = "".join([f'''
        <div style="display:flex; justify-content:space-between; padding:8px; background:#111; margin-bottom:5px; border-radius:4px;">
            <label style="font-size:0.8rem; color:#888;">{k.upper()}</label>
            <input type="checkbox" id="p_{k}" {"checked" if v else ""} onchange="updatePerms()">
        </div>
    ''' for k, v in config["perms"].items()])

    return f"""
    <body style="background:#0a0a0c;color:#fff;font-family:sans-serif;margin:0;padding:20px;display:flex;justify-content:center;">
        <div style="width:98%; display:grid; grid-template-columns: 300px 1fr 1fr; gap:20px;">
            
            <div style="background:#000; border:1px solid #1a1a1a; padding:20px; border-radius:8px;">
                <h3 style="font-size:0.9rem; border-bottom:1px solid #222; padding-bottom:10px; margin-bottom:20px;">🛡️ إعدادات الرتبة</h3>
                <label style="font-size:0.7rem; color:#555;">آيدي رتبة الإدارة:</label>
                <input type="text" id="rid" value="{config['admin_role']}" style="width:100%; padding:10px; background:#0a0a0a; border:1px solid #222; color:#fff; margin:10px 0;">
                <button onclick="saveRole()" style="width:100%; padding:10px; background:#fff; color:#000; border:none; cursor:pointer; font-weight:bold; margin-bottom:30px;">حفظ الرتبة</button>
                
                <h3 style="font-size:0.8rem; color:#555; margin-bottom:15px;">صلاحيات الرتبة:</h3>
                {perms_html}
            </div>

            <div style="background:#000; border:1px solid #1a1a1a; padding:20px; border-radius:8px;">
                <h3 style="font-size:0.9rem; border-bottom:1px solid #222; padding-bottom:10px; margin-bottom:20px;">👋 نظام الترحيب</h3>
                <label style="font-size:0.7rem;">آيدي روم الترحيب:</label>
                <input type="text" id="w_cid" value="{config['welcome_channel']}" style="width:100%; padding:10px; background:#0a0a0a; border:1px solid #222; color:#fff; margin:10px 0;">
                <label style="font-size:0.7rem;">رسالة الترحيب:</label>
                <textarea id="w_msg" style="width:100%; height:80px; background:#0a0a0a; border:1px solid #222; color:#fff; padding:10px; margin-top:10px;">{config['welcome_msg']}</textarea>
                <button onclick="saveWelcome()" style="width:100%; padding:10px; background:#fff; color:#000; border:none; cursor:pointer; font-weight:bold; margin-top:20px;">تفعيل الترحيب</button>
            </div>

            <div style="background:#000; border:1px solid #1a1a1a; padding:20px; border-radius:8px;">
                <h3 style="font-size:0.9rem; border-bottom:1px solid #222; padding-bottom:10px; margin-bottom:20px;">📜 قائمة الأوامر</h3>
                <div style="font-size:0.8rem; color:#666; line-height:2.2;">
                    • <b style="color:#fff;">مسح [عدد]</b> - تنظيف الشات <br>
                    • <b style="color:#fff;">طرد [@عضو]</b> - طرد <br>
                    • <b style="color:#fff;">بنعالي [@عضو]</b> - باند <br>
                    • <b style="color:#fff;">ر [@عضو] [@رتبة]</b> - إعطاء رتبة <br>
                    • <b style="color:#fff;">قول [نص]</b> - تكرار كلام <br>
                    • <b style="color:#fff;">سجن [@عضو]</b> - ميوت <br>
                    • <b style="color:#fff;">صورتي</b> - أفتار
                </div>
            </div>

        </div>

        <script>
            function saveRole() {{
                const id = document.getElementById('rid').value;
                fetch('/api/update?type=role&val=' + id).then(()=>alert('✅ تم الحفظ'));
            }}
            function saveWelcome() {{
                const cid = document.getElementById('w_cid').value;
                const msg = document.getElementById('w_msg').value;
                fetch(`/api/update?type=welcome&val=${{cid}}&msg=${{msg}}`).then(()=>alert('✅ تم الحفظ'));
            }}
            function updatePerms() {{
                const perms = {{
                    clear: document.getElementById('p_clear').checked,
                    kick: document.getElementById('p_kick').checked,
                    ban: document.getElementById('p_ban').checked,
                    role_mgmt: document.getElementById('p_role_mgmt').checked,
                    mute: document.getElementById('p_mute').checked
                }};
                fetch('/api/update?type=perms&val=' + JSON.stringify(perms));
            }}
        </script>
    </body>
    """

@app.route('/api/update')
def update_api():
    t = request.args.get('type')
    v = request.args.get('val')
    if t == 'role': config["admin_role"] = v
    if t == 'welcome':
        config["welcome_channel"] = v
        config["welcome_msg"] = request.args.get('msg')
    if t == 'perms':
        import json
        config["perms"] = json.loads(v)
    return {"status": "ok"}

# --- نظام معالجة الأوامر والترحيب ---
@client.event
async def on_member_join(member):
    if config["welcome_channel"]:
        chan = client.get_channel(int(config["welcome_channel"]))
        if chan: await chan.send(f"{member.mention} {config['welcome_msg']}")

@client.event
async def on_message(message):
    if message.author == client.user: return
    msg = message.content.strip().split()
    if not msg: return
    cmd = msg[0]

    # فحص الإدارة
    is_admin = False
    if message.author.guild_permissions.administrator: is_admin = True
    if config["admin_role"] and config["admin_role"] in [str(r.id) for r in message.author.roles]: is_admin = True

    if not is_admin: return

    # تنفيذ الأوامر بناءً على صلاحيات الموقع
    if cmd == 'مسح' and config["perms"]["clear"]:
        num = int(msg[1]) if len(msg) > 1 else 5
        await message.channel.purge(limit=num+1)
        await message.channel.send(f"🧹 تم تنظيف {num}", delete_after=2)

    elif cmd == 'طرد' and config["perms"]["kick"]:
        if message.mentions: await message.mentions[0].kick()

    elif cmd == 'بنعالي' and config["perms"]["ban"]:
        if message.mentions: await message.mentions[0].ban()

    elif cmd == 'ر' and config["perms"]["role_mgmt"]:
        if len(message.mentions) > 0 and len(message.role_mentions) > 0:
            await message.mentions[0].add_roles(message.role_mentions[0])
            await message.channel.send("✅ تم تسليم الرتبة")

    elif cmd == 'سجن' and config["perms"]["mute"]:
        if message.mentions:
            role = discord.utils.get(message.guild.roles, name="Muted")
            if not role: role = await message.guild.create_role(name="Muted")
            await message.mentions[0].add_roles(role)
            await message.channel.send("🔒 تم")

    elif cmd == 'قول':
        await message.delete()
        await message.channel.send(" ".join(msg[1:]))

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    Thread(target=run).start()
    client.run(os.getenv('DISCORD_TOKEN'))
