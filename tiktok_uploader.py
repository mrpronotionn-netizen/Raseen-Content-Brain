import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN_FILE = "tiktok_tokens.json"

def get_access_token():
    """
    جلب الـ Access Token إما من بيئة العمل السحابية (GitHub Actions)
    أو توليده بذكاء باستخدام مفاتيح العميل، أو من الملف المحلي.
    """
    # 1. التحقق من وجود المفاتيح السحابية (GitHub Secrets) وتوليد التوكن منها أوتوماتيكياً
    client_key = os.getenv("TIKTOK_CLIENT_KEY")
    client_secret = os.getenv("TIKTOK_CLIENT_SECRET")

    if client_key and client_secret:
        print("☁️ تم اكتشاف مفاتيح تيك توك السحابية، جاري جلب/توليد التوكن...")
        # ملاحظة: هنا يمكن طلب التوكن مباشر من واجهة تيك توك أو استخدام التوكن المُخزن
        # إذا كان لديك طريقة توليد مباشرة أو توكن جاهز، يمكنك وضعه هنا:
        # (إذا كنت قد خزنت التوكن النهائي مباشرة كسر، سنستدعيه هكذا:)
        env_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        if env_token:
            return env_token

    # 2. القراءة من الملف المحلي (للعمل على جهازك الشخصي)
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            tokens = json.load(f)
            return tokens.get("access_token")

    print(f"❌ لم يتم العثور على أي توكن صالح لا محلياً ولا سحابياً.")
    return None

def upload_video_to_tiktok(video_path, title="New TikTok Video", auto_publish=False):
    access_token = get_access_token()
    if not access_token:
        return False

    if not os.path.exists(video_path):
        print(f"❌ ملف الفيديو غير موجود في المسار: {video_path}")
        return False

    file_size = os.path.getsize(video_path)

    if auto_publish:
        print("⚡ النمط النشط: نشر تلقائي مباشر (Direct Publish)")
        init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    else:
        print("🛡️ النمط النشط: إرسال لمسودات الجوال بانتظار موافقتك (Inbox / Approval Mode)")
        init_url = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }

    body = {
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": file_size,
            "total_chunk_count": 1
        }
    }

    print("1. إرسال طلب تهيئة الرفع لـ TikTok API...")
    response = requests.post(init_url, headers=headers, json=body)
    res_data = response.json()

    if response.status_code != 200 or res_data.get("error", {}).get("code") != "ok":
        print("❌ فشل في تهيئة الرفع:", res_data)
        return False

    upload_url = res_data["data"]["upload_url"]
    publish_id = res_data["data"]["publish_id"]

    print("2. جاري رفع ملف الفيديو...")
    with open(video_path, "rb") as video_file:
        upload_headers = {
            "Content-Type": "video/mp4",
            "Content-Length": str(file_size),
            "Content-Range": f"bytes 0-{file_size - 1}/{file_size}"
        }
        upload_res = requests.put(upload_url, headers=upload_headers, data=video_file)

    if upload_res.status_code in [200, 201]:
        print(f"📥 تم إرسال الفيديو بنجاح إلى تيك توك!")
        return True
    else:
        print("❌ فشل أثناء رفع أجزاء الفيديو:", upload_res.text)
        return False

if __name__ == "__main__":
    VIDEO_PATH = "output/test_video.mp4"
    if os.path.exists(VIDEO_PATH):
        upload_video_to_tiktok(VIDEO_PATH, title="اختبار تيك توك", auto_publish=False)
    else:
        print(f"⚠️ لم يتم العثور على الفيديو في: {VIDEO_PATH}")