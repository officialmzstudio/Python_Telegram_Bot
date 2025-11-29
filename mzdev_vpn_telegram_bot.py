import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# --- تنظیمات ---
TOKEN = 'Telegram Token Here' 
ADMIN_ID = 'Admin ID Here'

# --- مراحل گفتگو (States) ---
SELECT_SERVICE, SHOW_PLAN, WAIT_FOR_RECEIPT = range(3)

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# --- داده‌های سرویس‌ها ---
SERVICES_INFO = {
    'v2ray': {
        'title': 'V2Ray - حجمی، قیمت مناسب، سرعت بالا',
        'prices': (
            "💎 **لیست قیمت V2Ray**:\n\n"
            "🔹 20 گیگ: 70 هزار تومان\n"
            "🔹 30 گیگ: 95 هزار تومان\n"
            "🔹 50 گیگ: 148 هزار تومان"
        )
    },
    'openvpn': {
        'title': 'OpenVPN - نامحدود، سرعت بالا، حرفه‌ای',
        'prices': (
            "🛡 **لیست قیمت OpenVPN**:\n\n"
            "🔸 1 ماهه نامحدود (تک کاربر): 200 هزار تومان\n"
            "🔸 1 ماهه نامحدود (دو کاربر): 275 هزار تومان"
        )
    },
    'ssh': {
        'title': 'SSH - نامحدود، سازگار، قیمت مناسب',
        'prices': (
            "🚀 **لیست قیمت SSH**:\n\n"
            "🔹 1 ماهه نامحدود (تک کاربر): 100 هزار تومان\n"
            "🔹 1 ماهه نامحدود (دو کاربر): 150 هزار تومان"
        )
    }
}

PAYMENT_TEXT = (
    "💳 **اطلاعات پرداخت**\n\n"
    "همه سرویس های ما سرعت بالایی دارند و بدون قطعی هستند.\n"
    "درصورتی که سرویس مورد نظرتون رو انتخاب کردید مبلغ رو به شماره کارت زیر واریز کرده و رسید واریزی رو همینجا ارسال کنید.\n\n"
    "`6219861915461023`\n\n"
    "🎥 برای دریافت آموزش استفاده از کانال ما دیدن کنید.\n\n"
    "📎 **لطفاً الان عکس رسید واریز را ارسال کنید:**"
)

# --- توابع شروع و منو ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # خوش‌آمدگویی متفاوت برای ادمین و کاربر
    if user.id == ADMIN_ID:
        await update.message.reply_text("سلام قربان 👋 ربات برای مدیریت آماده است.")
        return ConversationHandler.END
        
    welcome_text = f"سلام {user.first_name} عزیز، به ربات خرید فیلترشکن اینترنت خوش آمدید. 👇"
    
    keyboard = [
        [InlineKeyboardButton("🛍 مشاهده سرویس‌ها", callback_data='services')],
        [InlineKeyboardButton("👤 پشتیبانی", url='https://t.me/officialmzstudio')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    return SELECT_SERVICE

async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton(SERVICES_INFO['v2ray']['title'], callback_data='v2ray')],
        [InlineKeyboardButton(SERVICES_INFO['openvpn']['title'], callback_data='openvpn')],
        [InlineKeyboardButton(SERVICES_INFO['ssh']['title'], callback_data='ssh')],
        [InlineKeyboardButton("🔙 بازگشت", callback_data='back_to_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="🔥 لطفاً نوع سرویس مورد نظر خود را انتخاب کنید:",
        reply_markup=reply_markup
    )
    return SHOW_PLAN

# --- توابع نمایش قیمت و خرید ---

async def show_price_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'back_to_main':
        keyboard = [
            [InlineKeyboardButton("🛍 مشاهده سرویس‌ها", callback_data='services')],
            [InlineKeyboardButton("👤 پشتیبانی", url='https://t.me/officialmzstudio')]
        ]
        await query.edit_message_text("منوی اصلی:", reply_markup=InlineKeyboardMarkup(keyboard))
        return SELECT_SERVICE

    context.user_data['selected_service'] = data
    service_text = SERVICES_INFO[data]['prices']
    
    keyboard = [
        [InlineKeyboardButton("💳 خرید و ارسال رسید", callback_data='buy_process')],
        [InlineKeyboardButton("🔙 بازگشت به سرویس‌ها", callback_data='services')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=service_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return WAIT_FOR_RECEIPT

async def request_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == 'services':
        await show_services(update, context)
        return SHOW_PLAN
        
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("❌ انصراف", callback_data='cancel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=PAYMENT_TEXT,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return WAIT_FOR_RECEIPT

# --- تابع پردازش عکس رسید (سمت کاربر) ---

async def handle_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo_file = update.message.photo[-1].file_id
    selected_service_key = context.user_data.get('selected_service', 'نامشخص')
    service_name = SERVICES_INFO.get(selected_service_key, {}).get('title', selected_service_key)

    caption_for_admin = (
        f"💰 **رسید جدید!**\n\n"
        f"👤 کاربر: {user.first_name} (`{user.id}`)\n"
        f"🛒 سرویس: {service_name}\n\n"
        f"🛠 **راهنمای ارسال کانفیگ:**\n"
        f"1️⃣ **ارسال متن:** دستور `/send {user.id} کانفیگ` را بفرستید.\n"
        f"2️⃣ **ارسال فایل:** فایل را آپلود کنید و در کپشن بنویسید: `/send {user.id}`"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_file,
        caption=caption_for_admin,
        parse_mode='Markdown'
    )

    await update.message.reply_text(
        "✅ رسید شما دریافت شد.\nکانفیگ شما پس از بررسی همینجا ارسال می‌شود."
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("عملیات لغو شد. /start")
    return ConversationHandler.END

# --- توابع ادمین (ارسال متن و فایل) ---

async def admin_send_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال متن کانفیگ (مثل V2Ray)"""
    user = update.effective_user
    if user.id != ADMIN_ID: return

    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("❌ فرمت: `/send user_id متن`")
            return

        target_id = int(args[0])
        msg = " ".join(args[1:])
        
        await context.bot.send_message(chat_id=target_id, text=f"📩 **سفارش شما آماده شد:**\n\n{msg}")
        await update.message.reply_text("✅ متن ارسال شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

async def admin_send_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال فایل کانفیگ (مثل OpenVPN/SSH)"""
    user = update.effective_user
    if user.id != ADMIN_ID: return
    
    # بررسی اینکه آیا فایل کپشن دارد و کپشن با /send شروع شده؟
    caption = update.message.caption
    if not caption or not caption.startswith('/send'):
        return # اگر دستور نبود کاری نکن

    try:
        # استخراج آیدی از کپشن: "/send 123456" -> ["/send", "123456"]
        parts = caption.split()
        if len(parts) < 2:
            await update.message.reply_text("❌ آیدی کاربر در کپشن فایل وارد نشده.")
            return
            
        target_id = int(parts[1])
        document = update.message.document.file_id
        
        # ارسال فایل به کاربر
        await context.bot.send_document(
            chat_id=target_id,
            document=document,
            caption="📩 **سفارش شما آماده شد.\nفایل تنظیمات را دانلود کنید.**"
        )
        await update.message.reply_text("✅ فایل با موفقیت برای کاربر ارسال شد.")
        
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارسال فایل: {e}")

# --- اجرا ---

if __name__ == '__main__':
    print("ربات روشن شد...")
    app = Application.builder().token(TOKEN).build()

    # هندلر گفتگو با مشتری
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECT_SERVICE: [CallbackQueryHandler(show_services, pattern='^services$')],
            SHOW_PLAN: [CallbackQueryHandler(show_price_list, pattern='^(v2ray|openvpn|ssh|back_to_main)$')],
            WAIT_FOR_RECEIPT: [
                CallbackQueryHandler(request_receipt, pattern='^buy_process$'),
                CallbackQueryHandler(show_services, pattern='^services$'),
                CallbackQueryHandler(cancel, pattern='^cancel$'),
                MessageHandler(filters.PHOTO, handle_receipt_photo)
            ],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    app.add_handler(conv_handler)
    
    # هندلرهای ادمین
    # 1. برای متن (دستور معمولی)
    app.add_handler(CommandHandler('send', admin_send_text))
    
    # 2. برای فایل (شناسایی فایل‌هایی که ادمین میفرسته)
    # فیلتر: فقط داکیومنت‌ها + فقط از طرف ادمین + حتما کپشن داشته باشه
    admin_file_filter = filters.Document.ALL & filters.User(user_id=ADMIN_ID) & filters.CAPTION
    app.add_handler(MessageHandler(admin_file_filter, admin_send_file))

    app.run_polling()