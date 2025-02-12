# Developed By MrAmini

from telethon import TelegramClient, events, functions
import asyncio
import random
import os
import requests
import json

# Configuration
API_ID = '***'  # Replace with your API ID
API_HASH = '****'  # Replace with your API hash
BOT_OWNER_ID = ID  # Replace with the bot owner's Telegram user ID
USERS_FILE = 'user.txt'
MESSAGE_FILE = 'pm.txt'
BIO_API_URL = 'https://api.codebazan.ir/bio'
SETTINGS_FILE = 'settings.json'

# Default settings
default_settings = {
    'save_user': True,
    'chat_user': False,  # Default to False, will be activated by chatuseron
    'random_bio': False
}

# Load settings from file
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    else:
        return default_settings

# Save settings to file
def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

# Create the client
client = TelegramClient('session', API_ID, API_HASH)
settings = load_settings()
client.start()

# Helper functions
def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, 'w').close()

    with open(USERS_FILE, 'r') as f:
        users = set(f.read().splitlines())

    if str(user_id) not in users:
        with open(USERS_FILE, 'a') as f:
            f.write(f"{user_id}\n")
        print(f"User {user_id} saved successfully.")
    else:
        print(f"User {user_id} already exists.")

# Update bio with random text
async def update_bio():
    try:
        response = requests.get(BIO_API_URL)
        if response.status_code == 200:
            bio = response.text
            # Update the bio using UpdateProfileRequest
            await client(functions.account.UpdateProfileRequest(about=bio))
    except Exception as e:
        print(f"Error updating bio: {e}")

# Handlers
@client.on(events.NewMessage)
async def message_handler(event):
    sender_id = event.sender_id
    message = event.raw_text.lower()

    # Save chatting users if chat_user is enabled
    if settings['chat_user'] and event.is_group:  # Check if the message is from a group
        save_user(sender_id)

    if sender_id == BOT_OWNER_ID:
        if message == 'bot':
            await event.reply("سلام، آنلاینم! کارت رو بگو.")
        elif message == 'saveuseron':
            settings['save_user'] = True
            save_settings(settings)
            await event.reply("ذخیره کاربران گروه فعال شد.")
        elif message == 'saveuseroff':
            settings['save_user'] = False
            save_settings(settings)
            await event.reply("ذخیره کاربران گروه غیرفعال شد.")
        elif message == 'chatuseron':
            settings['chat_user'] = True
            save_settings(settings)
            await event.reply("ذخیره کاربران ارسال‌کننده پیام در گروه‌ها فعال شد.")
        elif message == 'chatuseroff':
            settings['chat_user'] = False
            save_settings(settings)
            await event.reply("ذخیره کاربران ارسال‌کننده پیام در گروه‌ها غیرفعال شد.")
        elif message == 'bioon':
            settings['random_bio'] = True
            save_settings(settings)
            await update_bio()  # اصلاح اینجا برای استفاده از await
            await event.reply("بیوگرافی تصادفی فعال شد.")
        elif message == 'biooff':
            settings['random_bio'] = False
            save_settings(settings)
            await event.reply("بیوگرافی تصادفی غیرفعال شد.")
        elif message == 'sendpm':
            if os.path.exists(USERS_FILE) and os.path.exists(MESSAGE_FILE):
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                    users = f.read().splitlines()

                with open(MESSAGE_FILE, 'r', encoding='utf-8') as f:
                    message_content = f.read()

                for user in users:
                    try:
                        await client.send_message(int(user), message_content)
                        await asyncio.sleep(random.randint(1, 10))
                    except Exception as e:
                        print(f"Error sending message to {user}: {e}")

                await event.reply("پیام‌ها با موفقیت ارسال شدند.")
            else:
                await event.reply("فایل‌های مورد نیاز وجود ندارند.")
        elif message == 'info':
            # Gathering bot's status information
            total_users = 0
            if os.path.exists(USERS_FILE):
                with open(USERS_FILE, 'r') as f:
                    total_users = len(f.read().splitlines())

            # Generate info text
            info_text = (
                f"وضعیت ربات: {'آنلاین' if client.is_connected else 'آفلاین'}\n"
                f"تعداد کاربران جمع شده: {total_users}\n"
                f"جمع‌آوری لیست اعضای گروه: {'فعال' if settings['save_user'] else 'غیرفعال'}\n"
                f"جمع‌آوری یوزرهای درحال چت: {'فعال' if settings['chat_user'] else 'غیرفعال'}\n"
                f"بیوگرافی تصادفی: {'فعال' if settings['random_bio'] else 'غیرفعال'}\n"
            )
            await event.reply(info_text)
        elif message == 'help':
            help_text = (
                "دستورات موجود:\n"
                "bot: بررسی آنلاین بودن ربات\n"
                "sendpm: ارسال پیام به تمام کاربران ذخیره‌شده\n"
                "saveuseron: فعال‌سازی ذخیره کاربران گروه‌ها\n"
                "saveuseroff: غیرفعال‌سازی ذخیره کاربران گروه‌ها\n"
                "chatuseron: فعال‌سازی ذخیره کاربران ارسال‌کننده پیام در گروه‌ها\n"
                "chatuseroff: غیرفعال‌سازی ذخیره کاربران ارسال‌کننده پیام در گروه‌ها\n"
                "bioon: فعال‌سازی بیوگرافی تصادفی\n"
                "biooff: غیرفعال‌سازی بیوگرافی تصادفی\n"
                "info: نمایش اطلاعات ربات\n"
                "help: نمایش لیست دستورات"
            )
            await event.reply(help_text)



@client.on(events.ChatAction)
async def chat_action_handler(event):
    if settings['save_user'] and event.user_added:
        # ذخیره یوزرها فقط از گروه‌ها
        if event.chat and event.is_group:
            for user in event.users:
                save_user(user.id)

# Run the client
print("ربات در حال اجرا است...")
client.start()
client.run_until_disconnected()
