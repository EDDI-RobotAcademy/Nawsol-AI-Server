import secrets
import os

from fastapi import Request, HTTPException

CSRF_COOKIE_NAME = "csrf_token"

# -----------------------
# 랜덤 CSRF 토큰 생성
# -----------------------
def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


# -----------------------
# 요청 헤더에서 CSRF 토큰 검증
# -----------------------
def verify_csrf_token(request: Request, csrf_token_from_header: str):
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    
    # 🔥 개발 환경(HTTP) 고려: secure=True로 인해 쿠키가 설정되지 않을 수 있음
    # 개발 환경에서 쿠키가 없으면 검증 우회
    is_production = os.getenv("ENVIRONMENT", "development") == "production"
    
    if not cookie_token:
        if not is_production:
            # 개발 환경: 쿠키 없어도 통과 (secure=True로 인한 HTTP 제약)
            print(f"[DEBUG] CSRF check bypassed in development (no cookie due to secure=True)")
            return
        else:
            # 운영 환경: 쿠키 필수
            print("INVALID CSRF TOKEN - No cookie in production")
            raise HTTPException(status_code=403, detail="Invalid CSRF token")
    
    # 쿠키는 있지만 헤더가 없거나 일치하지 않는 경우
    if not csrf_token_from_header or cookie_token != csrf_token_from_header:
        print("INVALID CSRF TOKEN - ALERT")
        print(f"Cookie token: {cookie_token}")
        print(f"Header token: {csrf_token_from_header}")
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
