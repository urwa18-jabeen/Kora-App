"""Urdu/English text. Add a key here, use {{ t('key') }} in templates."""
from flask import g
T={
"welcome":("Welcome to KORA","خوش آمدید"),"pick_lang":("Select Your Language","زبان کا انتخاب کریں"),
"signup":("Create Account","نیا اکاؤنٹ بنائیں"),"login":("Log In","لاگ اِن کریں"),"demo":("Explore Demo","ڈیمو دیکھیں"),
"demo_banner":("DEMO MODE - fictional data, no real OTP or payments","ڈیمو موڈ - فرضی ڈیٹا، کوئی حقیقی OTP یا ادائیگی نہیں"),
"full_name":("Full Name","پورا نام"),"contact":("Phone Number or Email","فون نمبر یا ای میل"),"password":("Password","پاس ورڈ"),
"confirm":("Confirm Password","پاس ورڈ کی تصدیق"),"who":("What would you like to be?","آپ کیا بننا چاہیں گے؟"),
"seller":("Seller","فروخت کنندہ"),"buyer":("Buyer","خریدار"),"continue":("Continue","جاری رکھیں"),
"verify_title":("Verification Code","تصدیقی کوڈ"),"enter_otp":("Enter the 6-digit code","6 ہندسوں کا کوڈ درج کریں"),
"demo_otp":("Demo OTP","ڈیمو OTP"),"verify":("Verify","تصدیق کریں"),"resend":("Resend Code","کوڈ دوبارہ بھیجیں"),
"forgot":("Forgot Password?","پاس ورڈ بھول گئے؟"),"reset_pw":("Reset Password","پاس ورڈ ری سیٹ کریں"),"new_pw":("New Password","نیا پاس ورڈ"),
"reset_sent":("If this account exists, a code was sent to its verified phone/email.","اگر یہ اکاؤنٹ موجود ہے تو کوڈ بھیج دیا گیا ہے۔"),
"bad_login":("Invalid details.","غلط تفصیلات۔"),"locked":("Too many attempts. Try again in 5 minutes.","بہت زیادہ کوششیں۔ 5 منٹ بعد کوشش کریں۔"),
"bad_name":("Please enter a valid name.","درست نام درج کریں۔"),"bad_contact":("Enter a valid phone number or email.","درست فون نمبر یا ای میل درج کریں۔"),
"bad_pw":("Password needs 8+ characters with a letter and a number.","پاس ورڈ میں 8+ حروف، ایک حرف اور ایک عدد ہونا چاہیے۔"),
"pw_mismatch":("Passwords do not match.","پاس ورڈ مماثل نہیں۔"),"exists":("An account already exists. Please log in.","اکاؤنٹ پہلے سے موجود ہے۔ لاگ اِن کریں۔"),
"bad_otp":("Wrong code.","غلط کوڈ۔"),"otp_exp":("Code expired. Start again.","کوڈ کی میعاد ختم۔ دوبارہ شروع کریں۔"),
"cooldown":("Please wait before requesting another code.","نیا کوڈ مانگنے سے پہلے انتظار کریں۔"),"otp_sent":("New code generated.","نیا کوڈ بن گیا۔"),
"home":("Home","ہوم"),"orders":("Orders","آرڈرز"),"chat":("Kora Team Chat","کورا ٹیم سے رابطہ"),"profile":("Profile","پروفائل"),
"queue":("Order Queue","آرڈر قطار"),"notifications":("Notifications","اطلاعات"),"logout":("Log out","لاگ آؤٹ"),
"search_ph":("Search products, shops, sellers...","پروڈکٹس، دکانیں یا سیلرز تلاش کریں..."),"search":("Search","تلاش"),
"all_cats":("All categories","تمام زمرے"),"max_price":("Max price (Rs.)","زیادہ سے زیادہ قیمت"),
"earn":("This Month's Earnings","اس ماہ کی کمائی"),"hello":("Welcome","خوش آمدید"),"vs_last":("compared with last month","پچھلے ماہ کے مقابلے میں"),
"messages":("Your Messages","آپ کے پیغامات"),"recommended":("Recommended","تجویز کردہ"),"results":("Results","نتائج"),"none":("Nothing found.","کچھ نہیں ملا۔"),
"catalogue":("Product Catalogue","مصنوعات کا کیٹلاگ"),"add_product":("Add product","پروڈکٹ شامل کریں"),"edit":("Edit","ترمیم"),"delete":("Delete","حذف کریں"),"save":("Save","محفوظ کریں"),
"pname":("Product name","پروڈکٹ کا نام"),"descr":("Description","تفصیل"),"category":("Category","زمرہ"),"price":("Price (PKR)","قیمت (روپے)"),"moq":("Minimum order qty","کم از کم آرڈر"),
"stock":("Available stock","دستیاب اسٹاک"),"location":("Manufacturing location","تیاری کا مقام"),"specs":("Specifications","خصوصیات"),"custom":("Customization available","کسٹمائزیشن دستیاب"),"photo":("Photo","تصویر"),
"order_now":("Place order","آرڈر دیں"),"qty":("Quantity","مقدار"),"address":("Delivery address","ڈیلیوری کا پتہ"),"wishlist":("Wishlist","وش لسٹ"),"saved":("Saved.","محفوظ ہو گیا۔"),
"order_placed_msg":("Order placed. KORA will verify it.","آرڈر دے دیا گیا۔ کورا تصدیق کرے گا۔"),"bad_qty":("Quantity must be between MOQ and stock.","مقدار MOQ اور اسٹاک کے درمیان ہونی چاہیے۔"),
"order_id":("Order","آرڈر"),"buyer_l":("Buyer","خریدار"),"seller_l":("Seller","فروخت کنندہ"),"pcs":("pcs","عدد"),"total":("Total","کل"),
"sim_track":("SIMULATED tracking - not real GPS","فرضی ٹریکنگ - اصل GPS نہیں"),"current_loc":("Current location","موجودہ مقام"),"all":("All","سب"),
"approve":("Approve","منظور کریں"),"flag":("Flag problem","مسئلہ نشان زد کریں"),"cancel":("Cancel order","آرڈر منسوخ کریں"),"set_stage":("Set stage","مرحلہ منتخب کریں"),
"note":("Note","نوٹ"),"update":("Update","اپڈیٹ"),"assign_me":("Assign to me","مجھے تفویض کریں"),"audit":("Audit history","آڈٹ ہسٹری"),"assigned":("Assigned","تفویض شدہ"),
"type_msg":("Type a message...","پیغام لکھیں..."),"send":("Send","بھیجیں"),"translated_from":("Translated from","ترجمہ شدہ از"),"view_orig":("View original","اصل دیکھیں"),"view_tr":("View translation","ترجمہ دیکھیں"),
"tr_unavailable":("Translation unavailable - showing original","ترجمہ دستیاب نہیں - اصل پیغام"),"no_staff":("No KORA team member is available yet.","ابھی کوئی کورا ٹیم ممبر دستیاب نہیں۔"),
"quick":("Quick replies","فوری جوابات"),"online":("Online","آن لائن"),"verification_officer":("Verification Officer","ویریفکیشن آفیسر"),
"edit_profile":("Edit Profile","پروفائل میں ترمیم"),"language":("Language","زبان"),"biz":("Business name","کاروبار کا نام"),"category_l":("Business category","کاروباری زمرہ"),
"city":("City","شہر"),"road":("Road name","سڑک کا نام"),"area":("Area / locality","علاقہ"),"landmark":("Landmark (optional)","نشانی (اختیاری)"),"postal":("Postal code","پوسٹل کوڈ"),
"profile_photo":("Profile photo","پروفائل تصویر"),"shop_photo":("Shop photo","دکان کی تصویر"),"bank":("Bank and Payment Details","بینک اور ادائیگی کی تفصیلات"),
"provider":("Bank / provider","بینک / فراہم کنندہ"),"holder":("Account holder","اکاؤنٹ ہولڈر"),"acc_no":("Account / IBAN / mobile no.","اکاؤنٹ / IBAN / موبائل نمبر"),"nick":("Nickname","عرفیت"),
"default":("Default","ڈیفالٹ"),"make_default":("Make default","ڈیفالٹ بنائیں"),"add":("Add","شامل کریں"),"bank_note":("Only the last 4 digits are stored. Never shown to buyers.","صرف آخری 4 ہندسے محفوظ ہوتے ہیں۔ خریداروں کو نظر نہیں آتے۔"),
"addresses":("Saved Addresses","محفوظ پتے"),"label":("Label","لیبل"),"line":("Street address","پتہ"),"country":("Country","ملک"),"help":("Help and Support","مدد اور سپورٹ"),
"help_text":("Chat with the KORA team from the Chat tab. Email: support@kora.example (placeholder).","چیٹ ٹیب سے کورا ٹیم سے رابطہ کریں۔ ای میل: support@kora.example (نمونہ)۔"),
"reset_demo":("Reset Demo Data","ڈیمو ڈیٹا ری سیٹ کریں"),"demo_reset_done":("Demo data restored.","ڈیمو ڈیٹا بحال ہو گیا۔"),"exit_demo":("Exit demo","ڈیمو سے باہر"),
"one_tap":("One-tap login","ایک ٹیپ لاگ اِن"),"seller_demo":("Seller Demo","فروخت کنندہ ڈیمو"),"buyer_demo":("Buyer Demo","خریدار ڈیمو"),"team_demo":("KORA Team Demo","کورا ٹیم ڈیمو"),
"staff_login":("KORA Team Login","کورا ٹیم لاگ اِن"),"private_route":("Private staff route","نجی اسٹاف راستہ"),"bad_file":("Only JPG/PNG/WEBP images up to 5 MB.","صرف JPG/PNG/WEBP تصاویر، 5 MB تک۔"),
"rating":("Rating","درجہ بندی"),"reviews":("reviews","جائزے"),"view_seller":("View seller","سیلر دیکھیں"),"unread":("unread","نہ پڑھے"),"mark_read":("Mark all read","سب پڑھا ہوا"),
"cat_edit_note":("Email/phone changes need OTP verification (not enabled).","ای میل/فون تبدیل کرنے کے لیے OTP ضروری ہے (فعال نہیں)۔"),
"recent_tx":("Recent transactions (simulated)","حالیہ لین دین (فرضی)"),"n_order":("Order {code} was updated.","آرڈر {code} اپڈیٹ ہوا۔"),"n_msg":("New message from {name}.","{name} کی طرف سے نیا پیغام۔"),"mic":("Voice search","آواز سے تلاش"),"manage":("Manage catalogue","کیٹلاگ منظم کریں"),
}
STAGES=[("Order Placed","آرڈر دیا گیا"),("Received by KORA","کورا کو موصول"),("Quality Verification","معیار کی جانچ"),("Approved","منظور"),("Packing","پیکنگ"),("Dispatched","روانہ"),("In Transit","راستے میں"),("Arrived at Warehouse","گودام پہنچا"),("Out for Delivery","ڈیلیوری کے لیے نکلا"),("Delivered","ڈیلیور شدہ")]
STATUS=[("Pending","زیر التواء"),("Under Verification","تصدیق جاری"),("Processing","پروسیسنگ"),("Shipped","بھیجا گیا"),("Out for Delivery","ڈیلیوری کے لیے نکلا"),("Delivered","ڈیلیور شدہ"),("Cancelled","منسوخ"),("Flagged","مسئلہ")]
def t(key,lang=None):
    lang=lang or getattr(g,"lang","en");v=T.get(key)
    return key if v is None else v[1 if lang=="ur" else 0]
def stage_name(i,lang=None):return STAGES[i][1 if (lang or g.lang)=="ur" else 0]
def status_name(i,lang=None):return STATUS[i][1 if (lang or g.lang)=="ur" else 0]
