"""KORA marketplace. Run:  python main.py   (a browser tab opens automatically)"""
import os,secrets,threading,webbrowser,sys
from flask import Flask
from database import init_real,init_demo,close_db,BASE
from routes import bp
def make_app():
    app=Flask(__name__)
    kf=os.path.join(BASE,"data",".secret_key")
    if not os.path.exists(kf):open(kf,"w").write(secrets.token_hex(32))
    app.secret_key=os.getenv("KORA_SECRET") or open(kf).read()
    app.config.update(MAX_CONTENT_LENGTH=6*1024*1024,SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE="Lax",PERMANENT_SESSION_LIFETIME=60*60*24*365)
    app.config["SHOW_OTP_ON_SCREEN"]=os.getenv("KORA_SHOW_OTP","1")=="1"   # no SMS needed: OTP is printed under the boxes
    app.config["KORA_DEMO_ONLY"]=os.getenv("KORA_DEMO_ONLY","0")=="1"
    app.teardown_appcontext(close_db);app.register_blueprint(bp)
    init_real()
    if not os.path.exists(os.path.join(BASE,"data","kora_demo.db")):init_demo(reset=True)
    return app
app=make_app()
if __name__=="__main__":
    port=int(os.getenv("PORT","5000"))
    host=os.getenv("KORA_HOST","127.0.0.1")
    threading.Timer(1.2,lambda:webbrowser.open(f"http://127.0.0.1:{port}")).start()
    app.run(host=host,port=port,debug=False)
