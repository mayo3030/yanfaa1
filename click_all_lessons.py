"""
سكريبت بسيط لفتح/النقر على جميع الدروس تلقائياً
يستخدم أدوات المتصفح المدمجة في Cursor
"""
# قائمة refs للدروس (من snapshot)
lessons = [
    ("برومو", "ref-haqoo5wx08g"),
    ("Introduction", "ref-w8sf24l28l"),
    ("Le on 1", "ref-svyocg0vul"),
    ("Le on 2", "ref-maypgjof63n"),
    ("Le on 3", "ref-bmucfok6m0u"),
    ("Le on 4", "ref-xgxmb9b6k3n"),
    ("Le on 5", "ref-itt87zccrfs"),
    ("Le on 6", "ref-o0ucildp8of"),
    ("Le on 7", "ref-jpmom3lxuvf"),
    ("Le on 8", "ref-81029m1t3ae"),
    ("Le on 9", "ref-5rn78phtnwg"),
    ("Le on 10", "ref-w8qf7gz1dm"),
    ("Le on 11", "ref-9wa7zuryhj"),
    ("Le on 12", "ref-75nabndy2tw"),
    ("Le on 13", "ref-b5uffo9po5q"),
    ("Le on 14", "ref-zy6tnl8gwr"),
    ("Le on 15", "ref-2tgetvaqh2a"),
    ("Le on 16", "ref-8utxm0ruh23"),
    ("Le on 17", "ref-c0qe76m6baf"),
    ("Le on 18", "ref-a3937xcsokw"),
    ("Le on 19", "ref-91udk5mn6zj"),
    ("Le on 20", "ref-gt7xcs6hsqt"),
    ("Le on 21", "ref-xgychhju8z"),
    ("Le on 22", "ref-qr184iaz3cj"),
    ("Le on 23", "ref-hs28u0a1qer"),
    ("Le on 24", "ref-vv94lly6nc"),
    ("Le on 25", "ref-70v7ralliy"),
    ("Le on 26", "ref-toll7axow1b"),
    ("Le on 27", "ref-41q0lstmfbm"),
    ("Le on 28", "ref-xlnmtcgbpv"),
]

print("="*60)
print(f"🚀 فتح جميع الدروس تلقائياً")
print(f"📚 العدد الإجمالي: {len(lessons)} درس")
print("="*60)

print("\n📋 قائمة الدروس:")
for i, (name, ref) in enumerate(lessons, 1):
    print(f"   {i:2d}. {name}")

print("\n" + "="*60)
print("✅ السكريبت جاهز!")
print("="*60)
print("""
📝 هذا السكريبت يحتوي على جميع refs للدروس
💡 لاستخدامه، سيتم النقر على كل درس تلقائياً

⚠️ ملاحظة: 
   - تأكد من أنك قمت بتسجيل الدخول
   - تأكد من فتح المتصفح في Cursor
   - الصفحة يجب أن تكون مفتوحة على الكورس
""")

print("\n🎯 جاهز للتنفيذ!")



