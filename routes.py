import os,re,secrets,time,hmac,random
from functools import wraps
from datetime import datetime
from flask import Blueprint,render_template,request,redirect,url_for,session,flash,g,abort,Response,current_app
from werkzeug.security import generate_password_hash,check_password_hash
from database import db,init_demo,connect,DEMO,REAL,BASE
from i18n import t,stage_name,status_name,STAGES,STATUS
from translation import detect,translate_for,PH
from seed_data import CATS
bp=Blueprint("kora",__name__)
UPLOADS=os.path.join(BASE,"static","uploads");FAILS={}
DEMO_KEYS={"seller":"seller@kora.demo","buyer":"buyer.demo@kora.pk","helper":"helper.demo@kora.pk"}
PROVIDERS=["Bank Account","Meezan Bank","HBL","UBL","Allied Bank","Other Pakistani Bank","JazzCash","Easypaisa"]
now=lambda:datetime.now().strftime("%Y-%m-%d %H:%M")
def norm(c):
    c=(c or "").strip()
    if "@" in c:
        e=c.lower();return("email",e) if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",e) else None
    d=re.sub(r"[\s-]","",c)
    if re.fullmatch(r"03\d{9}",d):d="+92"+d[1:]
    elif re.fullmatch(r"92\d{10}",d):d="+"+d
    return("phone",d) if re.fullmatch(r"\+\d{8,15}",d) else None
pw_ok=lambda p:len(p)>=8 and re.search(r"[A-Za-z]",p) and re.search(r"\d",p)
def me():
    if "u" not in g:
        g.u=None
        if session.get("uid"):g.u=db().execute("SELECT * FROM users WHERE id=?",(session["uid"],)).fetchone()
    return g.u
def need(*roles):
    def d(f):
        @wraps(f)
        def w(*a,**k):
            u=me()
            if not u:return redirect(url_for("kora.index"))
            if roles and u["role"] not in roles:abort(403)
            return f(*a,**k)
        return w
    return d
@bp.before_request
def pre():
    if current_app.config.get("KORA_DEMO_ONLY"):
        if request.endpoint in ("kora.signup","kora.login","kora.staff_login","kora.forgot","kora.reset"):
            return redirect(url_for("kora.demo_page"))
        if request.endpoint=="kora.demo_reset":abort(404)
        if request.endpoint=="kora.demo_login" and request.view_args.get("key")=="helper":abort(404)
    g.lang=session.get("lang","en")
    if request.method=="POST":
        tok=request.form.get("_csrf") or request.headers.get("X-CSRF")
        if not tok or tok!=session.get("csrf"):abort(400)
@bp.app_context_processor
def ctx():
    def csrf():
        session.setdefault("csrf",secrets.token_hex(16));return session["csrf"]
    u=me();unread=notes=0
    if u:
        c=db();unread=c.execute("SELECT COUNT(*) FROM messages m JOIN conversations v ON v.id=m.conv_id WHERE (v.u1=? OR v.u2=?) AND m.sender_id!=? AND m.read=0",(u["id"],u["id"],u["id"])).fetchone()[0]
        notes=c.execute("SELECT COUNT(*) FROM notifications WHERE user_id=? AND read=0",(u["id"],)).fetchone()[0]
    return dict(t=t,me=u,lang=g.lang,demo=session.get("demo"),csrf=csrf,unread=unread,notes=notes,CATS=CATS,STAGES=STAGES,stage_name=stage_name,status_name=status_name,stat_idx=stat_idx,PROVIDERS=PROVIDERS)
@bp.app_template_filter("rs")
def rs(n):return "Rs. {:,}".format(int(n or 0))
def stat_idx(o):
    if o["flagged"] and not o["cancelled"]:return 7
    if o["cancelled"]:return 6
    s=o["stage"];return 0 if s==0 else 1 if s<=3 else 2 if s==4 else 3 if s<=7 else 4 if s==8 else 5
def notify(uid,key,**k):
    c=db();l=c.execute("SELECT lang FROM users WHERE id=?",(uid,)).fetchone()
    c.execute("INSERT INTO notifications(user_id,text,created) VALUES(?,?,?)",(uid,t(key,l["lang"] if l else "en").format(**k),now()))
def audit(action,detail):db().execute("INSERT INTO audit_log(actor_id,action,detail,created) VALUES(?,?,?,?)",(me()["id"],action,detail,now()))
def svg(e,h):
    return Response(f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120'><rect width='120' height='120' fill='hsl({h},55%,85%)'/><text x='60' y='78' font-size='54' text-anchor='middle'>{e}</text></svg>",mimetype="image/svg+xml")
@bp.route("/pimg/<int:pid>")
def pimg(pid):
    p=db().execute("SELECT image,emoji,hue FROM products WHERE id=?",(pid,)).fetchone()
    if p and p["image"]:return redirect(url_for("static",filename="uploads/"+p["image"]))
    return svg(p["emoji"] if p else "📦",p["hue"] if p else 200)
@bp.route("/ph")
def ph():return svg(request.args.get("e","🏭")[:2],int(request.args.get("h","180")) if request.args.get("h","180").isdigit() else 180)
def save_upload(f):
    if not f or not f.filename:return None
    ext=f.filename.rsplit(".",1)[-1].lower()
    f.seek(0,2);n=f.tell();f.seek(0)
    if ext not in("jpg","jpeg","png","webp") or n>5*1024*1024:flash(t("bad_file"));return None
    name=secrets.token_hex(8)+"."+ext;f.save(os.path.join(UPLOADS,name));return name

# ---------- onboarding / auth ----------
@bp.route("/")
def index():
    if me():return redirect(url_for("kora.home"))
    return render_template("welcome.html")
@bp.route("/lang/<l>")
def setlang(l):
    if l in("ur","en"):
        session["lang"]=l;session.permanent=True
        if me():db().execute("UPDATE users SET lang=? WHERE id=?",(l,me()["id"]));db().commit()
    return redirect(request.referrer or url_for("kora.index"))
def otp_start(pend):
    pend.update(otp="%06d"%secrets.randbelow(10**6),exp=time.time()+600,tries=0,last=time.time());session["pend"]=pend
@bp.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        f=request.form;n=norm(f.get("contact"));name=f.get("name","").strip();role=f.get("role")
        err=None
        if len(name)<2 or len(name)>80:err="bad_name"
        elif not n:err="bad_contact"
        elif role not in("seller","buyer"):err="bad_contact"   # staff can never self-register
        elif not pw_ok(f.get("password","")):err="bad_pw"
        elif f.get("password")!=f.get("confirm"):err="pw_mismatch"
        else:
            col="email" if n[0]=="email" else "phone"
            if connect(REAL).execute(f"SELECT 1 FROM users WHERE {col}=?",(n[1],)).fetchone() or n[1] in DEMO_KEYS.values():err="exists"
        if err:flash(t(err));return render_template("signup.html",f=f)
        session.pop("demo",None);otp_start(dict(kind="signup",name=name,type=n[0],contact=n[1],pw=generate_password_hash(f["password"]),role=role,lang=g.lang))
        return redirect(url_for("kora.verify"))
    return render_template("signup.html",f={})
@bp.route("/verify",methods=["GET","POST"])
def verify():
    p=session.get("pend")
    if not p:return redirect(url_for("kora.index"))
    if request.method=="POST":
        if time.time()>p["exp"] or p["tries"]>=5:session.pop("pend");flash(t("otp_exp"));return redirect(url_for("kora.index"))
        if not hmac.compare_digest(request.form.get("code","").strip(),p["otp"]):
            p["tries"]+=1;session["pend"]=p;flash(t("bad_otp"));return redirect(url_for("kora.verify"))
        if p["kind"]=="reset":
            session["reset_uid"]=p["uid"];session["reset_exp"]=time.time()+600;session.pop("pend");return redirect(url_for("kora.reset"))
        c=connect(REAL);col="email" if p["type"]=="email" else "phone"
        if c.execute(f"SELECT 1 FROM users WHERE {col}=?",(p["contact"],)).fetchone():session.pop("pend");flash(t("exists"));return redirect(url_for("kora.login"))
        uid=c.execute(f"INSERT INTO users(name,{col},pw_hash,role,lang) VALUES(?,?,?,?,?)",(p["name"],p["contact"],p["pw"],p["role"],p["lang"])).lastrowid
        if p["role"]=="seller":c.execute("INSERT INTO seller_profiles(user_id,biz) VALUES(?,?)",(uid,p["name"]+"'s Business"))
        c.commit();c.close();session.pop("pend");session.update(uid=uid,lang=p["lang"])
        return redirect(url_for("kora.home"))
    return render_template("verify.html",p=p,show=current_app.config["SHOW_OTP_ON_SCREEN"])
@bp.route("/resend",methods=["POST"])
def resend():
    p=session.get("pend")
    if not p:return redirect(url_for("kora.index"))
    if time.time()-p["last"]<60:flash(t("cooldown"))
    else:otp_start(p);flash(t("otp_sent"))
    return redirect(url_for("kora.verify"))
def try_login(path,contact,pw,staff):
    n=norm(contact);k=n[1] if n else contact
    f=FAILS.get(k,(0,0))
    if f[0]>=5 and time.time()-f[1]<300:return "locked"
    if not n:return None
    r=connect(path).execute("SELECT * FROM users WHERE "+("email" if n[0]=="email" else "phone")+"=?",(n[1],)).fetchone()
    if r and check_password_hash(r["pw_hash"],pw) and (r["role"]=="staff")==staff:FAILS.pop(k,None);return r
    FAILS[k]=(f[0]+1,time.time());return None
def enter(r,demo):
    session.clear();session.permanent=True
    if demo:session["demo"]=True
    session.update(uid=r["id"],lang=r["lang"])
@bp.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        c,pw=request.form.get("contact",""),request.form.get("password","")
        for path,demo in((REAL,False),(DEMO,True)):
            r=try_login(path,c,pw,False)
            if r=="locked":flash(t("locked"));return render_template("login.html")
            if r:enter(r,demo);return redirect(url_for("kora.home"))
        flash(t("bad_login"))
    return render_template("login.html")
@bp.route("/staff-login",methods=["GET","POST"])
def staff_login():   # private route: not linked from public screens
    if request.method=="POST":
        c,pw=request.form.get("contact",""),request.form.get("password","")
        for path,demo in((REAL,False),(DEMO,True)):
            r=try_login(path,c,pw,True)
            if r=="locked":flash(t("locked"));break
            if r:enter(r,demo);return redirect(url_for("kora.home"))
        else:flash(t("bad_login"))
    return render_template("staff_login.html")
@bp.route("/forgot",methods=["GET","POST"])
def forgot():
    if request.method=="POST":
        n=norm(request.form.get("contact"))
        if not n:flash(t("bad_contact"));return render_template("forgot.html")
        r=connect(REAL).execute("SELECT * FROM users WHERE "+("email" if n[0]=="email" else "phone")+"=? AND role!='staff'",(n[1],)).fetchone()
        otp_start(dict(kind="reset",uid=r["id"] if r else -1,contact=n[1]))  # identical flow either way = no account enumeration
        flash(t("reset_sent"));return redirect(url_for("kora.verify"))
    return render_template("forgot.html")
@bp.route("/reset",methods=["GET","POST"])
def reset():
    if not session.get("reset_uid") or time.time()>session.get("reset_exp",0) or session["reset_uid"]<0:return redirect(url_for("kora.forgot"))
    if request.method=="POST":
        f=request.form
        if not pw_ok(f.get("password","")):flash(t("bad_pw"))
        elif f["password"]!=f.get("confirm"):flash(t("pw_mismatch"))
        else:
            c=connect(REAL);c.execute("UPDATE users SET pw_hash=? WHERE id=?",(generate_password_hash(f["password"]),session["reset_uid"]));c.commit()
            session.pop("reset_uid");flash(t("saved"));return redirect(url_for("kora.login"))
    return render_template("reset.html")
@bp.route("/logout")
def logout():
    lang=session.get("lang");session.clear()
    if lang:session["lang"]=lang
    return redirect(url_for("kora.index"))

# ---------- demo mode ----------
@bp.route("/demo")
def demo_page():return render_template("demo.html")
@bp.route("/demo/login/<key>",methods=["POST"])
def demo_login(key):
    if key not in DEMO_KEYS:abort(404)
    r=connect(DEMO).execute("SELECT * FROM users WHERE email=?",(DEMO_KEYS[key],)).fetchone();enter(r,True);return redirect(url_for("kora.home"))
@bp.route("/demo/reset",methods=["POST"])
@need()
def demo_reset():
    if not session.get("demo"):abort(403)
    uid,lang=session["uid"],session["lang"]
    from database import close_db;close_db();init_demo(reset=True);flash(t("demo_reset_done"));return redirect(url_for("kora.profile"))

# ---------- shared helpers ----------
def find(q,cat,maxp,limit=40):
    sql="SELECT * FROM products WHERE 1=1";a=[]
    if q:sql+=" AND (name LIKE ? OR category LIKE ? OR seller_name LIKE ? OR location LIKE ? OR descr LIKE ?)";a+=[f"%{q}%"]*5
    if cat:sql+=" AND category=?";a.append(cat)
    if maxp.isdigit():sql+=" AND price<=?";a.append(int(maxp))
    return db().execute(sql+" ORDER BY rating DESC,id LIMIT ?",a+[limit]).fetchall()
def threads(uid,other_role=None):
    c=db();out=[]
    for v in c.execute("SELECT * FROM conversations WHERE u1=? OR u2=?",(uid,uid)).fetchall():
        o=c.execute("SELECT id,name,role,photo,title FROM users WHERE id=?",(v["u2"] if v["u1"]==uid else v["u1"],)).fetchone()
        if other_role and o["role"]!=other_role:continue
        lm=c.execute("SELECT * FROM messages WHERE conv_id=? ORDER BY id DESC LIMIT 1",(v["id"],)).fetchone()
        un=c.execute("SELECT COUNT(*) FROM messages WHERE conv_id=? AND sender_id!=? AND read=0",(v["id"],uid)).fetchone()[0]
        prev=None
        if lm:
            prev=lm["body"]
            if lm["lang"]!=g.lang:
                tr=c.execute("SELECT text FROM translations WHERE message_id=? AND lang=? AND status='ok'",(lm["id"],g.lang)).fetchone()
                if tr:prev=tr["text"]
        out.append(dict(id=v["id"],other=o,prev=prev,time=lm["created"][11:16] if lm else "",unread=un))
    return out
def conv_between(a,b):
    c=db();r=c.execute("SELECT id FROM conversations WHERE (u1=? AND u2=?) OR (u1=? AND u2=?)",(a,b,b,a)).fetchone()
    if r:return r["id"]
    cid=c.execute("INSERT INTO conversations(u1,u2) VALUES(?,?)",(a,b)).lastrowid;c.commit();return cid
def orders_for(u,sidx=None):
    sql="SELECT o.*,p.name pname,b.name bname FROM orders o JOIN products p ON p.id=o.product_id JOIN users b ON b.id=o.buyer_id"
    a=[]
    if u["role"]=="seller":sql+=" WHERE o.seller_id=?";a=[u["id"]]
    elif u["role"]=="buyer":sql+=" WHERE o.buyer_id=?";a=[u["id"]]
    rows=db().execute(sql+" ORDER BY o.id DESC",a).fetchall()
    return [o for o in rows if sidx is None or stat_idx(o)==sidx]

# ---------- homes ----------
@bp.route("/home")
@need()
def home():
    u=me();q=request.args.get("q","").strip();cat=request.args.get("cat","");mp=request.args.get("maxp","").strip()
    filt=bool(q or cat or mp);prods=find(q,cat,mp,40 if filt else 12)
    if u["role"]=="staff":
        return render_template("staff_home.html",orders=orders_for(u),log=db().execute("SELECT a.*,u.name FROM audit_log a JOIN users u ON u.id=a.actor_id ORDER BY a.id DESC LIMIT 10").fetchall())
    if u["role"]=="seller":
        c=db();p=c.execute("SELECT * FROM seller_profiles WHERE user_id=?",(u["id"],)).fetchone()
        a,b=p["earn_this"],p["earn_prev"]
        if a is None:
            q1="SELECT COALESCE(SUM(o.amount),0) FROM orders o JOIN order_events e ON e.order_id=o.id AND e.stage=9 WHERE o.seller_id=? AND strftime('%Y-%m',e.ts)=strftime('%Y-%m','now'{})"
            a=c.execute(q1.format(""),(u["id"],)).fetchone()[0];b=c.execute(q1.format(",'-1 month'"),(u["id"],)).fetchone()[0]
        pct=round((a-b)/b*100,1) if b else None
        found=[]
        if q:found=[o for o in orders_for(u) if q.lower() in (o["code"]+o["pname"]).lower()]
        return render_template("seller_home.html",p=p,a=a,pct=pct,prods=prods,filt=filt,q=q,cat=cat,mp=mp,found=found,th=threads(u["id"],"buyer"))
    return render_template("buyer_home.html",prods=prods,filt=filt,q=q,cat=cat,mp=mp,th=threads(u["id"],"seller"),wish=[r[0] for r in db().execute("SELECT product_id FROM wishlist WHERE user_id=?",(u["id"],))])

# ---------- orders ----------
@bp.route("/orders")
@need()
def orders():
    s=request.args.get("s");s=int(s) if s and s.isdigit() else None
    return render_template("orders.html",orders=orders_for(me(),s),s=s)
@bp.route("/order/<int:oid>")
@need()
def order(oid):
    u=me();c=db();o=c.execute("SELECT o.*,p.name pname,b.name bname,s.name sname FROM orders o JOIN products p ON p.id=o.product_id JOIN users b ON b.id=o.buyer_id JOIN users s ON s.id=o.seller_id WHERE o.id=?",(oid,)).fetchone()
    if not o or (u["role"]=="seller" and o["seller_id"]!=u["id"]) or (u["role"]=="buyer" and o["buyer_id"]!=u["id"]):abort(404)
    ev={e["stage"]:e for e in c.execute("SELECT * FROM order_events WHERE order_id=?",(oid,))}
    return render_template("order.html",o=o,ev=ev,cur=ev.get(o["stage"]))
@bp.route("/order/<int:oid>/staff",methods=["POST"])
@need("staff")
def order_staff(oid):
    c=db();o=c.execute("SELECT * FROM orders WHERE id=?",(oid,)).fetchone()
    if not o:abort(404)
    a=request.form.get("action");note=request.form.get("note","")[:300];u=me()
    if a=="assign":c.execute("UPDATE orders SET staff_id=? WHERE id=?",(u["id"],oid))
    elif a=="approve" and 1<=o["stage"]<=2 and not o["cancelled"]:
        c.execute("UPDATE orders SET stage=3,flagged=0 WHERE id=?",(oid,));c.execute("INSERT INTO order_events(order_id,stage,ts,location,note) VALUES(?,?,?,?,?)",(oid,3,now(),"KORA Sialkot Office",note))
        c.execute("INSERT INTO verification_records(order_id,staff_id,result,notes,created) VALUES(?,?,?,?,?)",(oid,u["id"],"passed",note,now()))
    elif a=="flag":
        c.execute("UPDATE orders SET flagged=1 WHERE id=?",(oid,));c.execute("INSERT INTO verification_records(order_id,staff_id,result,notes,created) VALUES(?,?,?,?,?)",(oid,u["id"],"flagged",note,now()))
    elif a=="cancel":c.execute("UPDATE orders SET cancelled=1 WHERE id=?",(oid,))
    elif a=="stage":
        s=request.form.get("stage","");
        if s.isdigit() and 0<=int(s)<=9:
            s=int(s);c.execute("UPDATE orders SET stage=? WHERE id=?",(s,oid))
            c.execute("INSERT INTO order_events(order_id,stage,ts,location,note) VALUES(?,?,?,?,?)",(oid,s,now(),request.form.get("location","")[:80],note))
    else:abort(400)
    audit(a,f"order {o['code']} {note}")
    for uid in(o["buyer_id"],o["seller_id"]):notify(uid,"n_order",code=o["code"])
    c.commit();flash(t("saved"));return redirect(url_for("kora.order",oid=oid))
@bp.route("/product/<int:pid>")
@need()
def product(pid):
    c=db();p=c.execute("SELECT * FROM products WHERE id=?",(pid,)).fetchone()
    if not p:abort(404)
    u=me();w=c.execute("SELECT 1 FROM wishlist WHERE user_id=? AND product_id=?",(u["id"],pid)).fetchone()
    return render_template("product.html",p=p,w=w,addrs=c.execute("SELECT * FROM addresses WHERE user_id=?",(u["id"],)).fetchall())
@bp.route("/product/<int:pid>/order",methods=["POST"])
@need("buyer")
def place_order(pid):
    c=db();p=c.execute("SELECT * FROM products WHERE id=?",(pid,)).fetchone();q=request.form.get("qty","")
    if not p or not q.isdigit() or not(p["moq"]<=int(q)<=p["stock"]):flash(t("bad_qty"));return redirect(url_for("kora.product",pid=pid))
    q=int(q);code="KR-%d"%(1001+c.execute("SELECT COUNT(*) FROM orders").fetchone()[0]);seller=p["seller_id"] or (c.execute("SELECT id FROM users WHERE role='seller' LIMIT 1").fetchone() or [None])[0]
    if not seller:flash(t("bad_qty"));return redirect(url_for("kora.product",pid=pid))
    staff=c.execute("SELECT id FROM users WHERE role='staff' ORDER BY id LIMIT 1").fetchone()
    oid=c.execute("INSERT INTO orders(code,product_id,buyer_id,seller_id,qty,amount,stage,staff_id,created) VALUES(?,?,?,?,?,?,0,?,?)",(code,pid,me()["id"],seller,q,q*p["price"],staff["id"] if staff else None,now())).lastrowid
    c.execute("INSERT INTO order_events(order_id,stage,ts,location,note) VALUES(?,?,?,?,?)",(oid,0,now(),p["location"],"Order placed"))
    notify(seller,"n_order",code=code)
    if staff:notify(staff["id"],"n_order",code=code)
    c.commit();flash(t("order_placed_msg"));return redirect(url_for("kora.order",oid=oid))
@bp.route("/wish/<int:pid>",methods=["POST"])
@need("buyer")
def wish(pid):
    c=db();u=me()["id"]
    if c.execute("SELECT 1 FROM wishlist WHERE user_id=? AND product_id=?",(u,pid)).fetchone():c.execute("DELETE FROM wishlist WHERE user_id=? AND product_id=?",(u,pid))
    else:c.execute("INSERT INTO wishlist VALUES(?,?)",(u,pid))
    c.commit();return redirect(request.referrer or url_for("kora.home"))
@bp.route("/wishlist")
@need("buyer")
def wishlist():
    return render_template("wishlist.html",prods=db().execute("SELECT p.* FROM products p JOIN wishlist w ON w.product_id=p.id WHERE w.user_id=?",(me()["id"],)).fetchall())
@bp.route("/seller/<int:sid>")
@need()
def seller_public(sid):
    c=db();s=c.execute("SELECT u.*,p.* FROM users u JOIN seller_profiles p ON p.user_id=u.id WHERE u.id=?",(sid,)).fetchone()
    if not s:abort(404)
    return render_template("seller_public.html",s=s,prods=c.execute("SELECT * FROM products WHERE seller_id=? LIMIT 24",(sid,)).fetchall(),revs=c.execute("SELECT * FROM reviews WHERE seller_id=?",(sid,)).fetchall())

# ---------- seller catalogue ----------
@bp.route("/catalogue")
@need("seller")
def catalogue():
    c=db();e=request.args.get("edit","");p=c.execute("SELECT * FROM products WHERE id=? AND seller_id=?",(e,me()["id"])).fetchone() if e.isdigit() else None
    return render_template("catalogue.html",prods=c.execute("SELECT * FROM products WHERE seller_id=? ORDER BY id DESC",(me()["id"],)).fetchall(),e=p)
@bp.route("/catalogue/save",methods=["POST"])
@need("seller")
def catalogue_save():
    f=request.form;u=me();c=db()
    try:price,moq,stock=int(f["price"]),int(f["moq"]),int(f["stock"]);assert price>0 and moq>0 and stock>=0 and len(f["name"].strip())>1 and f["category"] in[x[0] for x in CATS]
    except Exception:flash(t("bad_qty"));return redirect(url_for("kora.catalogue"))
    img=save_upload(request.files.get("photo"));biz=c.execute("SELECT biz FROM seller_profiles WHERE user_id=?",(u["id"],)).fetchone()["biz"]
    cat=next(x for x in CATS if x[0]==f["category"]);vals=(f["name"].strip()[:120],f["category"],f.get("descr","")[:1000],price,moq,stock,f.get("location","")[:100],f.get("specs","")[:500],1 if f.get("custom") else 0)
    pid=f.get("id","")
    if pid.isdigit() and c.execute("SELECT 1 FROM products WHERE id=? AND seller_id=?",(pid,u["id"])).fetchone():
        c.execute("UPDATE products SET name=?,category=?,descr=?,price=?,moq=?,stock=?,location=?,specs=?,custom=? WHERE id=?",vals+(pid,))
        if img:c.execute("UPDATE products SET image=? WHERE id=?",(img,pid))
    else:c.execute("INSERT INTO products(seller_id,seller_name,name,category,descr,price,moq,stock,location,specs,custom,image,emoji,hue,rating) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)",(u["id"],biz)+vals+(img,cat[1],random.randint(0,359)))
    c.commit();flash(t("saved"));return redirect(url_for("kora.catalogue"))
@bp.route("/catalogue/delete/<int:pid>",methods=["POST"])
@need("seller")
def catalogue_delete(pid):
    db().execute("DELETE FROM products WHERE id=? AND seller_id=?",(pid,me()["id"]));db().commit();return redirect(url_for("kora.catalogue"))

# ---------- chat (with automatic translation) ----------
@bp.route("/chat")
@need()
def chat():
    u=me()
    if u["role"]=="staff":return render_template("chats.html",th=threads(u["id"]))
    s=db().execute("SELECT id FROM users WHERE role='staff' ORDER BY id LIMIT 1").fetchone()
    if not s:flash(t("no_staff"));return redirect(url_for("kora.home"))
    return redirect(url_for("kora.thread",cid=conv_between(u["id"],s["id"])))
def get_conv(cid):
    v=db().execute("SELECT * FROM conversations WHERE id=?",(cid,)).fetchone();u=me()
    if not v or u["id"] not in(v["u1"],v["u2"]):abort(404)
    return v
@bp.route("/chat/<int:cid>")
@need()
def thread(cid):
    c=db();u=me();v=get_conv(cid);o=c.execute("SELECT id,name,role,photo,title FROM users WHERE id=?",(v["u2"] if v["u1"]==u["id"] else v["u1"],)).fetchone()
    rows=c.execute("SELECT * FROM messages WHERE conv_id=? ORDER BY id",(cid,)).fetchall();msgs=[]
    for m in rows:
        mine=m["sender_id"]==u["id"];tr=None;un=False
        if not mine and m["lang"]!=g.lang:
            r=c.execute("SELECT text,status FROM translations WHERE message_id=? AND lang=?",(m["id"],g.lang)).fetchone()
            if r and r["status"]=="ok":tr=r["text"]
            else:un=True
        msgs.append(dict(body=m["body"],shown=tr or m["body"],tr=tr,unavail=un,lang=m["lang"],mine=mine,time=m["created"][11:16],read=m["read"],attach=m["attach"]))
    c.execute("UPDATE messages SET read=1 WHERE conv_id=? AND sender_id!=?",(cid,u["id"]));c.commit()
    return render_template("thread.html",cid=cid,o=o,msgs=msgs,chips=[p[1 if g.lang=="ur" else 0] for p in PH[:5]])
@bp.route("/chat/<int:cid>/send",methods=["POST"])
@need()
def send(cid):
    c=db();u=me();v=get_conv(cid);body=request.form.get("body","").strip()[:4000];att=save_upload(request.files.get("file"))
    if not body and not att:return redirect(url_for("kora.thread",cid=cid))
    lang=detect(body) if body else g.lang;oid=v["u2"] if v["u1"]==u["id"] else v["u1"]
    mid=c.execute("INSERT INTO messages(conv_id,sender_id,body,lang,created,attach) VALUES(?,?,?,?,?,?)",(cid,u["id"],body,lang,now(),att)).lastrowid
    ol=c.execute("SELECT lang FROM users WHERE id=?",(oid,)).fetchone()["lang"]
    terms=[r[0] for r in c.execute("SELECT p.name FROM orders o JOIN products p ON p.id=o.product_id WHERE o.buyer_id IN(?,?) OR o.seller_id IN(?,?)",(u["id"],oid,u["id"],oid))]
    if body:
        tr,st=translate_for(body,lang,ol,terms)
        if st!="same":c.execute("INSERT INTO translations VALUES(?,?,?,?)",(mid,ol,tr,st))
    notify(oid,"n_msg",name=u["name"]);c.commit();return redirect(url_for("kora.thread",cid=cid))

# ---------- profile ----------
@bp.route("/profile")
@need()
def profile():
    u=me();c=db();x={}
    if u["role"]=="seller":
        x=dict(p=c.execute("SELECT * FROM seller_profiles WHERE user_id=?",(u["id"],)).fetchone(),accts=c.execute("SELECT * FROM payment_accounts WHERE user_id=?",(u["id"],)).fetchall(),revs=c.execute("SELECT * FROM reviews WHERE seller_id=?",(u["id"],)).fetchall())
    if u["role"]=="buyer":x=dict(addrs=c.execute("SELECT * FROM addresses WHERE user_id=?",(u["id"],)).fetchall())
    return render_template("profile.html",**x)
@bp.route("/profile/save",methods=["POST"])
@need()
def profile_save():
    u=me();c=db();f=request.form;name=f.get("name","").strip()[:80]
    if len(name)<2:flash(t("bad_name"));return redirect(url_for("kora.profile"))
    ph_=save_upload(request.files.get("photo"));c.execute("UPDATE users SET name=?"+(",photo=?" if ph_ else "")+" WHERE id=?",(name,)+((ph_,) if ph_ else ())+(u["id"],))
    if u["role"]=="seller":
        sp=save_upload(request.files.get("shop_photo"))
        c.execute("UPDATE seller_profiles SET biz=?,descr=?,category=?,city=?,road=?,area=?,landmark=?,postal=?"+(",shop_photo=?" if sp else "")+" WHERE user_id=?",tuple(f.get(k,"")[:300] for k in("biz","descr","category","city","road","area","landmark","postal"))+((sp,) if sp else ())+(u["id"],))
    c.commit();flash(t("saved"));return redirect(url_for("kora.profile"))
@bp.route("/payment/add",methods=["POST"])
@need("seller")
def pay_add():
    f=request.form;num=re.sub(r"\s","",f.get("number",""))
    if f.get("provider") in PROVIDERS and re.fullmatch(r"[A-Za-z0-9+-]{6,34}",num) and len(f.get("holder","").strip())>1:
        c=db();d=1 if f.get("default") else 0
        if d:c.execute("UPDATE payment_accounts SET is_default=0 WHERE user_id=?",(me()["id"],))
        c.execute("INSERT INTO payment_accounts(user_id,provider,holder,last4,nickname,is_default) VALUES(?,?,?,?,?,?)",(me()["id"],f["provider"],f["holder"].strip()[:80],num[-4:],f.get("nick","")[:40],d));c.commit();flash(t("saved"))
    else:flash(t("bad_contact"))
    return redirect(url_for("kora.profile"))
@bp.route("/payment/delete/<int:i>",methods=["POST"])
@need("seller")
def pay_del(i):
    db().execute("DELETE FROM payment_accounts WHERE id=? AND user_id=?",(i,me()["id"]));db().commit();return redirect(url_for("kora.profile"))
@bp.route("/address/add",methods=["POST"])
@need("buyer")
def addr_add():
    f=request.form
    if len(f.get("line","").strip())>3:
        db().execute("INSERT INTO addresses(user_id,label,line,city,country,postal) VALUES(?,?,?,?,?,?)",(me()["id"],)+tuple(f.get(k,"")[:120] for k in("label","line","city","country","postal")));db().commit();flash(t("saved"))
    return redirect(url_for("kora.profile"))
@bp.route("/address/delete/<int:i>",methods=["POST"])
@need("buyer")
def addr_del(i):
    db().execute("DELETE FROM addresses WHERE id=? AND user_id=?",(i,me()["id"]));db().commit();return redirect(url_for("kora.profile"))
@bp.route("/notifications",methods=["GET","POST"])
@need()
def notifications():
    c=db();u=me()["id"]
    if request.method=="POST":c.execute("UPDATE notifications SET read=1 WHERE user_id=?",(u,));c.commit();return redirect(url_for("kora.notifications"))
    return render_template("notifications.html",ns=c.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT 50",(u,)).fetchall())
@bp.route("/help")
def help_():return render_template("help.html")
