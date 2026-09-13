import os
import requests
from dotenv import load_dotenv

from tiktok_uploader import upload_video_to_tiktok

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text):
    """إرسال رسالة لتطبيق التلغرام"""
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ تعذر إرسال الرسالة: {e}")

def get_telegram_updates(offset=None):
    """جلب الرسائل القادمة من التلغرام"""
    if not BOT_TOKEN:
        return []
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 10, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=12)
        if response.status_code == 200:
            return response.json().get("result", [])
    except Exception as e:
        print(f"⚠️ خطأ أثناء قراءة الرسائل: {e}")
    return []

def handle_incoming_telegram_commands():
    """الاستماع لأوامر الجوال المباشرة وتنفيذ خط الإنتاج فوراً"""
    # استيراد الملف كاملاً لتفادي أخطاء المسميات والتعارض الدوري
    import run_pipeline
    
    offset = None
    print("📱 [Telegram Control] البوت يستمع الآن لأوامرك من الجوال...")

    while True:
        updates = get_telegram_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message", {})
            text = message.get("text", "").strip()
            chat_id = str(message.get("chat", {}).get("id"))

            if CHAT_ID and chat_id != str(CHAT_ID):
                continue

            if text:
                print(f"\n📩 [طلب جديد من الجوال]: {text}")
                
                idea_title = text.replace("/create", "").strip()
                if not idea_title or text == "/start":
                    send_telegram_message(
                        "👋 **أهلاً بك في نظام رصين PRO للتحكم الذكي**\n\n"
                        "💡 أرسل لي أي فكرة مباشرة وسأقوم بإنتاجها ورفعها لـ TikTok Inbox فوراً!"
                    )
                    continue

                send_telegram_message(f"⚡ **[طلب يدوي مقبول]**\nجاري تشغيل خط الإنتاج لفكرتك:\n*{idea_title}*")

                # التكيف مع اسم الدالة الموجودة في run_pipeline سواء كانت run_raseen_pipeline أو run_pipeline
                pipeline_func = getattr(run_pipeline, 'run_raseen_pipeline', None) or getattr(run_pipeline, 'run_pipeline', None)
                
                pipeline_result = {}
                if pipeline_func:
                    pipeline_result = pipeline_func(
                        topic_title=idea_title,
                        raw_content=f"محتوى مخصص تم طلبه يدويًا من التلغرام: {idea_title}",
                        source_platform="Telegram Direct Command",
                        engagement_score=98,
                        is_emergency=True
                    )

                # توليد أصول الفيديو في حال عدم التوليد التلقائي
                video_path = pipeline_result.get("video_path") if isinstance(pipeline_result, dict) else None
                if not video_path:
                    from video_engine.generator import VideoProductionEngine
                    print("🎬 [Direct Trigger] جاري إنتاج أصول الفيديو مباشرة...")
                    video_engine = VideoProductionEngine()
                    prod_res = video_engine.generate_video_assets(script_title=idea_title, script_body=idea_title)
                    video_path = prod_res.get("video_path")

                # الرفع الفعلي لـ TikTok Inbox
                if video_path and os.path.exists(video_path):
                    send_telegram_message("📤 جاري رفع الفيديو كمسودة إلى TikTok Inbox...")
                    upload_success = upload_video_to_tiktok(video_path, title=idea_title, auto_publish=False)
                    
                    if upload_success:
                        send_telegram_message(f"✅ **تم بنجاح!**\nتم رفع فيديو: *{idea_title}*\nتفقّد **TikTok Inbox** في حسابك الآن.")
                    else:
                        send_telegram_message("❌ حدث خطأ أثناء عملية الرفع إلى TikTok.")
                else:
                    send_telegram_message("❌ تعذر توليد ملف الفيديو، يرجى مراجعة سجل النظام.")

if __name__ == "__main__":
    handle_incoming_telegram_commands()