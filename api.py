from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import run_raseen_pipeline
import uvicorn

# تعريف شكل الطلب القادم من الجوال
class ContentRequest(BaseModel):
    topic_title: str
    raw_content: str
    source_platform: str = "unknown"
    engagement_score: int = 50
    is_emergency: bool = False

# إنشاء تطبيق FastAPI
app = FastAPI(title="Raseen Brain API", description="مدير المحتوى الذكي لإنتاج الفيديو")

@app.post("/generate")
async def generate_video(request: ContentRequest):
    """
    يستقبل الجوال بيانات الموضوع، ويشغل محرك العقل، ويعيد النتيجة مباشرة.
    """
    try:
        result = run_raseen_pipeline(
            topic_title=request.topic_title,
            raw_content=request.raw_content,
            source_platform=request.source_platform,
            engagement_score=request.engagement_score,
            is_emergency=request.is_emergency
        )
        if result["status"] == "failed":
            raise HTTPException(status_code=400, detail=result.get("error", "فشل في المعالجة"))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "Raseen Brain is Alive!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)