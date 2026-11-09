"""ALL FICTIONAL demo data. Edit freely, then use 'Reset Demo Data' in the app."""
from datetime import datetime,timedelta
from werkzeug.security import generate_password_hash as gh
from translation import PH,translate_for,detect
CATS=[("Leather and Leather Goods","🧥",["Leather Football","Leather Jacket","Leather Gloves","Leather Wallet","Leather Belt"],1500,"hand-stitched from full-grain Sialkot leather"),
("Surgical and Dental Instruments","🩺",["Surgical Scissors","Forceps","Needle Holder","Dental Mirror Set","Surgical Clamp"],900,"German-pattern stainless steel, autoclave safe"),
("Sports Goods","⚽",["Soccer Ball","Cricket Bat","Boxing Gloves","Training Cone Set","Sports Bag"],2200,"match-grade sports equipment for clubs and export"),
("Textile and Apparel","👕",["T-Shirt","Hoodie","Track Jacket","Tracksuit","Work Uniform"],1800,"cut and sewn from combed cotton blends"),
("Sportswear and Gloves","🧤",["Fitness Gloves","Working Gloves","Cycling Gloves","Protective Gloves","Goalkeeper Gloves"],700,"durable grip palms with reinforced stitching"),
("Packaging and Cartons","📦",["Corrugated Carton","Printed Box","Mailer Box","Gift Box","Custom Packaging"],120,"export-grade board, available with offset printing"),
("Footwear","👟",["Sports Shoes","Leather Shoes","Safety Shoes","Casual Sneakers","Sandals"],3500,"comfort soles with factory quality checks"),
("Kitchenware and Cutlery","🔪",["Steel Knife","Kitchen Scissors","Cutlery Set","Peeler Set","Kitchen Tongs"],600,"food-safe stainless steel with mirror polish"),
("Fitness and Exercise Equipment","🏋️",["Resistance Band","Gym Grip Gloves","Skipping Rope","Yoga Mat","Dumbbell Set"],1100,"gym-tested training gear in bulk quantities"),
("Textile Accessories and Promotional Products","🧢",["Cap","Embroidered Patch","Custom Badge","Promo T-Shirt","Lanyard"],250,"promotional merchandise with logo embroidery")]
VAR=[("Classic",1,"standard finish"),("Premium",1.6,"premium finish"),("Export Grade",2.2,"export-quality finish"),("Custom Logo",1.9,"custom logo branding")]
SELLERS=[("Ali Surgical Works","Sialkot"),("Sialkot Sports House","Sialkot"),("Punjab Leather Co.","Lahore"),("Faisal Textiles","Faisalabad"),("Karachi Pack Industries","Karachi"),("Gujranwala Steelworks","Gujranwala")]
def ago(d,h=0):return (datetime.now()-timedelta(days=d,hours=h)).strftime("%Y-%m-%d %H:%M")
def seed(c):
    ex=lambda q,a=():c.execute(q,a)
    def user(n,e,p,pw,role,lang,**k):
        return c.execute("INSERT INTO users(name,email,phone,pw_hash,role,lang,staff_id,title) VALUES(?,?,?,?,?,?,?,?)",(n,e,p,gh(pw),role,lang,k.get("sid"),k.get("title"))).lastrowid
    ahmed=user("Ahmed Khan","seller@kora.demo","+923000000001","Demo123!","seller","ur")
    sarah=user("Sarah Williams","buyer.demo@kora.pk","+447000000002","KoraDemo123","buyer","en")
    bilal=user("Bilal Ahmed","helper.demo@kora.pk","+923000000003","KoraHelper123","staff","ur",sid="KORA-H-001",title="Verification Officer - Sialkot")
    ex("INSERT INTO seller_profiles VALUES(?,?,?,?,?,?,?,?,?,NULL,4.8,124,210000,194100)",(ahmed,"Ali Surgical Works","Fictional manufacturer of surgical and dental instruments in Sialkot (demo business).","Surgical and Dental Instruments","Sialkot","Instrument Lane (demo)","Small Industrial Estate","Near Demo Chowk","51310"))
    for r in [("Meezan Bank","Ahmed Khan","4582","Meezan (FAKE)",1),("HBL","Ahmed Khan","9921","HBL (FAKE)",0),("JazzCash","Ahmed Khan","0000","JazzCash 0300-0000000 (FAKE)",0),("Easypaisa","Ahmed Khan","0001","Easypaisa (FAKE)",0)]:
        ex("INSERT INTO payment_accounts(user_id,provider,holder,last4,nickname,is_default) VALUES(?,?,?,?,?,?)",(ahmed,)+r)
    for a,r,x in[("Rana Medical Store",5,"Excellent quality and on-time packing."),("Fatima Ali",5,"Instruments exactly as specified."),("Zubair Traders",4,"Good finish, slightly late dispatch."),("John Smith",5,"Great communication through KORA.")]:
        ex("INSERT INTO reviews(seller_id,author,rating,text) VALUES(?,?,?,?)",(ahmed,a,r,x))
    n=0;first=[]
    for ci,(cat,emo,items,base,blurb) in enumerate(CATS):
        for bi,b in enumerate(items):
            for vi,v in enumerate(VAR):
                s=SELLERS[(ci+bi+vi)%6];sid=ahmed if s[0]=="Ali Surgical Works" else None
                price=int(round(base*v[1]*(1+bi*.25)/10)*10)
                cur=c.execute("INSERT INTO products(seller_id,seller_name,name,category,descr,price,moq,stock,rating,location,specs,custom,hue,emoji) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                 (sid,s[0],f"{v[0]} {b}",cat,f"{v[0]} {b.lower()}: {blurb}. Made with {v[2]} in {s[1]} (fictional demo listing).",price,[50,100,200,500][(bi+vi)%4],(n*37)%900+100,round(4+((n*7)%10)/10,1),f"{s[1]}, Pakistan",f"Grade: {v[0]}; Finish: {v[2]}; Origin: {s[1]}",1 if vi==3 else 0,(ci*36+bi*7+vi*3)%360,emo))
                if sid:first.append(cur.lastrowid)
                n+=1
    ex("INSERT INTO addresses(user_id,label,line,city,country,postal) VALUES(?,?,?,?,?,?)",(sarah,"Warehouse (demo)","12 Demo Street","London","United Kingdom","EC1A 1AA"))
    ex("INSERT INTO addresses(user_id,label,line,city,country,postal) VALUES(?,?,?,?,?,?)",(sarah,"Office (demo)","5 Sample Road","Manchester","United Kingdom","M1 1AA"))
    for pid in(2,11,57):ex("INSERT INTO wishlist VALUES(?,?)",(sarah,pid))
    stages=[2,0,4,6,8,9,1]
    from i18n import STAGES
    locs=["Sialkot","KORA Sialkot Office","KORA Sialkot Office","KORA Sialkot Office","Seller workshop, Sialkot","Sialkot dispatch","Motorway M-2","Lahore Warehouse","Local courier, destination city","Delivered"]
    for i,st in enumerate(stages):
        pid=first[i];p=c.execute("SELECT price,moq FROM products WHERE id=?",(pid,)).fetchone();q=p["moq"]
        oid=c.execute("INSERT INTO orders(code,product_id,buyer_id,seller_id,qty,amount,stage,cancelled,staff_id,created) VALUES(?,?,?,?,?,?,?,?,?,?)",(f"KR-{1001+i}",pid,sarah,ahmed,q,q*p["price"],st,1 if i==6 else 0,bilal,ago(12-i))).lastrowid
        for s in range(st+1):ex("INSERT INTO order_events(order_id,stage,ts,location,note) VALUES(?,?,?,?,?)",(oid,s,ago(12-i,-s),locs[s],"Simulated demo event"))
    def conv(a,b,oid=None):return c.execute("INSERT INTO conversations(u1,u2,order_id) VALUES(?,?,?)",(a,b,oid)).lastrowid
    langs={ahmed:"ur",sarah:"en",bilal:"ur"}
    def msg(cid,frm,to,pi,side,mins,read=1):
        text=PH[pi][0 if side=="en" else 1];m=c.execute("INSERT INTO messages(conv_id,sender_id,body,lang,created,read) VALUES(?,?,?,?,?,?)",(cid,frm,text,side,ago(0,0)[:11]+mins,read)).lastrowid
        tr,stt=translate_for(text,side,langs[to])
        if stt!="same":ex("INSERT INTO translations VALUES(?,?,?,?)",(m,langs[to],tr,stt))
    cs=conv(sarah,ahmed,1);msg(cs,sarah,ahmed,0,"en","10:20");msg(cs,ahmed,sarah,1,"ur","10:22");msg(cs,sarah,ahmed,2,"en","10:24",0);msg(cs,sarah,ahmed,6,"en","10:25",0)
    ck=conv(ahmed,bilal,1);msg(ck,bilal,ahmed,10,"ur","09:50");msg(ck,ahmed,bilal,11,"ur","09:52");msg(ck,bilal,ahmed,3,"ur","09:55",0)
    cb=conv(sarah,bilal,1);msg(cb,bilal,sarah,3,"ur","09:56");msg(cb,sarah,bilal,2,"en","10:01");msg(cb,bilal,sarah,4,"ur","10:05",0)
    for u,tx in[(ahmed,"New order KR-1002 received."),(ahmed,"KORA approved order KR-1001 for packing."),(sarah,"Order KR-1005 is out for delivery (simulated)."),(bilal,"Order KR-1001 assigned to you.")]:
        ex("INSERT INTO notifications(user_id,text,created) VALUES(?,?,?)",(u,tx,ago(0,2)))
    ex("INSERT INTO verification_records(order_id,staff_id,result,notes,created) VALUES(1,?,?,?,?)",(bilal,"pending","Photos requested from seller",ago(1)))
    ex("INSERT INTO audit_log(actor_id,action,detail,created) VALUES(?,?,?,?)",(bilal,"assign","KR-1001 assigned",ago(1)))
