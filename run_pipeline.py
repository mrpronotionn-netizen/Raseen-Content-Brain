import os
import sys
import random
import asyncio
import requests
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory.manager import MemoryManager
from video_engine.generator import generate_video
from tiktok_uploader import upload_video_to_tiktok

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
memory_mgr = MemoryManager()

def send_telegram_notification(text):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"⚠️ تعذر إرسال الإشعار: {e}")

def analyze_and_evaluate_trends():
    """محاكاة البحث والتحليل المستمر في الخلفية"""
    candidates = [
        {
            "title": "أهم 3 أدوات ذكاء اصطناعي لأتمتة التسويق توفر عليك 10 ساعات أسبوعياً",
            "score": 88,
            "reason": "حل مشكلة حقيقية للعملاء، يحقق أعلى معدل حفظ وزيارات للملف الشخصي.",
            "hook_type": "سؤال مباشر + حل مشكلة"
        },
        {
            "title": "تحديث طارئ: أداة ذكية جديدة تقلب موازين صناعة المحتوى اليوم!",
            "score": 93,
            "reason": "ترند طارئ مرتفع للغاية يضمن تفاعل فوري ونمو سريع للمتابعين.",
            "hook_type": "خبر عاجل + فرصة ذهبية"
        },
        {
            "title": "كيف تبني أول أتمتة لأعمالك مجاناً وبدون كود لعام 2026",
            "score": 82,
            "reason": "محتوى مرجعي يرفع معدل تحويل المشاهد إلى متابع.",
            "hook_type": "قائمة قيمة مجانية"
        }
    ]
    return random.choice(candidates)

async def produce_and_publish_video(idea_data, is_emergency=False):
    """دورة إنتاج الفيديو الموقّتة أو الطارئة ورفعه لـ TikTok Inbox"""
    title = idea_data.get("title", "فيديو جديد")
    score = idea_data.get("score", 90)
    reason = idea_data.get("reason", "طلب مباشر")
    hook_type = idea_data.get("hook_type", "مباشر")

    prefix = "🚨 **[TikTokAgent - فرصة طارئة عاجلة]**" if is_emergency else "⏱️ **[TikTokAgent - فيديو موعد النشر اليومي]**"
    
    send_telegram_notification(
        f"{prefix}\n\n"
        f"📌 **الموضوع**: {title}\n"
        f"📊 **التقييم**: `{score}/100`\n"
        f"🧠 **السبب**: {reason}\n\n"
        f"⚙️ جاري التوليد والرفع إلى TikTok Inbox للمعاينة..."
    )

    # 1. توليد الفيديو
    try:
        video_path = await generate_video(title)
    except Exception as e:
        print(f"❌ خطأ أثنـاء إنتاج الفيديو: {e}")
        video_path = None

    if not video_path or not os.path.exists(video_path):
        print(f"❌ لم يتم العثور على ملف الفيديو الناتج من المحرك.")
        send_telegram_notification("❌ تعذر توليد ملف الفيديو، يرجى مراجعة سجلات النظام.")
        return False

    # 2. الرفع إلى تيك توك
    upload_success = upload_video_to_tiktok(video_path, f"رصين - {title}")
    
    if upload_success:
        memory_mgr.save_idea(title, score, reason, hook_type, status="inbox_ready")
        time_notice = "جاهز فوراً للنشر للظرف الطارئ!" if is_emergency else "بقيت **30 دقيقة** على موعد النشر المثالي، راجعه واضغط نشر 🚀"
        
        send_telegram_notification(
            f"✅ **[تم الرفع بنجاح لـ TikTok Inbox]**\n\n"
            f"📝 **العنوان**: {title}\n"
            f"🎯 **الإجراء المطلوب**: {time_notice}"
        )
        return True
    else:
        send_telegram_notification("❌ حدث خطأ أثناء عملية الرفع إلى TikTok.")
        return False

def run_background_research():
    """الدورة الخلفية: بحث وتحليل الأفكار وتخزينها دون إيقاف السلسلة عند التكرار"""
    print("\n🔍 [Background Research] جاري مسح الترندات وتحديث بنك الأفكار...")
    trend = analyze_and_evaluate_trends()
    
    if memory_mgr.is_duplicate(trend["title"]):
        print(f"⚠️ الفكرة '{trend['title']}' موجودة سابقاً في الذاكرة، سيتم متابعة التنفيذ...")

    record = memory_mgr.save_idea(
        title=trend["title"],
        score=trend["score"],
        reason=trend["reason"],
        hook_type=trend["hook_type"],
        status="analyzed"
    )
    print(f"🧠 تم حفظ الفكرة بنجاح بكتالوج البحث (التقييم: {trend['score']})")
    
    if trend["score"] >= 90:
        print("🚨 أفكار طارئة! تم اكتشاف فرصة استثنائية ذات تقييم مرتفع.")
        asyncio.run(produce_and_publish_video(trend, is_emergency=True))
    
    return record

def process_daily_scheduled_video():
    """اختيار أفضل فكرة من الذاكرة لإنتاجها قبل النشر بـ 30 دقيقة"""
    print("\n⏰ [Daily Scheduler] حان موعد التجهيز اليومي قبل موعد النشر بـ 30 دقيقة...")
    memory = memory_mgr.load_memory()
    
    candidates = [item for item in memory if item.get("status") == "analyzed"]
    
    if not candidates:
        print("⚠️ لا توجد أفكار جديدة في الذاكرة، سيتم تشغيل بحث سريع...")
        run_background_research()
        memory = memory_mgr.load_memory()
        candidates = [item for item in memory if item.get("status") == "analyzed"]
        
    if candidates:
        best_idea = max(candidates, key=lambda x: x.get("score", 0))
        asyncio.run(produce_and_publish_video(best_idea, is_emergency=False))
    else:
        print("❌ لم يتم العثور على أفكار مناسبة لإنتاج الفيديو.")

def force_custom_idea(title, score=95, reason="طلب يدوي مباشر من المستخدم"):
    """تنفيذ فكرة مخصصة فوراً بناءً على طلبك من التلغرام"""
    print(f"\n⚡ [Manual Trigger] جاري تنفيذ الفكرة المطلوبة فوراً: {title}")
    custom_idea = {
        "title": title,
        "score": score,
        "reason": reason,
        "hook_type": "طلب يدوي مباشر"
    }
    return asyncio.run(produce_and_publish_video(custom_idea, is_emergency=True))

if __name__ == "__main__":
    print("🚀 بدء تشغيل المحرك الرئيسي لـ رصين PRO...")
    if len(sys.argv) > 1:
        custom_title = " ".join(sys.argv[1:])
        force_custom_idea(custom_title)
    else:
        run_background_research()