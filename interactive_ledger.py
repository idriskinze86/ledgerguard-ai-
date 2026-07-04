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

def generate_local_report():
    file_name = "ledger.csv"
    if not os.path.exists(file_name):
        print("\n⚠️ No ledger data found. Try logging an expense first!")
        return

    print("\n📊 --- Local Ledger Balance Sheet Summary --- 📊")
    total_expenses_ngn = 0.0
    total_income_ngn = 0.0
    total_entries = 0

    with open(file_name, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Extract numeric values from formatted strings (removing commas, currency symbols, and text labels)
                income_str = row["Gross_Income_Fiat"].split(" ")[0].replace(",", "")
                expense_field = row["Local_Expense"]
                
                # Handle multi-currency expense formatting extraction
                if "(" in expense_field and "NGN" in expense_field:
                    expense_str = expense_field.split("(")[1].split(" ")[0].replace(",", "")
                else:
                    expense_str = expense_field.split(" ")[0].replace(",", "")
                
                total_income_ngn += float(income_str)
                total_expenses_ngn += float(expense_str)
                total_entries += 1
            except Exception:
                continue

    net_surplus = total_income_ngn - total_expenses_ngn
    
    print(f"📂 Total Audited Logs: {total_entries}")
    print(f"💰 Cumulative Pool Revenue: {total_income_ngn:,.2f} NGN")
    print(f"💸 Total Outbound Expenses: {total_expenses_ngn:,.2f} NGN")
    print(f"⚖️ Final Net Reconciled Capital: {net_surplus:,.2f} NGN")
    print("--------------------------------------------------")

def process_reconciliation(expense, crypto_amount=150.00, crypto_asset="USDT"):
    print("\n💼 --- LedgerLink AI Multi-Currency Engine --- 💼")
    current_rate = get_live_exchange_rate()
    
    total_fiat_earned_ngn = crypto_amount * current_rate
    expense_currency = expense["currency_fiat"].strip().upper()
    expense_amount_raw = expense["amount_fiat"]
    
    if expense_currency in ["USD", "USDT"]:
        expense_amount_ngn = expense_amount_raw * current_rate
        display_expense = f"{expense_amount_raw:,.2f} {expense_currency} ({expense_amount_ngn:,.2f} NGN)"
    else:
        expense_amount_ngn = expense_amount_raw
        display_expense = f"{expense_amount_raw:,.2f} {expense_currency}"

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
    print("3: 📊 Generate Local Financial Statement Summary")
    
    choice = input("\nSelect an option (1, 2, or 3): ").strip()
    
    if choice == "1":
        path = input("Enter receipt image path (or press Enter for test fallback): ").strip()
        if not path:
            path = "test_receipt.jpg"
        expense = parse_receipt_image(path)
        if expense:
            process_reconciliation(expense)
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
        if expense:
            process_reconciliation(expense)
    elif choice == "3":
        generate_local_report()
    else:
        print("❌ Invalid Option.")

if __name__ == "__main__":
    main_cli_loop()
