import asyncio
import json
import os
import re
import traceback
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8575184957:AAEZ4Wz-NQDQVc2SNqjpjmhlU56sMsVRih0"
ADMIN_IDS = ["7008926454"]
LOGIN_URL = "https://www.ivasms.com/login"
BASE_URL = "https://www.ivasms.com/"
SMS_API_ENDPOINT = "https://www.ivasms.com/portal/sms/received/getsms"
NUMBERS_URL = "https://www.ivasms.com/portal/sms/received/getsms/number"
SMS_DETAIL_URL = "https://www.ivasms.com/portal/sms/received/getsms/number/sms"

USERNAME = "ninjaxxdenki@gmail.com"
PASSWORD = "Denkidev4@"

POLLING_INTERVAL = 2
STATE_FILE = "processed_sms_ids.json"
CHAT_IDS_FILE = "chat_ids.json"

COUNTRY_FLAGS = {
    "Afghanistan": "🇦🇫", "Albania": "🇦🇱", "Algeria": "🇩🇿", "Andorra": "🇦🇩", "Angola": "🇦🇴",
    "Argentina": "🇦🇷", "Armenia": "🇦🇲", "Australia": "🇦🇺", "Austria": "🇦🇹", "Azerbaijan": "🇦🇿",
    "Bahrain": "🇧🇭", "Bangladesh": "🇧🇩", "Belarus": "🇧🇾", "Belgium": "🇧🇪", "Benin": "🇧🇯",
    "Bhutan": "🇧🇹", "Bolivia": "🇧🇴", "Brazil": "🇧🇷", "Bulgaria": "🇧🇬", "Burkina Faso": "🇧🇫",
    "Cambodia": "🇰🇭", "Cameroon": "🇨🇲", "Canada": "🇨🇦", "Chad": "🇹🇩", "Chile": "🇨🇱",
    "China": "🇨🇳", "Colombia": "🇨🇴", "Congo": "🇨🇬", "Croatia": "🇭🇷", "Cuba": "🇨🇺",
    "Cyprus": "🇨🇾", "Czech Republic": "🇨🇿", "Denmark": "🇩🇰", "Egypt": "🇪🇬", "Estonia": "🇪🇪",
    "Ethiopia": "🇪🇹", "Finland": "🇫🇮", "France": "🇫🇷", "Gabon": "🇬🇦", "Gambia": "🇬🇲",
    "Georgia": "🇬🇪", "Germany": "🇩🇪", "Ghana": "🇬🇭", "Greece": "🇬🇷", "Guatemala": "🇬🇹",
    "Guinea": "🇬🇳", "Haiti": "🇭🇹", "Honduras": "🇭🇳", "Hong Kong": "🇭🇰", "Hungary": "🇭🇺",
    "Iceland": "🇮🇸", "India": "🇮🇳", "Indonesia": "🇮🇩", "Iran": "🇮🇷", "Iraq": "🇮🇶",
    "Ireland": "🇮🇪", "Israel": "🇮🇱", "Italy": "🇮🇹", "IVORY COAST": "🇨🇮", "Ivory Coast": "🇨🇮",
    "Jamaica": "🇯🇲", "Japan": "🇯🇵", "Jordan": "🇯🇴", "Kazakhstan": "🇰🇿", "Kenya": "🇰🇪",
    "Kuwait": "🇰🇼", "Kyrgyzstan": "🇰🇬", "Laos": "🇱🇦", "Latvia": "🇱🇻", "Lebanon": "🇱🇧",
    "Liberia": "🇱🇷", "Libya": "🇱🇾", "Lithuania": "🇱🇹", "Luxembourg": "🇱🇺", "Madagascar": "🇲🇬",
    "Malaysia": "🇲🇾", "Mali": "🇲🇱", "Malta": "🇲🇹", "Mexico": "🇲🇽", "Moldova": "🇲🇩",
    "Monaco": "🇲🇨", "Mongolia": "🇲🇳", "Montenegro": "🇲🇪", "Morocco": "🇲🇦", "Mozambique": "🇲🇿",
    "Myanmar": "🇲🇲", "Namibia": "🇳🇦", "Nepal": "🇳🇵", "Netherlands": "🇳🇱", "New Zealand": "🇳🇿",
    "Nicaragua": "🇳🇮", "Niger": "🇳🇪", "Nigeria": "🇳🇬", "North Korea": "🇰🇵",
    "North Macedonia": "🇲🇰", "Norway": "🇳🇴", "Oman": "🇴🇲", "Pakistan": "🇵🇰", "Panama": "🇵🇦",
    "Paraguay": "🇵🇾", "Peru": "🇵🇪", "Philippines": "🇵🇭", "Poland": "🇵🇱", "Portugal": "🇵🇹",
    "Qatar": "🇶🇦", "Romania": "🇷🇴", "Russia": "🇷🇺", "Rwanda": "🇷🇼", "Saudi Arabia": "🇸🇦",
    "Senegal": "🇸🇳", "Serbia": "🇷🇸", "Sierra Leone": "🇸🇱", "Singapore": "🇸🇬", "Slovakia": "🇸🇰",
    "Slovenia": "🇸🇮", "Somalia": "🇸🇴", "South Africa": "🇿🇦", "South Korea": "🇰🇷", "Spain": "🇪🇸",
    "Sri Lanka": "🇱🇰", "Sudan": "🇸🇩", "Sweden": "🇸🇪", "Switzerland": "🇨🇭", "Syria": "🇸🇾",
    "Taiwan": "🇹🇼", "Tajikistan": "🇹🇯", "Tanzania": "🇹🇿", "Thailand": "🇹🇭", "TOGO": "🇹🇬",
    "Tunisia": "🇹🇳", "Turkey": "🇹🇷", "Turkmenistan": "🇹🇲", "Uganda": "🇺🇬", "Ukraine": "🇺🇦",
    "United Arab Emirates": "🇦🇪", "United Kingdom": "🇬🇧", "United States": "🇺🇸", "Uruguay": "🇺🇾",
    "Uzbekistan": "🇺🇿", "Venezuela": "🇻🇪", "Vietnam": "🇻🇳", "Yemen": "🇾🇪", "Zambia": "🇿🇲",
    "Zimbabwe": "🇿🇼", "Unknown Country": "🏴‍☠️"
}

SERVICE_KEYWORDS = {
    "Facebook": ["facebook"], "Google": ["google", "gmail"], "WhatsApp": ["whatsapp"],
    "Telegram": ["telegram"], "Instagram": ["instagram"], "Amazon": ["amazon"], "Netflix": ["netflix"],
    "LinkedIn": ["linkedin"], "Microsoft": ["microsoft", "outlook", "live.com"],
    "Apple": ["apple", "icloud"], "Twitter": ["twitter"], "Snapchat": ["snapchat"],
    "TikTok": ["tiktok"], "Discord": ["discord"], "Signal": ["signal"], "Viber": ["viber"],
    "IMO": ["imo"], "PayPal": ["paypal"], "Binance": ["binance"], "Uber": ["uber"],
    "Bolt": ["bolt"], "Airbnb": ["airbnb"], "Yahoo": ["yahoo"], "Steam": ["steam"],
    "Blizzard": ["blizzard"], "Foodpanda": ["foodpanda"], "Pathao": ["pathao"],
    "Messenger": ["messenger", "meta"], "Gmail": ["gmail", "google"], "YouTube": ["youtube", "google"],
    "X": ["x", "twitter"], "eBay": ["ebay"], "AliExpress": ["aliexpress"], "Alibaba": ["alibaba"],
    "Flipkart": ["flipkart"], "Outlook": ["outlook", "microsoft"], "Skype": ["skype", "microsoft"],
    "Spotify": ["spotify"], "iCloud": ["icloud", "apple"], "Stripe": ["stripe"],
    "Cash App": ["cash app", "square cash"], "Venmo": ["venmo"], "Zelle": ["zelle"],
    "Wise": ["wise", "transferwise"], "Coinbase": ["coinbase"], "KuCoin": ["kucoin"],
    "Bybit": ["bybit"], "OKX": ["okx"], "Huobi": ["huobi"], "Kraken": ["kraken"],
    "MetaMask": ["metamask"], "Epic Games": ["epic games", "epicgames"],
    "PlayStation": ["playstation", "psn"], "Xbox": ["xbox", "microsoft"], "Twitch": ["twitch"],
    "Reddit": ["reddit"], "ProtonMail": ["protonmail", "proton"], "Zoho": ["zoho"],
    "Quora": ["quora"], "StackOverflow": ["stackoverflow"], "Indeed": ["indeed"],
    "Upwork": ["upwork"], "Fiverr": ["fiverr"], "Glassdoor": ["glassdoor"],
    "Booking.com": ["booking.com", "booking"], "Careem": ["careem"], "Swiggy": ["swiggy"],
    "Zomato": ["zomato"], "McDonald's": ["mcdonalds", "mcdonald's"], "KFC": ["kfc"],
    "Nike": ["nike"], "Adidas": ["adidas"], "Shein": ["shein"], "OnlyFans": ["onlyfans"],
    "Tinder": ["tinder"], "Bumble": ["bumble"], "Grindr": ["grindr"], "Line": ["line"],
    "WeChat": ["wechat"], "VK": ["vk", "vkontakte"], "Unknown": ["unknown"]
}

SERVICE_EMOJIS = {
    "Telegram": "📩", "WhatsApp": "🟢", "Facebook": "📘", "Instagram": "📸", "Messenger": "💬",
    "Google": "🔍", "Gmail": "✉️", "YouTube": "▶️", "Twitter": "🐦", "X": "❌",
    "TikTok": "🎵", "Snapchat": "👻", "Amazon": "🛒", "eBay": "📦", "AliExpress": "📦",
    "Alibaba": "🏭", "Flipkart": "📦", "Microsoft": "🪟", "Outlook": "📧", "Skype": "📞",
    "Netflix": "🎬", "Spotify": "🎶", "Apple": "🍏", "iCloud": "☁️", "PayPal": "💰",
    "Stripe": "💳", "Cash App": "💵", "Venmo": "💸", "Zelle": "🏦", "Wise": "🌐",
    "Binance": "🪙", "Coinbase": "🪙", "KuCoin": "🪙", "Bybit": "📈", "OKX": "🟠",
    "Huobi": "🔥", "Kraken": "🐙", "MetaMask": "🦊", "Discord": "🗨️", "Steam": "🎮",
    "Epic Games": "🕹️", "PlayStation": "🎮", "Xbox": "🎮", "Twitch": "📺", "Reddit": "👽",
    "Yahoo": "🟣", "ProtonMail": "🔐", "Zoho": "📬", "Quora": "❓", "StackOverflow": "🧑‍💻",
    "LinkedIn": "💼", "Indeed": "📋", "Upwork": "🧑‍💻", "Fiverr": "💻", "Glassdoor": "🔎",
    "Airbnb": "🏠", "Booking.com": "🛏️", "Uber": "🚗", "Lyft": "🚕", "Bolt": "🚖",
    "Careem": "🚗", "Swiggy": "🍔", "Zomato": "🍽️", "Foodpanda": "🍱",
    "McDonald's": "🍟", "KFC": "🍗", "Nike": "👟", "Adidas": "👟", "Shein": "👗",
    "OnlyFans": "🔞", "Tinder": "🔥", "Bumble": "🐝", "Grindr": "😈", "Signal": "🔐",
    "Viber": "📞", "Line": "💬", "WeChat": "💬", "VK": "🌐", "Unknown": "❓"
}

def load_json(filename, default):
    if not os.path.exists(filename):
        save_json(filename, default)
        return default
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return default

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def escape_markdown(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id in ADMIN_IDS:
        await update.message.reply_text(
            "Welcome Admin!\nCommands:\n/add_chat <id>\n/remove_chat <id>\n/list_chats"
        )
    else:
        await update.message.reply_text("Unauthorized.")

async def add_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in ADMIN_IDS: return
    try:
        new_id = context.args[0]
        chats = load_json(CHAT_IDS_FILE, [])
        if new_id not in chats:
            chats.append(new_id)
            save_json(CHAT_IDS_FILE, chats)
            await update.message.reply_text(f"✅ Added {new_id}")
        else:
            await update.message.reply_text("⚠️ Already exists")
    except IndexError:
        await update.message.reply_text("❌ Usage: /add_chat <id>")

async def remove_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in ADMIN_IDS: return
    try:
        target_id = context.args[0]
        chats = load_json(CHAT_IDS_FILE, [])
        if target_id in chats:
            chats.remove(target_id)
            save_json(CHAT_IDS_FILE, chats)
            await update.message.reply_text(f"✅ Removed {target_id}")
        else:
            await update.message.reply_text("⚠️ Not found")
    except IndexError:
        await update.message.reply_text("❌ Usage: /remove_chat <id>")

async def list_chats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id not in ADMIN_IDS: return
    chats = load_json(CHAT_IDS_FILE, [])
    if chats:
        msg = "📜 Chat IDs:\n" + "\n".join(f"- `{escape_markdown(c)}`" for c in chats)
        await update.message.reply_text(msg, parse_mode='MarkdownV2')
    else:
        await update.message.reply_text("No chats registered.")

async def fetch_messages(client: httpx.AsyncClient, csrf_token: str):
    messages = []
    try:
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        from_date = yesterday.strftime('%m/%d/%Y')
        to_date = now.strftime('%m/%d/%Y')

        payload = {'from': from_date, 'to': to_date, '_token': csrf_token}
        res = await client.post(SMS_API_ENDPOINT, data=payload)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        group_divs = soup.find_all('div', {'class': 'pointer'})
        group_ids = [
            re.search(r"getDetials\('(.+?)'\)", d.get('onclick', '')).group(1)
            for d in group_divs if re.search(r"getDetials\('(.+?)'\)", d.get('onclick', ''))
        ]

        for gid in group_ids:
            num_payload = {'start': from_date, 'end': to_date, 'range': gid, '_token': csrf_token}
            num_res = await client.post(NUMBERS_URL, data=num_payload)
            num_soup = BeautifulSoup(num_res.text, 'html.parser')
            
            phones = [d.text.strip() for d in num_soup.select("div[onclick*='getDetialsNumber']")]

            for phone in phones:
                sms_payload = {'start': from_date, 'end': to_date, 'Number': phone, 'Range': gid, '_token': csrf_token}
                sms_res = await client.post(SMS_DETAIL_URL, data=sms_payload)
                sms_soup = BeautifulSoup(sms_res.text, 'html.parser')
                cards = sms_soup.find_all('div', class_='card-body')

                for card in cards:
                    p_tag = card.find('p', class_='mb-0')
                    if not p_tag: continue
                    
                    text = p_tag.get_text(separator='\n').strip()
                    msg_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                    
                    country_match = re.match(r'([a-zA-Z\s]+)', gid)
                    country = country_match.group(1).strip() if country_match else gid.strip()
                    
                    service = "Unknown"
                    lower_text = text.lower()
                    for s_name, kws in SERVICE_KEYWORDS.items():
                        if any(k in lower_text for k in kws):
                            service = s_name
                            break
                    
                    code_match = re.search(r'(\d{3}-\d{3})', text) or re.search(r'\b(\d{4,8})\b', text)
                    code = code_match.group(1) if code_match else "N/A"
                    unique_id = f"{phone}-{text}"
                    flag = COUNTRY_FLAGS.get(country, "🏴‍☠️")

                    messages.append({
                        "id": unique_id, "time": msg_time, "number": phone,
                        "country": country, "flag": flag, "service": service,
                        "code": code, "full_sms": text
                    })
    except Exception:
        traceback.print_exc()
    return messages

async def check_sms_job(context: ContextTypes.DEFAULT_TYPE):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
        try:
            login_page = await client.get(LOGIN_URL)
            soup = BeautifulSoup(login_page.text, 'html.parser')
            token_input = soup.find('input', {'name': '_token'})
            
            login_data = {'email': USERNAME, 'password': PASSWORD}
            if token_input:
                login_data['_token'] = token_input['value']

            login_res = await client.post(LOGIN_URL, data=login_data)
            
            if "login" in str(login_res.url):
                print("❌ Login failed")
                return

            dash_soup = BeautifulSoup(login_res.text, 'html.parser')
            csrf_meta = dash_soup.find('meta', {'name': 'csrf-token'})
            if not csrf_meta: return
            csrf_token = csrf_meta.get('content')
            headers['Referer'] = str(login_res.url)

            messages = await fetch_messages(client, csrf_token)
            if not messages: return

            processed = set(load_json(STATE_FILE, []))
            chats = load_json(CHAT_IDS_FILE, [])
            new_count = 0

            for msg in reversed(messages):
                if msg['id'] not in processed:
                    new_count += 1
                    svc_emoji = SERVICE_EMOJIS.get(msg['service'], "❓")
                    
                    txt = (
                        f"🔔 *OTP Received*\n\n"
                        f"📞 *Number:* `{escape_markdown(msg['number'])}`\n"
                        f"🔑 *Code:* `{escape_markdown(msg['code'])}`\n"
                        f"🏆 *Service:* {svc_emoji} {escape_markdown(msg['service'])}\n"
                        f"🌎 *Country:* {escape_markdown(msg['country'])} {msg['flag']}\n"
                        f"⏳ *Time:* `{escape_markdown(msg['time'])}`\n\n"
                        f"💬 *Message:*\n```\n{msg['full_sms']}\n```"
                    )

                    for chat_id in chats:
                        try:
                            await context.bot.send_message(chat_id=chat_id, text=txt, parse_mode='MarkdownV2')
                        except Exception as e:
                            print(f"Failed to send to {chat_id}: {e}")
                    
                    processed.add(msg['id'])
            
            if new_count > 0:
                save_json(STATE_FILE, list(processed))
                print(f"Sent {new_count} new messages")

        except Exception as e:
            print(f"Job Error: {e}")

def main():
    if not ADMIN_IDS:
        print("Set ADMIN_IDS first.")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("add_chat", add_chat_command))
    app.add_handler(CommandHandler("remove_chat", remove_chat_command))
    app.add_handler(CommandHandler("list_chats", list_chats_command))

    app.job_queue.run_repeating(check_sms_job, interval=POLLING_INTERVAL, first=1)
    
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
