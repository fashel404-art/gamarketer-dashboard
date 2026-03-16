import streamlit as st
import pandas as pd

# 🎨 إعدادات واجهة جماركتير
st.set_page_config(page_title="Gamarketer Dashboard", layout="wide")

st.markdown("""
    <style>
    .metric-card { background-color: #F3E5F5; border-radius: 10px; padding: 15px; border-left: 5px solid #9C27B0; text-align: center; color: #4A148C; }
    .stProgress > div > div > div > div { background-color: #9C27B0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🦉 محلل بيانات جماركتير")
st.write("ارفع ملف 'القدر' وسأقوم بحساب كل شيء فوراً.")

# 📥 رفع الملف
uploaded_file = st.file_uploader("ارفع ملف الإكسل هنا", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        # قراءة الملف (دعم الإكسل و CSV)
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl')

        # تنظيف البيانات (حذف الصفوف الفارغة)
        df = df.dropna(how='all')

        # 🔍 البحث التلقائي عن الأعمدة
        cols = df.columns.tolist()
        def get_col(keys):
            for k in keys:
                for c in cols:
                    if k.lower() in str(c).lower(): return c
            return cols[0]

        # تحديد الأعمدة
        spend_c = get_col(["المبلغ", "Spent", "Amount"])
        impr_c = get_col(["الظهور", "Impressions"])
        thru_c = get_col(["ThruPlay", "ثروبلاي"])
        v3s_c = get_col(["3-Second", "3 ثوانٍ"])

        # تحويل القيم لأرقام
        for col in [spend_c, impr_c, thru_c, v3s_c]:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.extract('(\d+\.?\d*)')[0], errors='coerce').fillna(0)

        # 🧮 الحسابات الأساسية
        total_spend = df[spend_c].sum()
        total_impr = df[impr_c].sum()
        total_thru = df[thru_c].sum()
        total_3s = df[v3s_c].sum()

        hook_rate = (total_3s / total_impr) * 100 if total_impr > 0 else 0
        hold_rate = (total_thru / total_3s) * 100 if total_3s > 0 else 0
        cpt = total_spend / total_thru if total_thru > 0 else 0

        # 📊 عرض النتائج في كروت احترافية
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card">💰 الإنفاق<br><h2>{total_spend:,.2f}</h2></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card">🎬 ثروبلاي<br><h2>{total_thru:,.0f}</h2></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card">💸 تكلفة الثروبلاي<br><h2>{cpt:.2f}</h2></div>', unsafe_allow_html=True)

        st.divider()

        # 🎯 تحليل الأداء
        c_hook, c_hold = st.columns(2)
        with c_hook:
            st.subheader("🪝 Hook Rate (قوة الخطف)")
            st.metric("النسبة", f"{hook_rate:.2f}%")
            st.progress(min(int(hook_rate), 100))
            if hook_rate < 15: st.error("⚠️ الخطاف ضعيف! الجمهور لا يكمل أول 3 ثوانٍ.")
            else: st.success("✅ خطاف ممتاز!")

        with c_hold:
            st.subheader("⏱️ Hold Rate (الاحتفاظ)")
            st.metric("النسبة", f"{hold_rate:.2f}%")
            st.progress(min(int(hold_rate), 100))
            if hold_rate < 30: st.warning("⚠️ المحتوى ممل في المنتصف.")
            else: st.success("✅ محتوى مقنع وجذاب!")

    except Exception as e:
        st.error(f"حدث خطأ: {e}")
        st.info("تأكد من عمل Reboot للتطبيق من قائمة Manage App.")
