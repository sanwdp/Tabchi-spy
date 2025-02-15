# Developed By MrAmini

import asyncio
import random
import os
import json
import re
import httpx
import logging
from telethon import TelegramClient, events, functions, types

# تنظیمات لاگینگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_ID = 'API_ID'  # جایگزین کنید با API ID خود
API_HASH = 'API_HASH'  # جایگزین کنید با API HASH خود
BOT_OWNER_ID = ID  # جایگزین کنید با آی‌دی تلگرام مالک ربات
USERS_FILE = 'user.txt'
MESSAGE_FILE = 'pm.txt'
BIO_API_URL = 'https://api.codebazan.ir/bio/'
SETTINGS_FILE = 'settings.json'
ACCOUNTS_FILE = 'accounts.json'

default_settings = {
    'save_user': True,
    'chat_user': False,
    'random_bio': False,
    'filter_last_seen': False,
    'remove_invalid_users': False,
    'daily_limit': 10,
    'auto_join': False
}

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                else:
                    return {}
            except json.JSONDecodeError:
                logger.error("خطا در رمزگشایی فایل حساب‌ها (JSON).")
                return {}
    return {}

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w', encoding="utf-8") as f:
        json.dump(accounts, f, ensure_ascii=False, indent=4)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.error("خطا در رمزگشایی فایل تنظیمات، از تنظیمات پیش‌فرض استفاده می‌شود.")
                return default_settings
    else:
        return default_settings

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

# راه‌اندازی کلاینت اصلی
client = TelegramClient('session', API_ID, API_HASH).start()
settings = load_settings()

def save_user(user_id: int):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, 'w').close()

    with open(USERS_FILE, 'r', encoding="utf-8") as f:
        users = set(f.read().splitlines())

    if str(user_id) not in users:
        with open(USERS_FILE, 'a', encoding="utf-8") as f:
            f.write(f"{user_id}\n")
        logger.info(f"کاربر {user_id} با موفقیت ذخیره شد.")
    else:
        logger.info(f"کاربر {user_id} قبلاً وجود دارد.")

async def set_new_pm(event):
    try:
        text = event.raw_text
        if not text.lower().startswith("setnewpm"):
            await event.reply("⚠️ دستور نامعتبر است. لطفاً پیام خود را به درستی وارد کنید.")
            return

        parts = text.split("\n", 1)
        if len(parts) < 2:
            await event.reply("⚠️ لطفاً پیام جدید خود را بعد از `setnewpm` در خط جدید وارد کنید.")
            return

        new_message = parts[1].strip()
        with open(MESSAGE_FILE, "w", encoding="utf-8") as f:
            f.write(new_message)

        await event.reply("✅ پیام جدید با موفقیت ذخیره شد.")
    except Exception as e:
        await event.reply(f"⚠️ خطا در ذخیره پیام: {e}")

async def update_bio():
    try:
        async with httpx.AsyncClient(follow_redirects=True) as req:
            response = await req.get(BIO_API_URL, timeout=5)
            if response.status_code == 200:
                bio = response.text.strip()
            else:
                raise Exception(f"API request failed with status {response.status_code}")
    except Exception as e:
        logger.warning(f"خطا در دریافت بیو از API: {e}. تلاش برای استفاده از فایل محلی.")
        try:
            with open("bio.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                bios = data.get("bio", [])
                if not bios:
                    return "بیو برای ست شدن یافت نشد."
                bio = random.choice(bios)
        except (FileNotFoundError, json.JSONDecodeError) as file_error:
            return f"Error: {file_error}"

    try:
        await client(functions.account.UpdateProfileRequest(about=bio))
        return f"**📩 بیوگرافی ست شده:**\n {bio}"
    except Exception as e:
        return f"Error updating bio: {e}"
    
async def get_last_seen(user_id):
    try:
        user = await client.get_entity(user_id)
        if hasattr(user.status, 'was_online'):
            return user.status.was_online
    except Exception as e:
        logger.error(f"خطا در دریافت آخرین بازدید برای {user_id}: {e}")
    return None

async def check_ban():
    try:
        await client.send_message(BOT_OWNER_ID, "Checking ban status...")
        return "ربات فعال است."
    except Exception as e:
        logger.error(f"خطا در بررسی بن: {e}")
        return "⚠️ ربات بن شده و قادر به ارسال پیام نیست."

async def join_group_from_message(event):
    if not settings.get('auto_join', False):
        return  # اگر قابلیت غیرفعال است، نیازی به ادامه نیست

    message_text = event.raw_text.strip()
    if "t.me/" not in message_text:
        return

    # بررسی لینک گروه خصوصی یا عمومی
    if "joinchat" in message_text or "t.me/+" in message_text:
        # لینک خصوصی
        private_link_pattern = r"https?:\/\/t\.me\/(?:joinchat\/|\+)?([a-zA-Z0-9_-]+)"
        private_match = re.search(private_link_pattern, message_text)
        if private_match:
            group_identifier = private_match.group(1)
            try:
                await client(functions.messages.ImportChatInviteRequest(group_identifier))
                await event.reply("✅ به گروه خصوصی پیوستم!")
            except Exception as e:
                await event.reply(f"❌ خطا در پیوستن به گروه: {str(e)}")
    else:
        # لینک عمومی
        group_link_pattern = r"(https?:\/\/t\.me\/(?:joinchat\/)?([a-zA-Z0-9_-]+))"
        match = re.search(group_link_pattern, message_text)
        if match:
            group_identifier = match.group(2)
            try:
                await client(functions.channels.JoinChannelRequest(group_identifier))
                await event.reply("✅ به گروه عمومی پیوستم!")
            except Exception as e:
                await event.reply(f"❌ خطا در پیوستن به گروه: {str(e)}")

# handler جداگانه برای پردازش ورود به گروه‌ها (برای جلوگیری از تداخل با سایر handlers)
@client.on(events.NewMessage)
async def group_join_handler(event):
    await join_group_from_message(event)

async def send_messages():
    if os.path.exists(USERS_FILE) and os.path.exists(MESSAGE_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = f.read().splitlines()

        with open(MESSAGE_FILE, 'r', encoding='utf-8') as f:
            message_content = f.read()

        accounts_data = load_accounts()
        active_accounts = [phone for phone, data in accounts_data.items() if data.get("status") == "active"]
        if not active_accounts:
            return "⛔ هیچ اکانت فعالی برای ارسال پیام وجود ندارد."

        total_accounts = len(active_accounts)
        limit_per_account = settings['daily_limit'] // total_accounts if settings['daily_limit'] > 0 else len(users) // total_accounts

        sent_count = 0
        failed_count = 0
        removed_users = 0

        # استفاده از یک کپی از لیست کاربران جهت جلوگیری از بروز مشکل هنگام حذف
        for index, user in enumerate(users.copy()):
            if settings['daily_limit'] > 0 and sent_count >= settings['daily_limit']:
                break

            current_account = active_accounts[index % total_accounts]
            # استفاده از کلاینت جداگانه برای هر اکانت به منظور جلوگیری از سردرگمی در استفاده از کلاینت اصلی
            acc_client = TelegramClient(f'session_{current_account}', API_ID, API_HASH)
            try:
                await acc_client.connect()
                try:
                    await acc_client.send_message(int(user), message_content)
                    sent_count += 1
                    await asyncio.sleep(random.randint(1, 5))
                except Exception as e:
                    failed_count += 1
                    logger.error(f"خطا در ارسال پیام به {user} با اکانت {current_account}: {e}")
                    if settings['remove_invalid_users'] and 'deleted/deactivated' in str(e).lower():
                        users.remove(user)
                        removed_users += 1
                finally:
                    await acc_client.disconnect()
            except Exception as conn_e:
                logger.error(f"خطا در اتصال با اکانت {current_account}: {conn_e}")
                failed_count += 1

        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(users))

        return (f"📊 گزارش ارسال پیام:\n"
                f"✅ ارسال موفق: {sent_count}\n"
                f"❌ ارسال ناموفق: {failed_count}\n"
                f"🚫 حذف کاربران غیرفعال: {removed_users}")
    return "فایل‌های مورد نیاز وجود ندارند."

@client.on(events.NewMessage(pattern=r'^addacc (\+\d+)$'))
async def add_account(event):
    sender_id = event.sender_id
    phone_number = event.pattern_match.group(1)

    if sender_id != BOT_OWNER_ID:
        return await event.reply("⛔ شما اجازه این کار را ندارید.")

    accounts = load_accounts()
    if phone_number in accounts:
        return await event.reply("⚠️ این شماره قبلاً اضافه شده است.")

    accounts[phone_number] = {"status": "pending"}
    save_accounts(accounts)

    new_client = TelegramClient(f'session_{phone_number}', API_ID, API_HASH)
    await new_client.connect()

    try:
        sent_code = await new_client.send_code_request(phone_number)
        accounts[phone_number]["hash"] = sent_code.phone_code_hash
        save_accounts(accounts)
        await event.reply(f"📩 کد تأیید به شماره {phone_number} ارسال شد.\n لطفاً کد را با دستور `verifyacc {phone_number} 12345` وارد کنید.\n اکانت نباید دارای ورود دو مرحله ای باشد.")
    except Exception as e:
        await event.reply(f"⚠️ خطا در ارسال کد: {e}")

@client.on(events.NewMessage(pattern=r'^verifyacc (\+\d+) (\d+)$'))
async def verify_account(event):
    sender_id = event.sender_id
    phone_number = event.pattern_match.group(1)
    code = event.pattern_match.group(2)

    if sender_id != BOT_OWNER_ID:
        return await event.reply("⛔ شما اجازه این کار را ندارید.")

    accounts = load_accounts()
    if phone_number not in accounts or "hash" not in accounts[phone_number]:
        return await event.reply("⚠️ شماره معتبر نیست یا هنوز کد ارسال نشده است.")

    new_client = TelegramClient(f'session_{phone_number}', API_ID, API_HASH)
    await new_client.connect()

    try:
        await new_client.sign_in(phone_number, code, phone_code_hash=accounts[phone_number]["hash"])
        accounts[phone_number]["status"] = "active"
        save_accounts(accounts)
        await event.reply(f"✅ شماره {phone_number} با موفقیت اضافه شد.")
    except Exception as e:
        await event.reply(f"⚠️ خطا در تأیید کد: {e}")
    finally:
        await new_client.disconnect()

@client.on(events.NewMessage(pattern=r'^accs$'))
async def list_accounts(event):
    sender_id = event.sender_id
    if sender_id != BOT_OWNER_ID:
        return await event.reply("⛔ شما اجازه این کار را ندارید.")

    accounts = load_accounts()
    if not accounts:
        return await event.reply("⚠️ هیچ اکانتی ثبت نشده است.")

    msg = "**📋 لیست اکانت‌ها:**\n"
    for phone, data in accounts.items():
        status = "✅ فعال" if data.get("status") == "active" else "⏳ در انتظار تأیید"
        msg += f"- {phone}: {status}\n"

    await event.reply(msg)

@client.on(events.NewMessage(pattern=r'^delacc (\+\d+)$'))
async def delete_account(event):
    sender_id = event.sender_id
    phone_number = event.pattern_match.group(1)

    if sender_id != BOT_OWNER_ID:
        return await event.reply("⛔ شما اجازه این کار را ندارید.")

    accounts = load_accounts()
    if phone_number not in accounts:
        return await event.reply("⚠️ این شماره در لیست نیست.")

    del accounts[phone_number]
    save_accounts(accounts)

    session_file = f'session_{phone_number}.session'
    if os.path.exists(session_file):
        try:
            os.remove(session_file)  # حذف فایل سشن
        except Exception as e:
            logger.error(f"خطا در حذف فایل سشن {session_file}: {e}")
    await event.reply(f"✅ اکانت {phone_number} با موفقیت حذف شد.")

@client.on(events.NewMessage)
async def command_handler(event):
    sender_id = event.sender_id
    message = event.raw_text.lower()
    
    # ذخیره کاربر چت در گروه (در صورت فعال بودن)
    if settings.get('chat_user') and event.is_group:
        save_user(sender_id)

    if sender_id == BOT_OWNER_ID:
        if message == 'bot':
            await event.reply("سلام، آنلاینم! کارت رو بگو.")
        elif message == 'onlastseen':
            settings['filter_last_seen'] = True  # استفاده از کلید ثابت
            save_settings(settings)
            await event.reply("فیلتر آخرین بازدید فعال شد.")
        elif message == 'offlastseen':
            settings['filter_last_seen'] = False
            save_settings(settings)
            await event.reply("فیلتر آخرین بازدید غیرفعال شد.")
        elif message == 'invaliduseron':
            settings['remove_invalid_users'] = True
            save_settings(settings)
            await event.reply("حذف کاربران نامعتبر فعال شد.")
        elif message == 'invaliduseroff':
            settings['remove_invalid_users'] = False
            save_settings(settings)
            await event.reply("حذف کاربران نامعتبر غیرفعال شد.")
        elif message.startswith('setlimit'):
            try:
                limit = int(message.split()[1])
                settings['daily_limit'] = limit
                save_settings(settings)
                await event.reply(f"حد ارسال روزانه روی {limit} پیام تنظیم شد.")
            except Exception as e:
                await event.reply("فرمت اشتباه است. استفاده صحیح: setlimit 50")
        elif message == 'sendreport':
            report = await send_messages()
            await event.reply(report)
        elif message == 'checkban':
            status_msg = await check_ban()
            await event.reply(status_msg)
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
            result = await update_bio()
            await event.reply(result)
        elif message == 'biooff':
            settings['random_bio'] = False
            save_settings(settings)
            await event.reply("بیوگرافی تصادفی غیرفعال شد.")
        elif message == 'autojoinon':
            settings['auto_join'] = True
            save_settings(settings)
            await event.reply("✅ ورود خودکار به گروه‌ها *فعال* شد.")
        elif message == 'autojoinoff':
            settings['auto_join'] = False
            save_settings(settings)
            await event.reply("❌ ورود خودکار به گروه‌ها *غیرفعال* شد.")
        elif message.startswith("setnewpm"):
            parts = event.raw_text.split("\n", 1)
            if len(parts) < 2:
                await event.reply("⚠️ لطفاً پیام جدید خود را در خط جدید بعد از `setnewpm` بنویسید.")
                return

            new_message = parts[1].strip()
            with open(MESSAGE_FILE, "w", encoding="utf-8") as f:
                f.write(new_message)

            await event.reply("✅ پیام جدید با موفقیت ذخیره شد.")
            logger.info("پیام جدید ذخیره شد.")
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
                        logger.error(f"خطا در ارسال پیام به {user}: {e}")

                await event.reply("پیام‌ها با موفقیت ارسال شدند.")
            else:
                await event.reply("فایل‌های مورد نیاز وجود ندارند.")
        elif message == 'info':
            total_users = 0
            if os.path.exists(USERS_FILE):
                with open(USERS_FILE, 'r', encoding='utf-8') as f:
                    total_users = len(f.read().splitlines())

            info_text = (
                f"وضعیت ربات: {'آنلاین' if client.is_connected() else 'آفلاین'}\n"
                f"تعداد کاربران جمع شده: {total_users}\n"
                f"جمع‌آوری لیست اعضای گروه: {'فعال' if settings.get('save_user') else 'غیرفعال'}\n"
                f"جمع‌آوری یوزرهای درحال چت: {'فعال' if settings.get('chat_user') else 'غیرفعال'}\n"
                f"بیوگرافی تصادفی: {'فعال' if settings.get('random_bio') else 'غیرفعال'}\n"
            )
            await event.reply(info_text)
        elif message == 'help':
            help_text = (
                "📌 **راهنمای دستورات ربات Mokhber**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🤖 **وضعیت ربات:**\n"
                "🔹 `bot` - بررسی آنلاین بودن ربات\n"
                "🔹 `info` - نمایش اطلاعات کلی ربات\n"
                "🔹 `checkban` - بررسی مسدود بودن ربات\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "📩 **ارسال پیام‌ها:**\n"
                "🔹 `sendpm` - ارسال پیام تبلیغاتی به تمام کاربران ذخیره‌شده\n"
                "🔹 `setnewpm` - تغییر متن پیام تبلیغاتی (متن جدید در خط بعدی)\n"
                "🔹 `sendreport` - دریافت گزارش ارسال پیام‌ها\n"
                "🔹 `setlimit <عدد>` - تنظیم محدودیت ارسال روزانه (به عنوان مثال: `setlimit 10`)\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "👥 **مدیریت کاربران:**\n"
                "🔹 `saveuseron` - فعال‌سازی ذخیره خودکار کاربران گروه‌ها\n"
                "🔹 `saveuseroff` - غیرفعال‌سازی ذخیره کاربران گروه‌ها\n"
                "🔹 `chatuseron` - فعال‌سازی ذخیره کاربران پیام‌دهنده در گروه‌ها\n"
                "🔹 `chatuseroff` - غیرفعال‌سازی ذخیره کاربران پیام‌دهنده در گروه‌ها\n"
                "🔹 `invaliduseron` - فعال‌سازی حذف خودکار کاربران نامعتبر\n"
                "🔹 `invaliduseroff` - غیرفعال‌سازی حذف خودکار کاربران نامعتبر\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "🔧 **ویژگی‌های اضافی:**\n"
                "🔹 `bioon` - فعال‌سازی به‌روزرسانی تصادفی بیو\n"
                "🔹 `biooff` - غیرفعال‌سازی به‌روزرسانی تصادفی بیو\n"
                "🔹 `onlastseen` - ارسال پیام تنها به کاربران فعال در ۲۴ ساعت اخیر\n"
                "🔹 `offlastseen` - ارسال پیام به تمامی کاربران ذخیره‌شده\n"
                "🔹 `autojoinon` - فعال‌سازی ورود خودکار به گروه‌ها از طریق لینک\n"
                "🔹 `autojoinoff` - غیرفعال‌سازی ورود خودکار به گروه‌ها\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "📱 **مدیریت اکانت‌ها:**\n"
                "🔹 `addacc <شماره>` - افزودن یک اکانت جدید (مثال: `addacc +989191234567`)\n"
                "🔹 `verifyacc <شماره> <کد>` - تأیید اکانت با وارد کردن کد دریافت‌شده (مثال: `verifyacc +989191234567 12345`)\n"
                "🔹 `delacc <شماره>` - حذف یک اکانت (مثال: `delacc +989191234567`)\n"
                "🔹 `accs` - مشاهده لیست اکانت‌ها و وضعیت آن‌ها\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "❓ **راهنما:**\n"
                "🔹 `help` - نمایش این لیست دستورات\n"
            )
            await event.reply(help_text, parse_mode='markdown')


@client.on(events.ChatAction)
async def chat_action_handler(event):
    if settings.get('save_user') and event.user_added:
        # ذخیره کاربران گروه در مواقعی که کاربر اضافه می‌شود
        if event.chat and event.is_group:
            for user in event.users:
                save_user(user.id)

# اجرای کلاینت
logger.info("ربات در حال اجرا است...")
client.run_until_disconnected()
