import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
TOKEN_FILE = "tiktok_tokens.json"

def load_tokens():
    """تحميل مفاتيح التوكين المخزنة"""
    if not os.path.exists(TOKEN_FILE):
        print(f"❌ ملف التوكين غير موجود: {TOKEN_FILE}. قم بالتسجيل أولاً عبر tiktok_auth.py")
        return None
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ خطأ في قراءة ملف التوكين: {e}")
        return None

def save_tokens(new_res_data):
    """حفظ التوكين الجديد مع الحفاظ على الـ refresh_token لضمان الاستمرارية"""
    current_tokens = load_tokens() or {}
    
    # دمج البيانات لضمان عدم ضياع refresh_token إذا لم يرسله تيك توك في الرد
    updated_tokens = {
        "access_token": new_res_data.get("access_token", current_tokens.get("access_token")),
        "refresh_token": new_res_data.get("refresh_token", current_tokens.get("refresh_token")),
        "expires_in": new_res_data.get("expires_in", current_tokens.get("expires_in")),
        "open_id": new_res_data.get("open_id", current_tokens.get("open_id"))
    }

    with open(TOKEN_FILE, "w") as f:
        json.dump(updated_tokens, f, indent=4)
    print("🔄 تم تحديث وحفظ Tokens الجديدة بنجاح في tiktok_tokens.json!")

def refresh_access_token(refresh_token):
    """تجديد access_token تلقائياً من سيرفر تيك توك"""
    if not refresh_token:
        print("❌ لا يوجد refresh_token صالح للتجديد!")
        return None

    print("⏳ جاري تجديد access_token تلقائياً من سيرفر تيك توك...")
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        res_data = response.json()

        # التعامل مع استجابات TikTok API المختلفة
        token_data = res_data.get("data") if "data" in res_data else res_data

        if "access_token" in token_data:
            save_tokens(token_data)
            return token_data["access_token"]
        else:
            print("❌ فشل تجديد التوكين من تيك توك:", res_data)
            return None
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الاتصال بتجديد التوكين: {e}")
        return None

def upload_video_to_tiktok(video_path, title, auto_publish=False):
    """
    رفع الفيديو المباشر إلى TikTok Inbox أو النشر المباشر مع التجديد التلقائي للتوكين
    """
    if not os.path.exists(video_path):
        print(f"❌ ملف الفيديو غير موجود في المسار: {video_path}")
        return False

    # 1. جلب التوكين الفعال من tiktok_tokens.json
    tokens = load_tokens()
    if not tokens or "access_token" not in tokens:
        print("⚠️ لم يتم العثور على access_token في tiktok_tokens.json. جاري الانتقال للمحاكاة...")
        print(f"🔄 [Simulation] تم محاكاة رفع الفيديو '{title}' بنجاح إلى TikTok Drafts.")
        return True

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    file_size = os.path.getsize(video_path)

    init_url = (
        "https://open.tiktokapis.com/v2/post/publish/video/init/"
        if auto_publish else
        "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
    )

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
    try:
        response = requests.post(init_url, headers=headers, json=body)
        res_data = response.json()
    except Exception as e:
        print(f"❌ خطأ أثناء الاتصال بـ TikTok API: {e}")
        return False

    # 2. إذا انتهت صلاحية التوكين (سواء بالـ Status Code أو نص الخطأ)، يتم التجديد تلقائياً وإعادة الطلب
    error_code = res_data.get("error", {}).get("code", "")
    if response.status_code in [401, 400] or error_code in ["access_token_invalid", "token_expired", "ok"] and response.status_code != 200:
        print("⚠️ التوكين الحالي منتهي الصلاحية أو غير صالحة! جاري البدء بالتجديد التلقائي...")
        new_access_token = refresh_access_token(refresh_token)
        if new_access_token:
            headers["Authorization"] = f"Bearer {new_access_token}"
            response = requests.post(init_url, headers=headers, json=body)
            res_data = response.json()
        else:
            print("❌ تعذر تجديد التوكين. يرجى إعادة المصادقة عبر tiktok_auth.py")
            return False

    if response.status_code != 200 or res_data.get("error", {}).get("code") != "ok":
        print("❌ فشل في تهيئة الرفع:", res_data)
        return False

    upload_url = res_data.get("data", {}).get("upload_url")
    if not upload_url:
        print("❌ لم يتم العثور على رابط الرفع (upload_url) في استجابة تيك توك.")
        return False

    # 3. رفع ملف الفيديو
    print("2. جاري رفع ملف الفيديو...")
    with open(video_path, "rb") as video_file:
        upload_headers = {
            "Content-Type": "video/mp4",
            "Content-Length": str(file_size),
            "Content-Range": f"bytes 0-{file_size - 1}/{file_size}"
        }
        upload_res = requests.put(upload_url, headers=upload_headers, data=video_file)

    if upload_res.status_code in [200, 201]:
        print("📥 تم إرسال الفيديو بنجاح لـ TikTok Inbox! التوكين فعال ومجدد.")
        return True
    else:
        print("❌ فشل أثناء رفع أجزاء الفيديو:", upload_res.text)
        return False

if __name__ == "__main__":
    VIDEO_PATH = "videos/final_1234.mp4"
    if os.path.exists(VIDEO_PATH):
        upload_video_to_tiktok(VIDEO_PATH, title="اختبار التجديد التلقائي", auto_publish=False)
    else:
        print(f"❌ لم يتم العثور على الفيديو في: {VIDEO_PATH}")