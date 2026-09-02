import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research.researcher import ResearchEngine

print("\n=== RASEEN RESEARCH ENGINE TEST ===")

engine = ResearchEngine()

sources_list = [
    "https://official-source.com/report",
    "https://tech-news.com/article"
]

research_result = engine.process_research(
    title="إطلاق نموذج ذكاء اصطناعي جديد لرصين",
    research_notes="تم فحص الميزات الجديدة: يدعم معالجة الفيديو والتصوير والتحليل الآلي بسرعة فائقة.",
    sources=sources_list
)

print("\nRESEARCH RESULT:")
print(research_result)

print("\n=== RESEARCH ENGINE TEST FINISHED ===")