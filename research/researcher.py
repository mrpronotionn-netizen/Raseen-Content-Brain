import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.manager import MemoryManager

class ResearchEngine:
    def __init__(self):
        self.memory = MemoryManager()

    def process_research(self, title, research_notes, sources):
        sources_text = "\n".join(sources) if sources else "لا توجد مصادر"
        content = f"ملاحظات البحث العميق:\n{research_notes}\n\nالمصادر:\n{sources_text}"
        
        result = self.memory.add_memory(
            memory_type="research_data",
            title=f"بحث: {title}",
            content=content,
            source_url=sources[0] if sources else None,
            status="researched"
        )
        return result