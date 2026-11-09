"""Automatic message translation (Urdu <-> English, extensible).
Order: 1) built-in phrasebook (works offline for the demo)  2) Google Cloud Translation if env GOOGLE_TRANSLATE_KEY is set  3) 'unavailable' (original shown)."""
import os,re,json,urllib.request
PH=[("Can you dispatch the order by tomorrow?","کیا آپ کل تک آرڈر بھیج سکتے ہیں؟"),("Yes, it will be ready tomorrow.","جی ہاں، یہ کل تک تیار ہو جائے گا۔"),
("Please send me the product pictures.","براہ کرم مجھے پروڈکٹ کی تصاویر بھیجیں۔"),("Your order is ready for verification.","آپ کا آرڈر تصدیق کے لیے تیار ہے۔"),
("Order checked, ready to ship.","آرڈر چیک ہو گیا، بھیجنے کے لیے تیار ہے۔"),("Thank you!","شکریہ!"),("Where is my order?","میرا آرڈر کہاں ہے؟"),
("Packing is done.","پیکنگ مکمل ہو گئی ہے۔"),("Is this item in stock?","کیا یہ آئٹم اسٹاک میں ہے؟"),("Yes, it is available.","جی ہاں، دستیاب ہے۔"),
("Please share clearer photos of the product.","براہ کرم پروڈکٹ کی صاف تصاویر بھیجیں۔"),("Photos uploaded.","تصاویر اپ لوڈ کر دی گئی ہیں۔")]
def detect(text):return "ur" if re.search(r"[\u0600-\u06FF]",text or "") else "en"
def _n(s):return re.sub(r"[\s\.\!\?؟۔،,]+"," ",s).strip().lower()
def _book(text,src,dst):
    i=0 if src=="en" else 1;j=0 if dst=="en" else 1
    for p in PH:
        if _n(p[i])==_n(text):return p[j]
def _protect(text,terms):
    esc=lambda s:s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    pat="|".join([re.escape(esc(x)) for x in terms if x]+[r"[A-Z]{2,4}-\d{3,}",r"\+?\d[\d\s-]{6,}\d",r"\d[\d,.]*"])
    return re.sub(pat,lambda m:'<span translate="no">%s</span>'%m.group(0),esc(text))
def _online(text,dst,terms):
    key=os.getenv("GOOGLE_TRANSLATE_KEY")
    if not key:return None
    body=json.dumps({"q":_protect(text,terms),"target":dst,"format":"html"}).encode()
    r=urllib.request.Request("https://translation.googleapis.com/language/translate/v2?key="+key,body,{"Content-Type":"application/json"})
    out=json.load(urllib.request.urlopen(r,timeout=8))["data"]["translations"][0]["translatedText"]
    out=re.sub(r"<[^>]+>","",out)
    for a,b in(("&#39;","'"),("&quot;",'"'),("&lt;","<"),("&gt;",">"),("&amp;","&")):out=out.replace(a,b)
    return out
def translate_for(text,src,dst,terms=()):
    """returns (translated_text or None, status). The ORIGINAL message is always stored separately and never changed."""
    if src==dst:return None,"same"
    r=_book(text,src,dst)
    if r:return r,"ok"
    try:
        r=_online(text,dst,terms)
        if r:return r,"ok"
    except Exception:pass
    return None,"unavailable"
