import os
import json
import base64
import csv
from datetime import datetime
import requests

def get_live_exchange_rate():
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url).json()
        return float(response["rates"]["NGN"])
    except Exception:
        return 1450.00

def parse_receipt_image(image_path):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY not found! Please set it.")
        return None

    if not os.path.exists(image_path):
        print(f"⚠️ Image not found at {image_path}. Defaulting to mock IBEDC data...")
        return {
            "date": "2026-05-12",
            "vendor": "IBEDC (Ibadan Electricity Distribution Company)",
            "amount_fiat": 20000.00,
            "currency_fiat": "NGN",
            "category": "Utilities"
        }

    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode('utf-8')

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [
                {"text": "Extract document data as JSON: {\"date\": \"YYYY-MM-DD\", \"vendor\": \"string\", \"amount_fiat\": float, \"currency_fiat\": \"string\", \"category\": \"string\"}"},
                {"inlineData": {"mimeType": "image/jpeg", "data": base64_image}}
            ]
        }],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1}
    }
    try:
        res = requests.post(url, json=payload).json()
        return json.loads(res['candidates'][0]['content']['parts'][0]['text'])
    except Exception as e:
        print(f"❌ Ingestion Error: {e}")
        return None

def save_to_csv(report, expense_date, category):
    file_name = "ledger.csv"
    file_exists = os.path.exists(file_name)
    
    headers = [
        "Timestamp", "Expense_Date", "Category", "Accounting_Period", 
        "Crypto_Pay", "Exchange_Rate", "Gross_Income_Fiat", 
        "Local_Expense", "Net_Balance", "Status"
    ]
    
    row_data = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        expense_date,
        category,
        report["accounting_period"],
        report["inbound_web3_pay"],
        report["conversion_rate"],
        report["gross_income_fiat"],
        report["local_fiat_expense"],
        report["net_reconciled_balance"],
        report["status"]
    ]
    
    with open(file_name, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row_data)
    print(f"\n💾 Transaction permanently written to '{file_name}'!")

def process_reconciliation(expense, crypto_amount=150.00, crypto_asset="USDT"):
    print("\n💼 --- LedgerLink AI Multi-Currency Engine --- 💼")
    current_rate = get_live_exchange_rate()
    
    # Calculate inbound income in base currency (NGN)
    total_fiat_earned_ngn = crypto_amount * current_rate
    
    # Clean up currency input strings to ensure strict consistency
    expense_currency = expense["currency_fiat"].strip().upper()
    expense_amount_raw = expense["amount_fiat"]
    
    # Multi-currency translation rule logic
    if expense_currency in ["USD", "USDT"]:
        expense_amount_ngn = expense_amount_raw * current_rate
        display_expense = f"{expense_amount_raw:,.2f} {expense_currency} ({expense_amount_ngn:,.2f} NGN)"
    else:
        expense_amount_ngn = expense_amount_raw
        display_expense = f"{expense_amount_raw:,.2f} {expense_currency}"

    # Reconcile final accounts balance sheets
    net_profit_margin_ngn = total_fiat_earned_ngn - expense_amount_ngn
    
    report = {
        "accounting_period": "May 2026",
        "inbound_web3_pay": f"{crypto_amount} {crypto_asset}",
        "conversion_rate": f"1 {crypto_asset} = {current_rate:,.2f} NGN",
        "gross_income_fiat": f"{total_fiat_earned_ngn:,.2f} NGN",
        "local_fiat_expense": f"{display_expense} ({expense['vendor']})",
        "net_reconciled_balance": f"{net_profit_margin_ngn:,.2f} NGN",
        "status": "✅ Fully Settled (Surplus)" if net_profit_margin_ngn >= 0 else "⚠️ Outstanding Deficit"
    }
    
    print(json.dumps(report, indent=4, ensure_ascii=False))
    save_to_csv(report, expense["date"], expense["category"])

def main_cli_loop():
    print("🚀 --- LedgerLink AI Multi-Modal Engine --- 🚀")
    print("1: 📸 Automate Expense via Document Ingestion")
    print("2: ⌨️ Manually Type New Expense Details")
    
    choice = input("\nSelect an ingestion mode (1 or 2): ").strip()
    
    if choice == "1":
        path = input("Enter receipt image path (or press Enter for test fallback): ").strip()
        if not path:
            path = "test_receipt.jpg"
        expense = parse_receipt_image(path)
    elif choice == "2":
        print("\n📝 Enter Expense Metadata manually:")
        vendor = input("Merchant/Vendor Name: ")
        amount = float(input("Amount Paid: "))
        currency = input("Currency Code (e.g. NGN, USD): ").strip().upper()
        date = input("Date (YYYY-MM-DD): ")
        category = input("Category (Utilities/Internet/etc): ")
        expense = {
            "date": date,
            "vendor": vendor,
            "amount_fiat": amount,
            "currency_fiat": currency,
            "category": category
        }
    else:
        print("❌ Invalid Option.")
        return

    if expense:
        process_reconciliation(expense)

if __name__ == "__main__":
    main_cli_loop()
