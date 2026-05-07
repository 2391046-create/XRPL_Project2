%%writefile /content/gemini_service.py
import os, json, base64, traceback
from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash"

def analyze_receipt(image_base64: str, target_country: str) -> dict:
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        image_bytes = base64.b64decode(image_base64)
        prompt = f"""
너는 유학생 재정 관리를 돕는 다국어 영수증 분석 전문가야.
영수증 이미지를 분석해서 아래 JSON 형식으로만 대답해. 마크다운 절대 쓰지마.
타겟 화폐: {target_country}
{{
    "merchant": "상호명",
    "items": [{{"name": "상품명", "quantity": 수량, "price": 개당가격, "category": "카테고리(식비/교통/쇼핑/카페/의료/기타 중 하나)"}}],
    "total_amount": 원래화폐_총액숫자,
    "currency": "원래화폐단위",
    "date": "YYYY-MM-DD",
    "target_country": "{target_country}",
    "converted_total": 환산된_총액숫자,
    "dutch_pay_per_person": 더치페이_1인당금액,
    "main_category": "전체영수증의주카테고리"
}}
"""
        response = client.models.generate_content(
            model=MODEL,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                types.Part.from_text(text=prompt),
            ]
        )
        result_text = response.text.strip().replace("```json","").replace("```","").strip()
        return json.loads(result_text)
    except Exception as e:
        traceback.print_exc()
        return {"merchant":"Error","error_detail":str(e),"items":[],"total_amount":0,"currency":"N/A","target_country":target_country}

def analyze_price_before_purchase(content: str, target_country: str, is_image: bool) -> dict:
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        if is_image:
            parts = [
                types.Part.from_bytes(data=base64.b64decode(content), mime_type="image/jpeg"),
                types.Part.from_text(text=f"메뉴판을 분석해서 메뉴명, 가격, {target_country} 환산가를 JSON으로만 반환해줘."),
            ]
        else:
            parts = [types.Part.from_text(text=f"다음 가격 정보를 {target_country}로 환산해서 JSON으로만 반환해줘: {content}")]
        response = client.models.generate_content(model=MODEL, contents=parts)
        result_text = response.text.strip().replace("```json","").replace("```","").strip()
        return json.loads(result_text)
    except Exception as e:
        traceback.print_exc()
        return {"error_detail": str(e)}
