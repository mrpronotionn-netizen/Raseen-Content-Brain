import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from social.listener import SocialListeningEngine

print("\n=== RASEEN SOCIAL LISTENING ENGINE TEST ===")

listener = SocialListeningEngine()

# اختبار التقاط إشارة اجتماعية وتقييم تفاعلها
signal_result = listener.process_social_signal(
    topic="تحديثات الرؤية الحاسوبية ومعالجة البيانات في رصين",
    source_platform="X / Twitter",
    engagement_score=88,
    is_fact=True
)

print("\nSOCIAL SIGNAL RESULT:")
print(signal_result)

print("\n=== SOCIAL LISTENING ENGINE TEST FINISHED ===")