import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.manager import MemoryManager

class VerificationEngine:
    def __init__(self):
        self.memory = MemoryManager()

    def verify_item(self, title, confidence_score, verification_notes):
        """
        التحقق من صحة المعلومة وتحديد حالة القبول أو الرفض
        """
        status = "verified" if confidence_score >= 0.7 else "rejected"
        decision = "approved" if status == "verified" else "rejected"
        
        content = f"درجة الثقة: {confidence_score * 100}%\nملاحظات التحقق: {verification_notes}"
        
        result = self.memory.add_memory(
            memory_type="verification_log",
            title=f"تحقق: {title}",
            content=content,
            status=status,
            decision=decision,
            decision_reason=verification_notes
        )
        return result