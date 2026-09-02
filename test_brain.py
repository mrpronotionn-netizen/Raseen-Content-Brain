import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from decision import BrainDecisionEngine


# وضعنا الكود داخل دالة تبدأ بـ test_ ليتعرف عليها pytest
def test_brain_decision_engine():
    print("\n=== RASEEN BRAIN DECISION ENGINE TEST ===")

    engine = BrainDecisionEngine()

    # 1. قرار بالموافقة
    approval_decision = engine.make_decision(
        title="إطلاق نموذج ذكاء اصطناعي جديد لرصين",
        is_approved=True,
        priority="High",
        reasoning="الموضوع موثق ومهم جداً للمتابعين ويغطي ميزات جديدة.",
    )
    print("\nAPPROVAL DECISION RESULT:")
    print(approval_decision)

    # 2. قرار بالرفض
    rejection_decision = engine.make_decision(
        title="شائعة غير مؤكدة",
        is_approved=False,
        priority="Low",
        reasoning="لا تتوفر أدلة كافية والفكرة مكررة.",
    )
    print("\nREJECTION DECISION RESULT:")
    print(rejection_decision)

    print("\n=== BRAIN DECISION ENGINE TEST FINISHED ===")

    # تأكيد نجاح الاختبار
    assert approval_decision is not None
    assert rejection_decision is not None