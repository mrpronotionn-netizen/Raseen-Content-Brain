import os
import sys

# إضافة مجلد المشروع الرئيسي لمسارات بايثون
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.store import remember, recall, search_memory, memory_exists

print("\n=== RASEEN MEMORY STORE TEST ===")

# 1. اختبار الحفظ
remember(
    memory_type="test",
    title="اختبار ذاكرة رصين Direct Store",
    content="تجربة الحفظ المباشر في قاعدة البيانات.",
    source_url=None
)

# 2. اختبار الاسترجاع
memories = recall(limit=5)
print("\n[RECENT MEMORIES]:")
for m in memories:
    print(m)

# 3. اختبار البحث
search_results = search_memory("رصين")
print(f"\n[SEARCH RESULTS FOR 'رصين']: Found {len(search_results)} items.")

print("\n=== MEMORY STORE TEST FINISHED ===")