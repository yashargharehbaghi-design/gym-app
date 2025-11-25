# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# تلاش برای ایمپورت هوش مصنوعی
try:
    import google.generativeai as genai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# ==========================================
# 1. تنظیمات صفحه (باید اولین خط کد باشد)
# ==========================================
st.set_page_config(page_title="FitPro Coach 2025", layout="wide", page_icon="💪")
CSV_FILE = 'users_web_data.csv'

# تنظیم فونت و استایل راست‌چین برای فارسی
st.markdown("""
<style>
    body {direction: rtl; text-align: right;}
    .stTextInput, .stNumberInput, .stSelectbox {direction: rtl;}
    h1, h2, h3, p {font-family: 'Tahoma', sans-serif; text-align: right;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. منطق برنامه (Logic) - همان منطق نسخه دسکتاپ
# ==========================================
class BioCalculator:
    @staticmethod
    def calculate_age(birth_input):
        current_year_shamsi = 1403
        current_year_gregorian = datetime.now().year
        try:
            y = int(birth_input)
            if y < 100: return y
            if 1300 <= y <= 1500: return current_year_shamsi - y + 1
            if 1900 <= y <= current_year_gregorian: return current_year_gregorian - y
            return None
        except:
            return None

    @staticmethod
    def get_bmr_tdee(gender, weight, height_m, age, activity_days):
        height_cm = height_m * 100
        s = 5 if gender == 'Male' else -161
        bmr = (10 * weight) + (6.25 * height_cm) - (5 * age) + s
        factors = {0: 1.2, 1: 1.375, 2: 1.375, 3: 1.55, 4: 1.55, 5: 1.725, 6: 1.9}
        factor = factors.get(activity_days if activity_days < 7 else 6, 1.55)
        return bmr, bmr * factor

class CoachAI:
    def __init__(self, u, api_key=None):
        self.u = u
        self.api_key = api_key
        self.bmi = self.u['weight'] / (self.u['height'] ** 2)
        self.bmr, self.tdee = BioCalculator.get_bmr_tdee(
            self.u['gender'], self.u['weight'], self.u['height'], self.u['age'], self.u['days']
        )
        
        if self.bmi > 25: self.goal = "کاهش وزن"
        elif self.bmi < 18.5: self.goal = "افزایش حجم"
        else: self.goal = "تثبیت و تناسب"

    def ask_ai(self, prompt):
        if AI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel('gemini-pro')
                return model.generate_content(prompt).text
            except:
                return None
        return None

    def get_plan(self):
        # 1. تلاش برای AI
        prompt = f"برنامه تمرینی {self.u['days']} روزه و رژیم {int(self.tdee)} کالری برای {self.goal}. خلاصه و فارسی."
        ai_res = self.ask_ai(prompt)
        if ai_res: return ai_res

        # 2. آفلاین
        return f"""
        ### 📋 برنامه هوشمند آفلاین
        **هدف:** {self.goal} | **کالری:** {int(self.tdee)}
        
        **💪 تمرین پیشنهادی:**
        - تمرینات فول بادی (اسکات، سینه، زیربغل)
        - {self.u['days']} روز در هفته
        - کاردیو: { '۲۰ دقیقه بعد تمرین' if 'کاهش' in self.goal else '۱۰ دقیقه گرم کردن'}
        
        **🍎 تغذیه:**
        - پروتئین بالا (مرغ، تخم مرغ، ماهی)
        - کربوهیدرات مدیریت شده (برنج، سیب زمینی)
        """

# ==========================================
# 3. رابط کاربری وب (Web UI)
# ==========================================
st.title("🏋️‍♂️ مربی هوشمند من (نسخه وب)")
st.info("این نسخه وب بدون نیاز به فیلترشکن کار می‌کند.")

# سایدبار برای ورودی‌ها
with st.sidebar:
    st.header("📝 اطلاعات ورزشکار")
    name = st.text_input("نام کامل")
    birth = st.number_input("سال تولد (شمسی/میلادی)", min_value=1300, max_value=2025, value=1370)
    gender = st.selectbox("جنسیت", ["Male", "Female"])
    height = st.slider("قد (cm)", 140, 210, 175)
    weight = st.slider("وزن (kg)", 35, 230, 75)
    days = st.slider("روزهای تمرین", 1, 7, 3)
    meals = st.selectbox("تعداد وعده", [3, 4, 5, 6])
    sleep = st.slider("ساعت خواب", 4, 12, 7)
    api_key = st.text_input("کلید Gemini AI (اختیاری)", type="password")
    
    btn_process = st.button("✅ دریافت برنامه")

# نمایش خروجی
if btn_process:
    age = BioCalculator.calculate_age(birth)
    if age:
        user_data = {
            'name': name, 'age': age, 'gender': gender,
            'height': height/100, 'weight': weight,
            'days': days, 'meals': meals, 'sleep': sleep
        }
        
        coach = CoachAI(user_data, api_key)
        res = coach.get_plan()
        
        st.success(f"خوش آمدید {name} عزیز (سن: {age})")
        
        # تب‌بندی نتایج
        tab1, tab2, tab3 = st.tabs(["📜 برنامه جامع", "📊 وضعیت بدنی", "📈 نمودارها"])
        
        with tab1:
            st.markdown(res)
            
        with tab2:
            col1, col2 = st.columns(2)
            col1.metric("BMI", f"{coach.bmi:.2f}")
            col2.metric("کالری مورد نیاز (TDEE)", f"{int(coach.tdee)}")
            st.progress(min(coach.bmi/40, 1.0))
            
        # ذخیره داده‌ها
        new_row = {'Date': datetime.now().strftime("%Y-%m-%d"), 'Name': name, 
                   'Weight': weight, 'Height': height, 'BMI': coach.bmi, 'Age': age}
        df_new = pd.DataFrame([new_row])
        
        if os.path.exists(CSV_FILE):
            df_new.to_csv(CSV_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
        else:
            df_new.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
            
        with tab3:
            if os.path.exists(CSV_FILE):
                df = pd.read_csv(CSV_FILE)
                st.write("آمار کاربران ثبت شده:")
                
                fig, ax = plt.subplots(1, 2, figsize=(10, 4))
                ax[0].hist(df['Age'], bins=5, color='skyblue')
                ax[0].set_title('توزیع سنی')
                
                ax[1].scatter(df['Weight'], df['Height'], c='red', alpha=0.5)
                ax[1].set_title('پراکندگی قد و وزن')
                
                st.pyplot(fig)
    else:
        st.error("سال تولد نامعتبر است.")
