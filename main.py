import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- واجهة الموقع الزاحف ---
app = Flask(__name__)
@app.route('/')
def home():
    return "<h1>Ráinbot is Online! Developed by Wilked</h1>"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run).start()

# --- إعدادات البوت (الحل النهائي للأوامر) ---
intents = discord.Intents.all()
# خلينا البادئة فاضية بس هنعالجها يدوي عشان ما يهنج
bot = commands.Bot(command_prefix='', intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} رجع للحياة وشغال!')

# دي أهم حتة عشان الأوامر اللي بدون علامات تشتغل
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # قائمة الأوامر اللي مسموح بيها بدون بادئة
    valid_commands = ['مساعدة', 'موقع', 'مسح', 'طرد', 'بند', 'قول']
    
    # لو أول كلمة في الرسالة هي أمر من أوامرنا، ينفذها
    command_name = message.content.split()[0]
    if command_name in valid_commands:
        await bot.process_commands(message)

# --- نظام التنبيه بالأخطاء ---
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
        embed = discord.Embed(title="❌ نقص في المعلومات", color=0xff0000)
        embed.description = f"يا وحش، لازم تمنشن العضو أو تكتب العدد صح.\n\n**مثال:** `{ctx.command.name} @عضو` أو `مسح 10`"
        await ctx.send(embed=embed, delete_after=10)

# 1. مساعدة
@bot.command(name="مساعدة")
async def help_cmd(ctx):
    embed = discord.Embed(title="🌑 أوامر Ráinbot", description="تحكم كامل - بواسطة **Wilked**", color=0xffffff)
    embed.add_field(name="🛡️ الإدارة", value="`مسح` | `طرد` | `بند`", inline=False)
    embed.add_field(name="🔗 عام", value="`موقع` | `قول`", inline=False)
    embed.set_footer(text="Developed by Wilked")
    await ctx.send(embed=embed)

# 2. موقع
@bot.command(name="موقع")
async def site_link(ctx):
    await ctx.send("🔗 **رابط الداشبورد الزاحف:** https://system-rain-server-production.up.railway.app")

# 3. مسح
@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ تم تنظيف `{amount}` رسالة.", delete_after=3)

# 4. طرد
@bot.command(name="طرد")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("منشن الشخص اللي تبي تطرده يا وحش!")
    await member.kick()
    await ctx.send(f"👤 تم طرد {member.mention}")

# 5. بند
@bot.command(name="بند")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("منشن الشخص اللي تبي تبنده يا وحش!")
    await member.ban()
    await ctx.send(f"🚫 تم تبنيد {member.mention}")

# 6. قول
@bot.command(name="قول")
async def say(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

bot.run(os.getenv('DISCORD_TOKEN'))
