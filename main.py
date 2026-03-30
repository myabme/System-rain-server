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
