import os
import json
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI", "https://www.example.com/callback")
TOKEN_FILE = "tiktok_tokens.json"

def run_auth():
    scope = "user.info.basic,video.upload,video.publish"
    encoded_redirect = urllib.parse.quote(REDIRECT_URI, safe="")
    
    auth_url = (
        f"https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={CLIENT_KEY}"
        f"&scope={scope}"
        f"&response_type=code"
        f"&redirect_uri={encoded_redirect}"
    )

    print("\n" + "="*70)
    print("🔑 انسخ الرابط المباشر التالي وافتحه في متصفحك:")
    print("="*70)
    print(auth_url)
    print("="*70 + "\n")

    code_url = input("بعد الضغط على موافقة، انسخ الرابط الجديد كاملاً من المتصفح وإلصقه هنا واضغط Enter:\n").strip()

    if "code=" in code_url:
        code = code_url.split("code=")[1].split("&")[0]
        exchange_code_for_token(code)
    else:
        print("❌ لم يتم العثور على رمز code في الرابط.")

def exchange_code_for_token(code):
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }

    res = requests.post(url, headers=headers, data=data)
    token_data = res.json()

    if "access_token" in token_data:
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=4)
        print("\n✅ تم استلام وحفظ access_token بنجاح في tiktok_tokens.json!")
    else:
        print("\n❌ فشل الحصول على التوكين:", token_data)

if __name__ == "__main__":
    run_auth()