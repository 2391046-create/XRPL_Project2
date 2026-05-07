%%writefile /content/main.py
import sys
sys.path.insert(0, '/content')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from gemini_service import analyze_receipt, analyze_price_before_purchase
from xrpl_service import record_transaction_with_memo, get_transaction_info, get_account_balance, validate_wallet

app = FastAPI(title="Finance Compass Backend", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class ScanReceiptRequest(BaseModel):
    image_base64: str
    target_country: str = "USD"

class AnalyzePriceRequest(BaseModel):
    image_base64: Optional[str] = None
    text: Optional[str] = None
    target_country: str = "USD"

class RecordXRPLRequest(BaseModel):
    expense_data: dict
    wallet_seed: Optional[str] = None

class TransactionInfoRequest(BaseModel):
    tx_hash: str

class WalletValidationRequest(BaseModel):
    wallet_seed: str

@app.get("/")
async def root():
    return {"status": "Finance Compass API running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "time": datetime.utcnow().isoformat()}

@app.post("/scan-receipt")
async def scan_receipt(req: ScanReceiptRequest):
    try:
        return {"success": True, "data": analyze_receipt(req.image_base64, req.target_country)}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/analyze-price")
async def analyze_price(req: AnalyzePriceRequest):
    try:
        content = req.image_base64 if req.image_base64 else req.text
        if not content:
            raise ValueError("image_base64 또는 text 필요")
        return {"success": True, "data": analyze_price_before_purchase(content, req.target_country, bool(req.image_base64))}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/record-xrpl")
async def record_xrpl(req: RecordXRPLRequest):
    r = record_transaction_with_memo(req.wallet_seed, req.expense_data)
    if r.get("success"):
        return {"success": True, "data": r}
    raise HTTPException(400, r.get("error"))

@app.post("/xrpl/transaction-info")
async def xrpl_tx(req: TransactionInfoRequest):
    r = get_transaction_info(req.tx_hash)
    if r.get("success"):
        return {"success": True, "data": r}
    raise HTTPException(404, r.get("error"))

@app.get("/xrpl/account-balance")
async def xrpl_bal(account_address: Optional[str] = None):
    r = get_account_balance(account_address)
    if r.get("success"):
        return {"success": True, "data": r}
    raise HTTPException(400, r.get("error"))

@app.post("/xrpl/validate-wallet")
async def xrpl_val(req: WalletValidationRequest):
    r = validate_wallet(req.wallet_seed)
    if r.get("success"):
        return {"success": True, "data": r}
    raise HTTPException(400, r.get("error"))
