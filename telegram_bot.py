import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# التوكن ومعرف المحادثة الخاص بك
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8960674717:AAHvKloB4Ajz7h2rt2sqO2tDRFkipbkinw")
DEFAULT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1719115694")

# مسار ملف البيانات أو قائمة العناصر المرسلة
DATA_FILE = "videos_data.json"

def load_data():
    """تحميل البيانات من ملف JSON المحلي"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

async def send_telegram_message(text, chat_id=None, token=None):
    """دالة مساعدة لإرسال الرسائل النصية عند طلبها من أي ملف آخر (مثل main.py)"""
    bot_token = token or TELEGRAM_TOKEN
    target_chat = chat_id or DEFAULT_CHAT_ID
    bot = Bot(token=bot_token)
    async with bot:
        await bot.send_message(chat_id=target_chat, text=text, parse_mode="Markdown")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب وأوامر البوت الأساسية"""
    welcome_text = (
        "اهلاً بك يا فنان! 🎬\n"
        "أنا بوت إدارة وتدفق الفيديوهات الخاصة بنظام **رصين PRO**.\n\n"
        "الأوامر المتاحة:\n"
        "/pending - استعراض الفيديوهات الجاهزة للمراجعة والنشر 🚀"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def show_pending_videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """جلب وعرض الفيديوهات الجاهزة للنشر من القائمة"""
    data = load_data()
    
    # تصفية العناصر المنتجة والتي تمتلك فيديو نهائي
    produced_videos = [
        item for item in data 
        if item.get("status") == "produced" or "videos/final_" in item.get("reason", "")
    ]

    if not produced_videos:
        await update.message.reply_text("لا توجد فيديوهات جاهزة حالياً في الانتظار. كل الأمور تحت السيطرة! ✨")
        return

    for item in produced_videos:
        video_id = item.get("id")
        title = item.get("title")
        reason = item.get("reason", "")
        
        # استخراج مسار الفيديو من السبب إذا وجد
        video_path = ""
        for line in reason.split("\n"):
            if "الفيديو النهائي:" in line:
                video_path = line.split("الفيديو النهائي:")[1].strip()

        caption = (
            f"📌 **عنوان الفيديو:** {title}\n"
            f"🆔 **المعرف:** {video_id}\n"
            f"📊 **التقييم:** {item.get('score', 'N/A')}\n\n"
            f"📝 *التفاصيل:* \n{reason}"
        )

        # أزرار التحكم التفاعلية
        keyboard = [
            [
                InlineKeyboardButton("✅ موافقة ونشر", callback_data=f"approve_{video_id}"),
                InlineKeyboardButton("🔄 تعديل", callback_data=f"edit_{video_id}")
            ],
            [
                InlineKeyboardButton("❌ رفض وحذف", callback_data=f"reject_{video_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # إرسال الفيديو إن وجد الملف محلياً، أو إرسال تفاصيله كبطاقة نصية
        if video_path and os.path.exists(video_path):
            with open(video_path, "rb") as video_file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=video_file,
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"⚠️ (ملف الفيديو غير موجود محلياً)\n\n{caption}",
                parse_mode="Markdown",
                reply_markup=reply_markup
            )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التعامل مع ضغطات الأزرار من الجوال"""
    query = update.callback_query
    await query.answer()
    
    data_parts = query.data.split("_")
    action = data_parts[0]
    video_id = data_parts[1]

    if action == "approve":
        await query.edit_message_caption(
            caption=f"{query.message.caption}\n\n✨ **الحالة:** تم الموافقة على النشر بنجاح! 🚀"
        )
    elif action == "edit":
        await query.message.reply_text(f"للفيديو ذي المعرف #{video_id}. أرسل لي التعديل المطلوب.")
    elif action == "reject":
        await query.edit_message_caption(
            caption=f"{query.message.caption}\n\n❌ **الحالة:** تم رفض وحذف الفيديو."
        )

def main():
    # بناء تطبيق البوت
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pending", show_pending_videos))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("🤖 بوت تيليجرام يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == "__main__":
    main()
    async def send_telegram_message(text, chat_id=None, token=None):
    """دالة مساعدة متوافقة مع استدعاءات main.py"""
    import telegram
    bot_token = token or TELEGRAM_TOKEN
    target_chat = chat_id or "1719115694"
    bot = telegram.Bot(token=bot_token)
    async with bot:
        await bot.send_message(chat_id=target_chat, text=text, parse_mode="Markdown")
