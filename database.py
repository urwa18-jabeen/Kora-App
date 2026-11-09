import os,sqlite3
from flask import g,session
BASE=os.path.dirname(os.path.abspath(__file__))
REAL=os.path.join(BASE,"data","kora.db");DEMO=os.path.join(BASE,"data","kora_demo.db")  # separate files = demo can never touch real data
SCHEMA="""
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT,email TEXT UNIQUE,phone TEXT UNIQUE,pw_hash TEXT,role TEXT,lang TEXT DEFAULT 'en',photo TEXT,staff_id TEXT,title TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS seller_profiles(user_id INTEGER PRIMARY KEY,biz TEXT,descr TEXT,category TEXT,city TEXT,road TEXT,area TEXT,landmark TEXT,postal TEXT,shop_photo TEXT,rating REAL DEFAULT 0,reviews INTEGER DEFAULT 0,earn_this INTEGER,earn_prev INTEGER);
CREATE TABLE IF NOT EXISTS payment_accounts(id INTEGER PRIMARY KEY,user_id INTEGER,provider TEXT,holder TEXT,last4 TEXT,nickname TEXT,is_default INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY,seller_id INTEGER,seller_name TEXT,name TEXT,category TEXT,descr TEXT,price INTEGER,moq INTEGER,stock INTEGER,rating REAL,location TEXT,specs TEXT,custom INTEGER,image TEXT,hue INTEGER DEFAULT 200,emoji TEXT DEFAULT '📦');
CREATE TABLE IF NOT EXISTS wishlist(user_id INTEGER,product_id INTEGER,PRIMARY KEY(user_id,product_id));
CREATE TABLE IF NOT EXISTS addresses(id INTEGER PRIMARY KEY,user_id INTEGER,label TEXT,line TEXT,city TEXT,country TEXT,postal TEXT);
CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY,code TEXT UNIQUE,product_id INTEGER,buyer_id INTEGER,seller_id INTEGER,qty INTEGER,amount INTEGER,stage INTEGER DEFAULT 0,cancelled INTEGER DEFAULT 0,flagged INTEGER DEFAULT 0,staff_id INTEGER,created TEXT);
CREATE TABLE IF NOT EXISTS order_events(id INTEGER PRIMARY KEY,order_id INTEGER,stage INTEGER,ts TEXT,location TEXT,note TEXT);
CREATE TABLE IF NOT EXISTS conversations(id INTEGER PRIMARY KEY,u1 INTEGER,u2 INTEGER,order_id INTEGER);
CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY,conv_id INTEGER,sender_id INTEGER,body TEXT,lang TEXT,created TEXT,read INTEGER DEFAULT 0,attach TEXT);
CREATE TABLE IF NOT EXISTS translations(message_id INTEGER,lang TEXT,text TEXT,status TEXT,PRIMARY KEY(message_id,lang));
CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY,user_id INTEGER,text TEXT,created TEXT,read INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY,seller_id INTEGER,author TEXT,rating INTEGER,text TEXT);
CREATE TABLE IF NOT EXISTS verification_records(id INTEGER PRIMARY KEY,order_id INTEGER,staff_id INTEGER,result TEXT,notes TEXT,created TEXT);
CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY,actor_id INTEGER,action TEXT,detail TEXT,created TEXT);
"""
def connect(path):
    os.makedirs(os.path.dirname(path),exist_ok=True)
    c=sqlite3.connect(path);c.row_factory=sqlite3.Row;return c
def db():
    if "db" not in g:g.db=connect(DEMO if session.get("demo") else REAL)
    return g.db
def close_db(e=None):
    d=g.pop("db",None)
    if d:d.close()
def init_real():
    c=connect(REAL);c.executescript(SCHEMA);c.commit();c.close()
def init_demo(reset=True):
    if reset and os.path.exists(DEMO):os.remove(DEMO)
    if os.path.exists(DEMO):return
    from seed_data import seed
    c=connect(DEMO);c.executescript(SCHEMA);seed(c);c.commit();c.close()
