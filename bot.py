import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
import time

# --- تنظیمات اصلی ---
TOKEN = '8292483737:AAHnxnWCgcKCVAmLOFefVSTqrzce7Lbsyc4'
ADMIN_ID = 7566531905
SUPPORT_USERNAME = '@Dbxhdv'

bot = telebot.TeleBot(TOKEN)

referrals = {}
custom_buttons = {}
welcome_message = "سلام به ربات خوش اومدی 🌹 از دکمه‌های زیر استفاده کن:"

# /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if len(message.text.split()) > 1:
        ref_id = message.text.split()[1]
        if ref_id != str(user_id):
            if ref_id not in referrals:
                referrals[ref_id] = []
            if user_id not in referrals[ref_id]:
                referrals[ref_id].append(user_id)

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("📋 قوانین", callback_data='rules'))
    keyboard.add(InlineKeyboardButton("🧑‍💼 پشتیبانی", url=f'https://t.me/{SUPPORT_USERNAME.strip("@")}'))
    keyboard.add(InlineKeyboardButton("📣 لینک زیرمجموعه‌گیری", callback_data='referral'))

    for btn in custom_buttons:
        keyboard.add(InlineKeyboardButton(btn, callback_data=f'custom_{btn}'))

    # اضافه کردن دکمه حذف دکمه‌ها
    keyboard.add(InlineKeyboardButton("🗑 حذف دکمه‌ها", callback_data='clear_buttons'))

    bot.send_message(user_id, welcome_message, reply_markup=keyboard)

# دکمه‌ها
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    user_id = call.from_user.id
    if call.data == 'rules':
        bot.answer_callback_query(call.id)
        bot.send_message(user_id, "📋 قوانین:\n۱. ادب را رعایت کن\n۲. سوال داشتی به پشتیبانی پیام بده.")
    elif call.data == 'referral':
        link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        count = len(referrals.get(str(user_id), []))
        bot.send_message(user_id, f"📣 لینک شما:\n{link}\n👥 زیرمجموعه‌ها: {count}")
    elif call.data == 'clear_buttons':
        if user_id == ADMIN_ID:
            custom_buttons.clear()
            bot.answer_callback_query(call.id, "✅ دکمه‌ها حذف شدند.")
        else:
            bot.answer_callback_query(call.id, "⛔ شما اجازه این کار را ندارید.")
    elif call.data.startswith('custom_'):
        key = call.data.replace('custom_', '')
        reply = custom_buttons.get(key, '❌ دکمه تعریف نشده.')
        bot.send_message(user_id, reply)

# فقط مدیر
def is_admin(message):
    return message.from_user.id == ADMIN_ID

# پنل مدیریت
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message): return
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ افزودن دکمه", "✏️ تنظیم پاسخ دکمه")
    markup.add("📢 پیام همگانی", "👥 پیام به زیرمجموعه‌ها")
    markup.add("📃 لیست زیرمجموعه‌ها", "🎉 تنظیم پیام خوش‌آمد")
    markup.add("🔙 خروج از پنل")
    bot.send_message(message.chat.id, "🔧 پنل مدیریت:", reply_markup=markup)

# دستورات مدیر
@bot.message_handler(func=is_admin)
def admin_actions(message):
    text = message.text

    if text == "➕ افزودن دکمه":
        bot.send_message(message.chat.id, "📝 نام دکمه را ارسال کنید:")
        bot.register_next_step_handler(message, save_button_name)

    elif text == "✏️ تنظیم پاسخ دکمه":
        bot.send_message(message.chat.id, "📝 نام دکمه‌ای که می‌خوای پاسخ براش تنظیم کنی:")
        bot.register_next_step_handler(message, set_button_response)

    elif text == "📢 پیام همگانی":
        bot.send_message(message.chat.id, "📝 متن پیام همگانی را بفرست:")
        bot.register_next_step_handler(message, send_broadcast)

    elif text == "👥 پیام به زیرمجموعه‌ها":
        bot.send_message(message.chat.id, "📝 متن پیام برای زیرمجموعه‌ها:")
        bot.register_next_step_handler(message, send_to_refs)

    elif text == "📃 لیست زیرمجموعه‌ها":
        all_refs = []
        for k, v in referrals.items():
            all_refs.append(f"{k}: {len(v)} نفر")
        text = "\n".join(all_refs) or "هیچ زیرمجموعه‌ای ثبت نشده."
        bot.send_message(message.chat.id, text)

    elif text == "🎉 تنظیم پیام خوش‌آمد":
        bot.send_message(message.chat.id, "📝 پیام خوش‌آمد جدید را بفرست:")
        bot.register_next_step_handler(message, set_welcome)

    elif text == "🔙 خروج از پنل":
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(message.chat.id, "از پنل مدیریت خارج شدی.", reply_markup=markup)

# افزودن دکمه جدید
def save_button_name(message):
    name = message.text.strip()
    if name in custom_buttons:
        bot.send_message(message.chat.id, "این دکمه قبلاً ثبت شده.")
    else:
        custom_buttons[name] = "پاسخی تنظیم نشده."
        bot.send_message(message.chat.id, f"✅ دکمه {name} ثبت شد.")

# تنظیم پاسخ دکمه
def set_button_response(message):
    btn_name = message.text.strip()
    if btn_name not in custom_buttons:
        bot.send_message(message.chat.id, "⛔ دکمه‌ای با این نام وجود ندارد.")
    else:
        bot.send_message(message.chat.id, "📝 متن پاسخ برای این دکمه را ارسال کن:")
        bot.register_next_step_handler(message, lambda msg: save_button_response(btn_name, msg))

def save_button_response(btn, message):
    custom_buttons[btn] = message.text
    bot.send_message(message.chat.id, f"✅ پاسخ دکمه {btn} ذخیره شد.")

# تنظیم پیام خوش‌آمد
def set_welcome(message):
    global welcome_message
    welcome_message = message.text
    bot.send_message(message.chat.id, "✅ پیام خوش‌آمد بروزرسانی شد.")

# ارسال همگانی
def send_broadcast(message):
    text = message.text
    try:
        users = set()
        for lst in referrals.values():
            users.update(lst)
        users.update(referrals.keys())
        for uid in users:
            bot.send_message(uid, text)
        bot.send_message(message.chat.id, f"✅ پیام به {len(users)} کاربر ارسال شد.")
    except:
        bot.send_message(message.chat.id, "❌ خطا در ارسال پیام.")

# پیام به زیرمجموعه‌ها
def send_to_refs(message):
    text = message.text
    count = 0
    for users in referrals.values():
        for uid in users:
            try:
                bot.send_message(uid, text)
                count += 1
            except:
                pass
    bot.send_message(message.chat.id, f"✅ پیام به {count} زیرمجموعه ارسال شد.")

# راه‌اندازی دائم
print("✅ ربات با موفقیت فعال شد...")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("❌ خطا:", e)
        time.sleep(5)
