
# test_run.py
from manager import MemoryManager

# إنشاء كائن لإدارة الذاكرة
memory = MemoryManager()

# 1. تجربة إضافة ذاكرة جديدة
print("--- تجربة الإضافة ---")
result = memory.add_memory(
    memory_type="project_note",
    title="مشروع رصين - اختبار",
    content="هذه ملاحظة تجريبية للتحقق من عمل النظام.",
    source_url="https://example.com"
)
print("نتيجة الإضافة:", result)

# 2. تجربة فحص الوجود (منع التكرار)
print("\n--- تجربة إضافة نفس العنوان (فحص التكرار) ---")
duplicate_result = memory.add_memory(
    memory_type="project_note",
    title="مشروع رصين - اختبار",
    content="محتوى مكرر"
)
print("نتيجة التكرار:", duplicate_result)

# 3. تجربة البحث
print("\n--- تجربة البحث ---")
search_results = memory.search(query="رصين")
print("نتائج البحث:", search_results)

# 4. تجربة عرض أحدث السجلات
print("\n--- تجربة عرض أحدث السجلات ---")
recent_memories = memory.recent(limit=5)
print("السجلات الأخيرة:", recent_memories)