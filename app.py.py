import streamlit as st
import pandas as pd

# 🎨 إعدادات واجهة جماركتير الاحترافية
st.set_page_config(page_title="Gamarketer Pro Dashboard", layout="wide")

st.markdown("""
    <style>
    .metric-box { background-color: #F3E5F5; border-radius: 12px; padding: 20px; border-right: 5px solid #9C27B0; text-align: center; color: #4A148C; margin-bottom: 10px; }
    .stProgress > div > div > div > div { background-color: #9C27B0; }
    h3 { color: #6A1B9A; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦉 محلل جماركتير الذكي - Gamarketer Pro")
st.write("تحليل شامل للمقاييس (CAC, LTV, ROAS) وقوة المحتوى الإعلاني")

# 📥 رفع الملف
uploaded_file = st.file_uploader("ارفع ملف 'القدر' أو أي تقرير إعلانات", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # قراءة ذكية لتخطي الصفوف التعريفية في البداية
        if uploaded_file.name.endswith('.csv'):
            df_temp = pd.read_csv(uploaded_file, header=None)
        else:
            df_temp = pd.read_excel(uploaded_file, header=None)

        # البحث عن أول صف يحتوي على بيانات حقيقية (زي "اسم الحملة" أو "المبلغ")
        header_index = 0
        for i, row in df_temp.iterrows():
            if any(word in str(row.values) for word in ["اسم", "المبلغ", "Campaign", "Spent", "Amount"]):
                header_index = i
                break
        
        # إعادة القراءة من الصف الصحيح
        uploaded_file.seek(0)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, skiprows=header_index)
        else:
            df = pd.read_excel(uploaded_file, skiprows=header_index)

        # تنظيف البيانات
        df = df.dropna(how='all').reset_index(drop=True)

        # ⚙️ محرك التعرف التلقائي على الأعمدة
        cols = df.columns.tolist()
        def find_c(keys):
            for k in keys:
                for c in cols:
                    if k.lower() in str(c).lower(): return c
            return None

        # تعيين الأعمدة
        sp_c = find_c(["المبلغ", "Spent", "Amount"])
        im_c = find_c(["الظهور", "Impressions"])
        th_c = find_c(["ThruPlay", "ثروبلاي"])
        v3_c = find_c(["3 ثوانٍ", "3-Second"])
        pu_c = find_c(["عمليات الشراء", "Purchases", "Results"])
        va_c = find_c(["قيمة", "Value", "Revenue"])

        # تحويل البيانات لأرقام ومعالجة العملات (EGP, SR...)
        for c in [sp_c, im_c, th_c, v3_c, pu_c, va_c]:
            if c:
                df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', '').str.extract('(\d+\.?\d*)')[0], errors='coerce').fillna(0)

        # 🧮 الحسابات المتقدمة
        total_spend = df[sp_c].sum() if sp_c else 0
        total_purchases = df[pu_c].sum() if pu_c else 1 # لتجنب القسمة على صفر
        total_revenue = df[va_c].sum() if va_c else 0
        
        # المقاييس اللي طلبتها:
        cac = total_spend / total_purchases if total_purchases > 0 else 0
        roas = total_revenue / total_spend if total_spend > 0 else 0
        hook_rate = (df[v3_c].sum() / df[im_c].sum() * 100) if im_c and v3_c else 0
        hold_rate = (df[th_c].sum() / df[v3_c].sum() * 100) if v3_c and th_c else 0

        # 📊 عرض النتائج في مربعات
        st.subheader("🚀 مقاييس النمو والأداء")
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-box">💰 الإنفاق<br><h3>{total_spend:,.2f}</h3></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-box">🎯 CAC (تكلفة العميل)<br><h3>{cac:,.2f}</h3></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-box">📈 ROAS<br><h3>{roas:.2f}x</h3></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-box">💎 الإيرادات<br><h3>{total_revenue:,.2f}</h3></div>', unsafe_allow_html=True)

        st.divider()

        # 🎬 تحليل جودة الفيديو
        st.subheader("🎬 تحليل سلوك المشاهد (Video Funnel)")
        c_h, c_r = st.columns(2)
        with c_h:
            st.write(f"**Hook Rate:** {hook_rate:.2f}%")
            st.progress(min(int(hook_rate), 100))
            if hook_rate < 20: st.error("❌ الخطاف ضعيف - الجمهور لا ينجذب للفيديو")
            else: st.success("✅ خطاف قوي - المحتوى جذاب")

        with c_r:
            st.write(f"**Hold Rate:** {hold_rate:.2f}%")
            st.progress(min(int(hold_rate), 100))
            if hold_rate < 30: st.warning("⚠️ محتوى ممل - المشاهد يهرب في المنتصف")
            else: st.success("✅ محتوى مقنع - المشاهد يكمل الفيديو")

        # عرض الجدول النهائي للتأكد
        with st.expander("👁️ استعراض البيانات الخام التي تم تحليلها"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"حدث خطأ في قراءة البيانات: {e}")
else:
    st.info("👋 مرحباً جمال! ارفع ملف إكسل من مدير الإعلانات وسأظهر لك الـ CAC والـ ROAS وقوة الفيديو فوراً.")
