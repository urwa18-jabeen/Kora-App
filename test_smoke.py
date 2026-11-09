"""Quick self-test:  python test_smoke.py"""
import re,os
os.environ["KORA_SHOW_OTP"]="1"
from main import app
def tok(c):
    with c.session_transaction() as s:
        import secrets;s.setdefault("csrf",secrets.token_hex(8));return s["csrf"]
def post(c,url,**d):
    d["_csrf"]=tok(c);return c.post(url,data=d,follow_redirects=True)
def ok(name,cond):print(("PASS " if cond else "FAIL ")+name);assert cond
c=app.test_client()
r=c.get("/");ok("welcome",b"Select Your Language" in r.data)
c.get("/lang/en");ok("welcome after lang",b"Create Account" in c.get("/").data)
# signup -> OTP on screen -> verify
r=post(c,"/signup",name="Test Seller",contact="03001234567",password="Passw0rd1",confirm="Passw0rd1",role="seller")
otp=re.search(r"Demo OTP: (\d{6})",r.get_data(as_text=True));ok("otp shown on screen",bool(otp))
r=post(c,"/verify",code="000000" if otp.group(1)!="000000" else "111111");ok("wrong otp rejected",b"Wrong code" in r.data)
r=post(c,"/verify",code=otp.group(1));ok("signup -> seller home",b"Seller" in r.data and b"Earnings" in r.data)
ok("real seller has empty catalogue",b"Nothing found" in r.data)
r=post(c,"/catalogue/save",name="Test Wallet",category="Leather and Leather Goods",descr="x",price="500",moq="10",stock="100",location="Sialkot");ok("add product",b"Test Wallet" in r.data)
c.get("/logout")
# login role from backend
r=post(c,"/login",contact="03001234567",password="Passw0rd1");ok("login seller",b"Earnings" in r.data)
c.get("/logout");r=post(c,"/login",contact="03001234567",password="bad");ok("bad login",b"Invalid" in r.data)
# forgot password no enumeration
r=post(c,"/forgot",contact="03001234567");otp=re.search(r"Demo OTP: (\d{6})",r.get_data(as_text=True));ok("reset otp",bool(otp))
r=post(c,"/verify",code=otp.group(1));ok("reset page",b"New Password" in r.data)
r=post(c,"/reset",password="NewPass99",confirm="NewPass99");r=post(c,"/login",contact="03001234567",password="NewPass99");ok("login new pw",b"Earnings" in r.data)
r=post(c,"/forgot",contact="03999999999");ok("unknown account same flow",b"Demo OTP" in r.data)
c.get("/logout")
# staff cannot self-register
r=post(c,"/signup",name="Evil",contact="evil@x.com",password="Passw0rd1",confirm="Passw0rd1",role="staff");ok("staff signup blocked",b"Verification Code" not in r.data)
# demo seller (urdu)
d=app.test_client();post(d,"/demo/login/seller")
r=d.get("/home");t=r.get_data(as_text=True);ok("demo seller urdu + banner",'dir="rtl"' in t and "ڈیمو موڈ" in t and "210,000" in t and "+8.2%" in t)
r=d.get("/home?q=Surgical+Scissors");ok("search",b"Surgical Scissors" in r.data)
r=d.get("/orders");ok("orders",b"KR-1001" in r.data)
r=d.get("/order/1");ok("timeline",r.get_data(as_text=True).count("class=\"tl done")>=2 and "simulated" in r.get_data(as_text=True).lower())
r=d.get("/chat",follow_redirects=True);ok("kora chat",b"Bilal" in r.data)
r=d.get("/chat/1");t=r.get_data(as_text=True);ok("buyer msg translated to urdu",("tr-toggle" in t))
r=post(d,"/chat/2/send",body="Packing is done.");r=d.get("/chat/2");ok("send+translate",b"Packing is done" in r.data or "پیکنگ" in r.get_data(as_text=True))
# buyer + staff
b=app.test_client();post(b,"/demo/login/buyer");r=b.get("/home");ok("buyer home",b"Recommended" in r.data)
r=b.get("/home?q=football&maxp=5000");ok("buyer search filter",b"Football" in r.data)
r=b.get("/chat/1");ok("buyer sees english translation",b"Can you dispatch" in r.data or b"Yes, it will be ready" in r.data)
r=post(b,"/product/1/order",qty="999999");ok("qty validation",b"between MOQ" in r.data)
n=app.test_client();r=post(n,"/demo/login/helper");r=n.get("/home");ok("staff queue",b"KR-1001" in r.data)
r=post(n,"/order/1/staff",action="approve",note="ok");ok("staff approve","محفوظ" in r.get_data(as_text=True) and "منظور" in r.get_data(as_text=True))
ok("buyer blocked from staff action",post(b,"/order/1/staff",action="approve").status_code==403)
ok("seller blocked from staff action",post(d,"/order/1/staff",action="approve").status_code==403)
ok("csrf enforced",app.test_client().post("/login",data={"contact":"x","password":"y"}).status_code==400)
r=post(d,"/demo/reset");ok("reset demo",b"restored" in r.data.lower() or "ڈیمو ڈیٹا بحال" in r.get_data(as_text=True))
cnt=__import__("sqlite3").connect("data/kora_demo.db").execute("select count(*) from products").fetchone()[0];ok("200 products",cnt==200)
print("ALL OK")
