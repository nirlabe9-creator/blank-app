import streamlit as st
import google.generativeai as genai
import json
import datetime

# הגדרות עיצוב עברית ותצוגה למובייל
st.set_page_config(page_title="המונה שלי", page_icon="💪", layout="centered")

# כותרת האפליקציה
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>💪 מונה הקלוריות שלי</h1>", unsafe_allow_html=True)

# הזנת מפתח ה-API בצורה מאובטחת או דרך תיבה באפליקציה
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# יעדים קבועים לפי התוכנית שלך
CALORIE_GOAL = 2300
PROTEIN_GOAL = 160

# זיכרון נתונים
if 'calories' not in st.session_state:
    st.session_state.calories = 0
if 'protein' not in st.session_state:
    st.session_state.protein = 0
if 'history' not in st.session_state:
    st.session_state.history = []

# ממשק הגדרת מפתח ה-API בפעם הראשונה
if not st.session_state.api_key:
    st.subheader("מפתח API")
    key_input = st.text_input("הכנס את מפתח ה-Gemini API שלך (חד פעמי):", type="password")
    if st.button("שמור והמשך"):
        if key_input:
            st.session_state.api_key = key_input
            st.rerun()
    st.markdown("[לחץ כאן כדי להוציא מפתח בחינם ב-2 שניות מ-Google AI Studio](https://aistudio.google.com/)")
    st.stop()

# חיבור ל-AI
genai.configure(api_key=st.session_state.api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_food(text_input):
    prompt = f"""
    You are a nutrition expert. Analyze the following text in Hebrew or English and estimate the total calories and protein.
    Text: "{text_input}"
    You must respond ONLY with a valid JSON object, strictly containing these two keys: "calories" (as integer) and "protein" (as integer).
    Do not include markdown like ```json. Just raw JSON.
    """
    try:
        response = model.generate_content(prompt)
        clean_text = response.text.strip().replace("
```json", "").replace("```", "")
        data = json.loads(clean_text)
        return data.get("calories", 0), data.get("protein", 0)
    except:
        return 0, 0

# --- תצוגת מדדים ---
col1, col2 = st.columns(2)
with col1:
    st.metric(label="🔥 קלוריות שנאכלו", value=f"{st.session_state.calories} / {CALORIE_GOAL}")
    st.progress(min(st.session_state.calories / CALORIE_GOAL, 1.0))
with col2:
    st.metric(label="🍗 חלבון (גרם)", value=f"{st.session_state.protein} / {PROTEIN_GOAL}")
    st.progress(min(st.session_state.protein / PROTEIN_GOAL, 1.0))

st.markdown("<hr/>", unsafe_allow_html=True)

# --- הזנת אוכל ---
user_food = st.text_input("מה אכלת?", placeholder="לדוגמה: 2 סקופים חלבון עם חלב שיבולת שועל, או קופסת טונה ובננה")

if st.button("הוסף ליום שלי", use_container_width=True):
    if user_food:
        with st.spinner("מחשב..."):
            cals, prot = analyze_food(user_food)
            if cals > 0 or prot > 0:
                st.session_state.calories += cals
                st.session_state.protein += prot
                time_now = datetime.datetime.now().strftime("%H:%M")
                st.session_state.history.append(f"⏰ {time_now} - {user_food} ({cals} קלוריות, {prot}ג חלבון)")
                st.success(f"התווסף בהצלחה!")
                st.rerun()
    else:
        st.warning("תכתוב משהו קודם...")

# --- היסטוריה ---
if st.session_state.history:
    st.markdown("### 📝 מה אכלנו היום:")
    for item in reversed(st.session_state.history):
        st.info(item)

# --- איפוס ---
st.markdown("<br/><br/>", unsafe_allow_html=True)
if st.button("❌ איפוס יום (מתחילים מחדש)", use_container_width=True):
    st.session_state.calories = 0
    st.session_state.protein = 0
    st.session_state.history = []
    st.rerun()
