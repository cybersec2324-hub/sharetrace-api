import telebot
import requests
import html

BOT_TOKEN = "8710920366:AAFFFBvBO75WQG2ib5id4xuFPWvrkZJpqmw"
API_URL = "http://127.0.0.1:8000/analyze"

bot = telebot.TeleBot(BOT_TOKEN)

def format_result(res_data, url):
    if "status" in res_data and res_data["status"] == "error":
        return f"❌ Error: {html.escape(res_data.get('message', 'Could not process link.'))}"

    if "error" in res_data:
        return f"❌ Error: {html.escape(res_data['error'])}"

    platform = res_data.get("platform", "Extracted data").capitalize()
    details = res_data.get("data", res_data)

    if not isinstance(details, dict) or not details:
        return "❌ Error: No metadata extracted."

    response_text = f"🎭 <b>{html.escape(platform)}</b>\n\n🔗 {url}\n\n"

    field_labels = {
        "username": "Username",
        "name": "Name",
        "bio": "Bio",
        "description": "Description",
        "avatar_url": "Avatar",
        "avatar": "Avatar",
        "follower_count": "Followers",
        "followers": "Followers",
        "following_count": "Following",
        "video_count": "Videos",
        "heart_count": "Likes",
        "device": "Device",
        "share_method": "Share Method",
        "creation_time": "Created",
        "created_at": "Created",
        "email": "Email",
        "emails": "Emails"
    }

    for key, value in details.items():
        if value is None or str(value).strip() == "" or key == "platform":
            continue

        label = field_labels.get(key, key.replace("_", " ").title())

        if isinstance(value, int):
            formatted_val = f"{value:,}"
        else:
            formatted_val = str(value)

        # Avatar link handling
        if "avatar" in key:
            response_text += f"<b>{label}:</b>\n{formatted_val}\n"
        elif isinstance(value, list):
            response_text += f"<b>{label}:</b>\n"
            for item in value:
                response_text += f"• {html.escape(str(item))}\n"
        elif key in ["bio", "description"]:
            response_text += f"<b>{label}:</b> {html.escape(formatted_val)}\n\n"
        else:
            response_text += f"<b>{label}:</b> {html.escape(formatted_val)}\n"

    return response_text

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Hi! Send me a share link (TikTok, GitHub, ChatGPT share, Google Docs, Notion, etc.) "
        "and I'll try to extract data about who shared it.\n\n"
        "Commands:\n"
        "/help — this message\n"
        "/platforms — list of supported platforms"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['platforms'])
def send_platforms(message):
    platforms_text = (
        "Supported platforms:\n"
        "• TikTok\n• ChatGPT\n• Discord\n• Instagram\n• Microsoft\n"
        "• Perplexity\n• Pinterest\n• Substack\n• Suno\n• Telegram\n"
        "• Claude\n• Google Docs\n• GitHub\n• GitLab\n"
        "• Hugging Face\n• LinkedIn\n• Notion\n• YouTube"
    )
    bot.reply_to(message, platforms_text)

@bot.message_handler(func=lambda message: True)
def analyze_message(message):
    url = message.text.strip()

    if not url.startswith("http"):
        bot.reply_to(message, "Send me an http/https link and I'll try to process it.")
        return

    status_msg = bot.reply_to(message, "🔍 Analyzing link metadata... please wait.")

    try:
        response = requests.get(f"{API_URL}?url={url}", timeout=45)
        res_data = response.json()

        formatted_message = format_result(res_data, url)

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            text=formatted_message,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except requests.exceptions.RequestException:
        bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id, text="⚠️ Server communication error.")
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id, text=f"⚠️ Error: {e}")

print("Bot is polling...")
bot.infinity_polling()