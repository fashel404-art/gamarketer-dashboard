import streamlit as st
import pandas as pd
from PIL import Image

# 🎨 1. إعدادات الهوية البصرية (لافندر وبنفسجي)
st.set_page_config(page_title="Gamarketer Dashboard", layout="wide")

st.markdown("""
    <style>
    .metric-card { background-color: #F3E5F5; border-radius: 10px; padding: 15px; border-left: 5px solid #9C27B0; text-align: center; }
    .stProgress > div > div > div > div { background-color: #9C27B0; }
    </style>
    """, unsafe_allow_html=True)

# 🦉 2. الشعار والعنوان
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        st.image('logo.png', width=120)
    except:
        st.write("🦉 **Gamarketer**")

with col_title:
    st.title("محلل بيانات جماركتير الذكي")
    st.write("لوحة تحكم جمال حسان لتحليل الفيديوهات الإعلانية")

st.divider()

# 📥 3. منطقة رفع الملف
uploaded_file = st.file_uploader("ارفع ملف Excel الخاص بمدير الإعلانات", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("✅ تم استلام البيانات! حدد الأعمدة من القائمة الجانبية.")

        # ⚙️ 4. القائمة الجانبية لاختيار الأعمدة
        st.sidebar.header("⚙️ ضبط الأعمدة")
        col_names = df.columns.tolist()
        spend_col = st.sidebar.selectbox("عمود الإنفاق", col_names)
        impr_col = st.sidebar.selectbox("عمود الظهور (Impressions)", col_names)
        thru_col = st.sidebar.selectbox("عمود الثروبلاي (ThruPlays)", col_names)
        views3s_col = st.sidebar.selectbox("عمود مشاهدات 3 ثوانٍ", col_names)

        # الحسابات
        total_spend = df[spend_col].sum()
        total_impr = df[impr_col].sum()
        total_thru = df[thru_col].sum()
        total_3s = df[views3s_col].sum()

        hook_rate = (total_3s / total_impr) * 100 if total_impr > 0 else 0
        hold_rate = (total_thru / total_3s) * 100 if total_3s > 0 else 0
        cpt = total_spend / total_thru if total_thru > 0 else 0

        # 📊 5. العرض البصري
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card">💰 الإنفاق الكلي<br><h3>{total_spend:,.2f}</h3></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card">🎬 ثروبلاي<br><h3>{total_thru:,}</h3></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card">💸 تكلفة الثروبلاي<br><h3>{cpt:.2f}</h3></div>', unsafe_allow_html=True)

        st.divider()
        
        # تحليل الجودة
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
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
else:
    st.info("💡 بانتظار رفع الملف للتحليل...")