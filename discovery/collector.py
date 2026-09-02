import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.manager import MemoryManager

class DiscoveryEngine:
    def __init__(self):
        self.memory = MemoryManager()

    def discover_item(self, title, content, source_url=None, category="ai_news"):
        memory_type = f"discovery_{category}"
        result = self.memory.add_memory(
            memory_type=memory_type,
            title=title,
            content=content,
            source_url=source_url,
            status="new"
        )
        return result