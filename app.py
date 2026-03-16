import streamlit as st
import pandas as pd
from PIL import Image

# 🎨 إعدادات الهوية البصرية
st.set_page_config(page_title="Gamarketer Dashboard", layout="wide")

st.markdown("""
    <style>
    .metric-card { background-color: #F3E5F5; border-radius: 10px; padding: 15px; border-left: 5px solid #9C27B0; text-align: center; }
    .stProgress > div > div > div > div { background-color: #9C27B0; }
    </style>
    """, unsafe_allow_html=True)

# 🦉 الشعار والعنوان
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        st.image('logo.png', width=120)
    except:
        st.write("🦉 **Gamarketer**")

with col_title:
    st.title("محلل بيانات جماركتير الذكي")
    st.write("لوحة تحكم احترافية لتحليل حملات الفيديو")

st.divider()

# 📥 رفع الملف
uploaded_file = st.file_uploader("ارفع ملف الإكسل الخاص بمدير الإعلانات", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # حل مشكلة الصفوف الفارغة: نبحث عن الصف الذي يحتوي على كلمة "اسم الحملة" أو "المبلغ"
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file, header=None)
        else:
            df_raw = pd.read_excel(uploaded_file, header=None)

        # البحث عن صف العناوين تلقائياً
        header_row = 0
        for i, row in df_raw.iterrows():
            if "اسم الحملة" in str(row.values) or "المبلغ" in str(row.values):
                header_row = i
                break
        
        # إعادة قراءة الملف من الصف الصحيح
        uploaded_file.seek(0)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, skiprows=header_row)
        else:
            df = pd.read_excel(uploaded_file, skiprows=header_row)

        # تنظيف البيانات من الصفوف الفارغة تماماً
        df = df.dropna(how='all').reset_index(drop=True)

        st.success("✅ تم استلام البيانات بنجاح!")

        # ⚙️ القائمة الجانبية
        st.sidebar.header("⚙️ ضبط الأعمدة")
        col_names = df.columns.tolist()
        
        # محاولة اختيار الأعمدة تلقائياً إذا كانت الأسماء مطابقة
        def find_col(keywords, options):
            for k in keywords:
                for opt in options:
                    if k in str(opt): return opt
            return options[0]

        spend_col = st.sidebar.selectbox("عمود الإنفاق", col_names, index=col_names.index(find_col(["المبلغ", "Spent"], col_names)))
        impr_col = st.sidebar.selectbox("عمود الظهور", col_names, index=col_names.index(find_col(["الظهور", "Impressions"], col_names)))
        thru_col = st.sidebar.selectbox("عمود الثروبلاي", col_names, index=col_names.index(find_col(["ThruPlay"], col_names)))
        views3s_col = st.sidebar.selectbox("عمود 3 ثوانٍ", col_names, index=col_names.index(find_col(["3 ثوانٍ", "3-Second"], col_names)))

        # تحويل الأعمدة لأرقام (لأنها أحياناً تُقرأ كنصوص بسبب العملات)
        for c in [spend_col, impr_col, thru_col, views3s_col]:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', '').str.extract('(\d+\.?\d*)')[0], errors='coerce').fillna(0)

        total_spend = df[spend_col].sum()
        total_impr = df[impr_col].sum()
        total_thru = df[thru_col].sum()
        total_3s = df[views3s_col].sum()

        hook_rate = (total_3s / total_impr) * 100 if total_impr > 0 else 0
        hold_rate = (total_thru / total_3s) * 100 if total_3s > 0 else 0
        cpt = total_spend / total_thru if total_thru > 0 else 0

        # 📊 العرض البصري
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card">💰 الإنفاق الكلي<br><h3>{total_spend:,.2f}</h3></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card">🎬 ثروبلاي<br><h3>{total_thru:,.0f}</h3></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card">💸 تكلفة الثروبلاي<br><h3>{cpt:.2f}</h3></div>', unsafe_allow_html=True)

        st.divider()
        
        col_h, col_r = st.columns(2)
        with col_h:
            st.subheader("🪝 قوة الخطاف (Hook Rate)")
            st.metric("النسبة", f"{hook_rate:.2f}%")
            st.progress(int(min(hook_rate, 100)))
            if hook_rate < 15: st.error("❌ أول 3 ثوانٍ غير جذابة!")
            elif hook_rate > 30: st.success("💎 خطاف ممتاز!")

        with col_r:
            st.subheader("⏱️ الاحتفاظ (Hold Rate)")
            st.metric("النسبة", f"{hold_rate:.2f}%")
            st.progress(int(min(hold_rate, 100)))
            if hold_rate < 30: st.warning("🔶 الجمهور يمل بسرعة")
            elif hold_rate > 50: st.success("💎 المحتوى مقنع جداً!")

    except Exception as e:
        st.error(f"حدث خطأ في قراءة محتوى الملف: {e}")
        st.info("تأكد أن الملف يحتوي على أعمدة واضحة للإنفاق والظهور والثروبلاي.")
else:
    st.info("💡 بانتظار رفع ملف 'القدر.xlsx' للتحليل...")