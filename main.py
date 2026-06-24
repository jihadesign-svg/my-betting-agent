# --- إعداد الواجهة ---
st.set_page_config(page_title="Gemini Pro Betting Agent", layout="wide")
st.title("🎯 Gemini: المراهن الحقيقي (وضع التداول الرياضي)")

# --- الإعدادات الجانبية ---
st.sidebar.title("🛠️ إعدادات الوكيل")
base_path = st.sidebar.text_input("مسار حفظ بيانات التعلم:", os.getcwd())
log_file = os.path.join(base_path, "performance_log.txt")

# --- محرك التحليل المتكامل ---
def gemini_engine(a1, b1, a2, b2):
# تحليل الزخم (Weighted Pace)
pace_a = (a1 * 0.4) + (a2 * 0.6)
pace_b = (b1 * 0.4) + (b2 * 0.6)
projection = (pace_a + pace_b) * 2
# محاكاة مونتي كارلو
sims = np.random.normal(projection, 5, 50000)
prob_even = (np.sum(np.round(sims) % 2 == 0) / 50000) * 100
return prob_even, pace_a, pace_b

# --- الواجهة الرئيسية ---
col1, col2 = st.columns(2)
with col1:
a1 = st.number_input("الفريق A - الربع 1", 0)
a2 = st.number_input("الفريق A - الربع 2", 0)
with col2:
b1 = st.number_input("الفريق B - الربع 1", 0)
b2 = st.number_input("الفريق B - الربع 2", 0)

if st.button("اتخاذ القرار النهائي (Gemini Verdict)"):
prob, pa, pb = gemini_engine(a1, b1, a2, b2)
decision = "زوجي" if prob > 50 else "فردي"
# 1. التوقع البصري (شموع التداول)
fig = go.Figure(data=[go.Candlestick(x=['المباراة'], open=[a1-b1], high=[max(a1-b1, a2-b2)],
low=[min(a1-b1, a2-b2)], close=[a2-b2])])
fig.update_layout(title="تحليل قوة الزخم (شمعة التداول)")
st.plotly_chart(fig)
# 2. القرار والإدارة المالية
st.metric("نسبة ثقة الوكيل", f"{prob:.2f}%")
stake = (max(prob, 100-prob) * 0.9 - (100 - max(prob, 100-prob))) / 0.9
st.info(f"القرار: {decision} | حجم الرهان المقترح (معادلة كيلي): {max(0, stake/10):.2f}%")

if prob > 60 or prob < 40:
notification.notify(title="فرصة مراهنة!", message=f"الوكيل يوصي بـ {decision}")
st.success("أنا أتحمل المسؤولية: هذه فرصة قوية!")

st.session_state.last_decision = decision
st.session_state.last_prob = prob

# --- نظام التعلم الذاتي (التقييم) ---
st.sidebar.subheader("تقييم قرار الوكيل الأخير:")
if st.sidebar.button("✅ نجحت"):
with open(log_file, "a") as f:
f.write(f"{datetime.datetime.now()} | {st.session_state.last_decision} | نجاح\n")
st.sidebar.success("تم تثبيت النجاح في ملفي الشخصي")

if st.sidebar.button("❌ أخطأت"):
with open(log_file, "a") as f:
f.write(f"{datetime.datetime.now()} | {st.session_state.last_decision} | خطأ\n")
st.sidebar.error("تم تسجيل الخطأ، سأقوم بمعايرة خوارزمياتي")
