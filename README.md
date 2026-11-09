# KORA - Pakistani bilingual marketplace (Python / Flask)

## Run in VS Code
1. Install Python 3.10+ and the VS Code extensions: **Python** (ms-python.python) and optionally **Jinja** (VS Code will suggest them).
2. Open this folder in VS Code. Open a terminal (Ctrl+`).
3. `python -m venv venv`  then activate it  (Windows: `venv\Scripts\activate`, Mac/Linux: `source venv/bin/activate`)
4. `pip install -r requirements.txt`
5. `python main.py`  -> the website opens at http://127.0.0.1:5000

## Open on a phone without internet
Connect the phone and computer to the same Wi-Fi network. In PowerShell, start KORA with:
`$env:KORA_HOST="0.0.0.0"; python main.py`
Then open `http://<computer-wi-fi-IP>:5000` on the phone (for example, `http://192.168.1.10:5000`).
Keep the computer and KORA running. This works over the local Wi-Fi without internet; it is not an offline copy that runs with the computer off.

## Public online demo (Render)
The `render.yaml` file configures a public, demo-only Render service. Create a private GitHub repository and push this project to it; `.gitignore` excludes local databases, secrets, environments, and uploads. Then in Render choose **New → Blueprint**, connect that repository, and deploy. Render will show the public `https://...onrender.com` URL when deployment finishes; open that URL on your phone. The computer can then be off, but the phone needs internet.

This deployment disables account signup, password login/reset, staff access, and demo reset. It hides on-screen OTPs and uses fictional demo data only. Do not use it for real accounts or marketplace data. The free service may sleep when idle and its local demo data may reset after a restart.

## Demo (no typing needed)
Welcome -> Explore Demo -> Seller Demo / Buyer Demo (one tap). KORA Team demo: private page http://127.0.0.1:5000/staff-login
Demo uses a SEPARATE database file (data/kora_demo.db). "Reset Demo Data" (Profile) rebuilds it. Real users live in data/kora.db.
Demo credentials: seller@kora.demo / Demo123!   buyer.demo@kora.pk / KoraDemo123   helper.demo@kora.pk / KoraHelper123

## OTP
No SMS/email service needed: the 6-digit OTP is shown on screen under the boxes as "(Demo OTP: ......)".
Set environment variable KORA_SHOW_OTP=0 to hide it (then you must plug in a real SMS/email sender in routes.py -> otp_start).

## Translation
Built-in phrasebook works offline (demo conversations + quick-reply chips). For free-typed text set env var GOOGLE_TRANSLATE_KEY (Google Cloud Translation key); without it the original message is shown with "Translation unavailable".

## Staff
Real staff are created by an admin only:  python create_staff.py staff@example.com "StrongPass1" "Name" KORA-H-002

## Files
main.py (start) · routes.py (all pages) · database.py (schema) · seed_data.py (200 products + demo accounts) · translation.py · i18n.py (Urdu/English) · templates/ · static/
## Limits
Product images are emoji tiles unless a seller uploads a photo. Payment accounts store only the last 4 digits. Email/phone change, push notifications, voice messages and real shipment tracking APIs are not included.
