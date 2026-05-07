%%writefile /content/xrpl_service.py
def record_transaction_with_memo(wallet_seed, expense_data):
    try:
        return {"success": True, "tx_hash": "SIMULATED_TX_HASH", "ledger_index": 12345678}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_transaction_info(tx_hash):
    return {"success": True, "data": {"hash": tx_hash, "status": "tesSUCCESS"}}

def get_account_balance(account_address):
    return {"success": True, "balance": "10000000"}

def validate_wallet(wallet_seed):
    return {"success": True, "is_valid": True, "address": "rSimulatedAddress"}
