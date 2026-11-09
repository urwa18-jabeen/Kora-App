"""Staff accounts are NEVER created by public signup. Usage:
   python create_staff.py staff@example.com "StrongPass1" "Full Name" KORA-H-002"""
import sys
from werkzeug.security import generate_password_hash
from database import connect,REAL,SCHEMA
if len(sys.argv)<5:sys.exit(__doc__)
e,p,n,s=sys.argv[1:5];c=connect(REAL);c.executescript(SCHEMA)
c.execute("INSERT INTO users(name,email,pw_hash,role,lang,staff_id,title) VALUES(?,?,?,?,?,?,?)",(n,e.lower(),generate_password_hash(p),"staff","ur",s,"Verification Officer"));c.commit();print("Staff created:",e)
