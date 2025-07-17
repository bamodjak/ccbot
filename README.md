# ✅ Card Checker Bot
A Telegram bot to:
- Accept API keys from users (sk_test_... or sk_live_...)
- Generate Luhn-valid credit card numbers from BINs
- Validate cards using  Tokens + PaymentMethod API
...
ccbot/
├── main.py                     # 🔁 Full Telegram bot logic w/ UI, session, admin
├── generator.py                # 🎲 Card generator using Luhn and BIN metadata
├── checker.py                  # ✅ Batch validation using token + gateway
├── validation_api.py           # 🔌 All gateway logic: Stripe, PayPal, Mollie, Adyen, etc.
├── utils/
│   ├── luhn.py                 # 🔢 Luhn checksum/validation logic
│   ├── randoms.py              # 🎰 Random BIN, expiry, CVV generators
│   ├── parsers.py              # 🧩 Input parsing for card formats
│   └── delays.py               # ⏱ Async delay/cooldown utils (optional)
├── requirements.txt            # 📦 All Python deps: telegram, stripe, dotenv, etc.
├── Procfile                    # 🧬 Railway/Render support (worker = python main.py)
├── Dockerfile                  # 🐳 For optional container deployment
├── .env.example                # 🛠 Example config for secret keys and admin ID
├── README.md                   # 📘 Project overview, setup, and notes


