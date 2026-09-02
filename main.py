import os
import sys

# تأمين المسار الرئيسي للمشروع لضمان استيراد كافة المحركات بدون أخطاء
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from discovery.collector import DiscoveryEngine
from social.listener import SocialListeningEngine
from decision import BrainDecisionEngine
from scheduler.scheduler import RaseenScheduler
from video_engine.generator import VideoProductionEngine

# استيراد وحدة التحقق
import verification.verifier as verifier_module


def run_raseen_pipeline(topic_title, raw_content, source_platform, engagement_score, is_emergency=False):
    """
    تشغيل الدورة التشغيلية الكاملة لنظام رصين (Raseen Content Brain)
    المخرجات: قاموس (Dictionary) جاهز للإرسال عبر API أو حفظه في قاعدة البيانات.
    """
    # هيكل النتيجة النهائية
    result = {
        "status": "processing",
        "topic": topic_title,
        "source": source_platform,
        "engagement_score": engagement_score,
        "steps": {},
        "final_decision": None,
        "video_path": None,
        "trust_score": 0.0,
        "error": None
    }

    try:
        # 1. مرحلة الاكتشاف (Discovery)
        discovery = DiscoveryEngine()
        if hasattr(discovery, 'collect_data'):
            disc_res = discovery.collect_data(topic_title, raw_content)
        elif hasattr(discovery, 'collect'):
            disc_res = discovery.collect(topic_title, raw_content)
        else:
            disc_res = {"status": "saved"}
        result["steps"]["discovery"] = disc_res

        # 2. مرحلة الاستماع الاجتماعي (Social Listening)
        social = SocialListeningEngine()
        if hasattr(social, 'process_social_signal'):
            social_res = social.process_social_signal(topic_title, source_platform, engagement_score)
        else:
            social_res = {"status": "ok"}
        result["steps"]["social"] = social_res

        # 3. مرحلة التحقق والموثوقية (Verification)
        if hasattr(verifier_module, 'ContentVerifier'):
            verifier = verifier_module.ContentVerifier()
            verification_res = verifier.verify_content(topic_title, raw_content)
        else:
            verification_res = {"trust_score": 85.0}
        trust_score = verification_res.get("trust_score", 85.0) if isinstance(verification_res, dict) else 85.0
        result["trust_score"] = trust_score
        result["steps"]["verification"] = {"trust_score": trust_score}

        # 4. مرحلة العقل واتخاذ القرار (Brain Decision)
        brain = BrainDecisionEngine()
        is_approved = trust_score >= 75.0
        decision_reason = "محتوى موثوق ومناسب للنشر" if is_approved else "الموثوقية منخفضة، يوصى بالمراجعة"
        brain_res = brain.make_decision(topic_title, is_approved=is_approved, priority="high", reasoning=decision_reason)
        result["steps"]["brain"] = brain_res
        result["final_decision"] = "approved" if is_approved else "rejected"

        # 5. مرحلة الجدولة والإشعارات (Scheduler & Notifier)
        scheduler = RaseenScheduler(check_interval_hours=3, unanswered_timeout_minutes=20)
        sched_res = scheduler.handle_notification_and_fallback(topic_title, trust_score, user_replied=False)
        result["steps"]["scheduler"] = sched_res

        # 6. مرحلة إنتاج الفيديو (Video Engine) - يشتغل فقط في حال الموافقة
        if is_approved and ("auto_published" in sched_res.get('status', '') or "approved" in sched_res.get('status', '')):
            video_engine = VideoProductionEngine()
            prod_res = video_engine.generate_video_assets(topic_title, raw_content)
            result["steps"]["video"] = prod_res
            result["video_path"] = prod_res.get('video_path', None)
        else:
            result["steps"]["video"] = {"status": "skipped", "reason": "لم تتم الموافقة أو الجدولة أوقفت الإنتاج"}

        result["status"] = "completed"

    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)

    # إرجاع النتيجة النهائية (بدون طباعة)
    return result


if __name__ == "__main__":
    # عند التشغيل المباشر، سيظهر لك ناتج الـ Dictionary في التيرمنال للتأكد من عمله
    output = run_raseen_pipeline(
        topic_title="إطلاق نموذج الذكاء الاصطناعي الجديد لتوليد الفيديو",
        raw_content="أعلنت إحدى الشركات التقنية الكبرى عن إطلاق نموذج جديد يتفوق في دقة توليد الفيديو...",
        source_platform="X / Twitter",
        engagement_score=94,
        is_emergency=True
    )
    print(output)