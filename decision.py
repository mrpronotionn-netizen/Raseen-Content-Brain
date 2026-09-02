import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.manager import MemoryManager

class BrainDecisionEngine:
    def __init__(self):
        self.memory = MemoryManager()

    def make_decision(self, title, is_approved, priority, reasoning):
        """
        اتخاذ القرار النهائي بشأن فكرة المحتوى وتحديد أولويتها (High, Medium, Low)
        """
        decision_status = "approved_for_content" if is_approved else "rejected_by_brain"
        
        content = f"الأولوية: {priority}\nسبب القرار: {reasoning}"
        
        result = self.memory.add_memory(
            memory_type="decision",
            title=f"قرار: {title}",
            content=content,
            status=decision_status,
            decision="approve" if is_approved else "reject",
            decision_reason=reasoning
        )
        return result