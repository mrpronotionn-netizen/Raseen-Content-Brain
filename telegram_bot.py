import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# استبدل هذا بالتوكن الخاص ببوك تيليجرام الخاص بك
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# مسار ملف البيانات أو قائمة العناصر المرسلة
DATA_FILE = "videos_data.json"

def load_data():
    """تحميل البيانات (يمكنك ربطه بقاعدة بيانات أو ملف JSON المحلي)"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

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
    # يمكنك تمرير البيانات هنا أو قراءتها مباشرة من القائمة التي زودتني بها
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

async def button_callback(context: ContextTypes.DEFAULT_TYPE, update: Update):
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
        # هنا يمكنك إضافة كود الربط لمنصات النشر أو تشغيل الأتمتة عبر Make/n8n
    elif action == "edit":
        await query.message.reply_text(fللفيديو ذي المعرف #{video_id}. أرسل لي التعديل المطلوبة.")
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
    # حفظ البيانات الواردة مؤقتاً لتسهيل القراءة للاختبار
    if not os.path.exists(DATA_FILE):
        sample_data = [...] # البيانات التي أرسلتها
        # with open(DATA_FILE, "w", encoding="utf-8") as f:
        #     json.dump(sample_data, f, ensure_ascii=False, indent=2)
            
    main()
