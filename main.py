import discord
from discord.ext import commands
from flask import Flask, render_template_string
from threading import Thread
import os
import json

# --- 1. إعداد Flask (الواجهة السوداء الفخمة) ---
app = Flask('')

# ملف حفظ الرتب المسموح لها
DATA_FILE = "allowed_roles.json"

def get_allowed_roles():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

@app.route('/')
def home():
    roles = get_allowed_roles()
    roles_list = "".join([f"<li>رتبة ID: {r}</li>" for r in roles]) if roles else "<li>لا يوجد رتب مضافة حالياً</li>"
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>Ráin Bot | Dashboard</title>
        <style>
            body {{ background-color: #000; color: #fff; font-family: 'Arial', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .card {{ background: #0a0a0a; border: 1px solid #1a1a1a; padding: 40px; border-radius: 15px; width: 450px; text-align: center; box-shadow: 0 0 20px rgba(255,255,255,0.05); }}
            h1 {{ font-size: 2.5rem; margin-bottom: 20px; letter-spacing: 2px; text-transform: uppercase; }}
            .section {{ text-align: right; margin-top: 30px; }}
            h2 {{ color: #444; font-size: 1rem; border-bottom: 1px solid #111; padding-bottom: 5px; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ background: #0f0f0f; margin: 8px 0; padding: 12px; border-radius: 8px; font-size: 0.9rem; border-right: 3px solid #fff; }}
            .footer {{ margin-top: 40px; color: #222; font-size: 0.8rem; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Ráin Bot</h1>
            <div class="section">
                <h2>📋 الرتب المصرح لها باستخدام الأوامر:</h2>
                <ul>
                    <li>الإداريين (Administrator)</li>
                    {roles_list}
                </ul>
            </div>
            <div class="section">
                <h2>🛠️ أوامر البوت المتاحة:</h2>
                <ul>
                    <li><b>بنعالي @user</b> - حظر نهائي</li>
                    <li><b>طرد @user</b> - طرد من السيرفر</li>
                    <li><b>مزعج @user</b> - تايم أوت</li>
                    <li><b>مسح [العدد]</b> - تنظيف الشات</li>
                    <li><b>ر @user @role</b> - تعديل الرتب</li>
                </ul>
            </div>
            <div class="footer">Ráin Bot System • 2026</div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)

def run_web():
    # Railway بيعطيك بورت تلقائي، لازم نستخدمه
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. إعدادات البوت ---
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f"✅ Ráin Bot جاهز على ريلوي!")

@client.command(name="ادارة")
@commands.has_permissions(administrator=True)
async def add_role(ctx, role: discord.Role):
    roles = get_allowed_roles()
    if str(role.id) not in roles:
        roles.append(str(role.id))
        with open(DATA_FILE, "w") as f:
            json.dump(roles, f)
        await ctx.send(f"✅ تم إضافة {role.name} لقائمة المصرح لهم في الواجهة.")
    else:
        await ctx.send("الرتبة مضافة أصلاً.")

# تشغيل الموقع في خلفية البوت
Thread(target=run_web).start()

# حط التوكن حقك في Settings -> Variables في Railway باسم DISCORD_TOKEN
client.run(os.getenv('DISCORD_TOKEN'))
