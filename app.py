import streamlit as st
import pickle
import time
from streamlit_lottie import st_lottie
import json
import requests


# --- Load Lottie Animations ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_healthy = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_5njp3vgg.json")
lottie_warning = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_gn0to0lr.json")

# --- Custom CSS for Modern Dark Theme ---
st.markdown("""
<style>
    :root {
        --primary: #52fab7;
        --secondary: #e0f0ea;
        --bg: #232d36;
        --card-bg: #1a1d24;
    }

    .stApp {
        background-color: var(--bg);
        color: white;
    }

    .st-bb, .st-at, .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj {
        background-color: var(--card-bg) !important;
    }

    .stSlider [data-baseweb="slider"] {
        background-color: var(--primary) !important;
    }

    .st-b7 {
        color: var(--primary) !important;
    }

    .metric-card {
        background: linear-gradient(135deg, #2c3e50 0%, #1a1d24 100%);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        border-left: 4px solid var(--primary);
        margin: 10px 0;
    }

    .input-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        color: #fff;
    }

    .risk-high {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        animation: pulse 2s infinite;
    }

    .risk-low {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.03); }
        100% { transform: scale(1); }
    }

    .stButton>button {
        background: linear-gradient(135deg, var(--primary) 0%, #4a934a 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(110, 181, 47, 0.3);
    }
</style>
""", unsafe_allow_html=True)


# --- Load Model ---
@st.cache_resource
def load_model():
    return pickle.load(open('diabetes_model.pkl', 'rb'))


model = load_model()

# --- App Header ---
st.title("🩺 Diabetes Risk Assessment")
st.subheader("Enter your health metrics to evaluate diabetes risk")

# --- Animated Input Section ---
with st.container():
    col1, col2 = st.columns([1, 1])

    with col1:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.header("Personal Metrics")

            pregnancies = st.slider("Pregnancies", 0, 20, 1,
                                    help="Number of times pregnant")
            age = st.slider("Age", 0, 100, 25)
            bmi = st.slider("BMI", 0.0, 70.0, 25.0, step=0.1,
                            help="Body Mass Index")
            dpf = st.slider("Diabetes Pedigree", 0.0, 3.0, 0.5, step=0.01,
                            help="Genetic predisposition")
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.header("Biochemical Metrics")
            glucose = st.slider("Glucose (mg/dL)", 0, 200, 100,
                                help="Plasma glucose concentration")
            bp = st.slider("Blood Pressure (mmHg)", 0, 130, 70,
                           help="Diastolic blood pressure")
            skin_thickness = st.slider("Skin Thickness (mm)", 0, 100, 20,
                                       help="Triceps skinfold thickness")
            insulin = st.slider("Insulin (μU/mL)", 0, 300, 80,
                                help="2-Hour serum insulin")
            st.markdown('</div>', unsafe_allow_html=True)

# --- Prediction Button ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    predict_btn = st.button("🔍 Analyze Diabetes Risk",
                            use_container_width=True,
                            key="predict_button")

# --- Results Section ---
if predict_btn:
    with st.spinner('Analyzing your health profile...'):
        time.sleep(2)  # Simulate processing time

        input_data = [[pregnancies, glucose, bp, skin_thickness, insulin, bmi, dpf, age]]
        prediction = model.predict(input_data)[0]
        probability = model.predict_proba(input_data)[0][1] * 100

        st.markdown("---")

        if prediction == 1:
            risk_class = "risk-high"
            animation = lottie_warning
            message = "⚠️ High Diabetes Risk Detected"
            advice = "Please consult a healthcare professional for comprehensive screening and advice."
        else:
            risk_class = "risk-low"
            animation = lottie_healthy
            message = "✅ Low Diabetes Risk"
            advice = "Maintain healthy habits with regular check-ups to stay low-risk."

        # Animated Result Card
        with st.container():
            st.markdown(f'<div class="metric-card {risk_class}">', unsafe_allow_html=True)

            col1, col2 = st.columns([1, 2])
            with col1:
                if animation:
                    st_lottie(animation, height=150, key="result_animation")

            with col2:
                st.markdown(f"<h2 style='color: white;'>{message}</h2>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div style='display: flex; justify-content: space-between; color: white; font-size: 18px;'>
                        <span>Risk Probability</span>
                        <span>{probability:.1f}%</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.caption(advice)

            st.markdown('</div>', unsafe_allow_html=True)

        # Health Score Visualization
        st.progress(int(probability),
                    text=f"Your Diabetes Risk Score: {probability:.1f}%")

        # Risk Factors Analysis
        with st.expander("📊 Understand Your Risk Factors"):
            risk_factors = {
                "High Glucose (>140 mg/dL)": glucose > 140,
                "High BMI (>30)": bmi > 30,
                "Age >45": age > 45,
                "High Blood Pressure (>90 mmHg)": bp > 90
            }

            for factor, is_risk in risk_factors.items():
                st.write(f"{'🔴' if is_risk else '🟢'} {factor}")

            st.info("Addressing these factors can significantly reduce your diabetes risk")

# --- Footer ---
st.markdown("---")
st.caption(
    "ℹ️ This tool provides preliminary assessment only. Always consult healthcare professionals for medical advice.")

# --- Sidebar for Additional Info ---
with st.sidebar:
    st.header("About This Tool")
    st.write("This AI-powered analyzer evaluates your diabetes risk using machine learning trained on clinical data.")
    st.markdown("""
    **Healthy Ranges:**
    - Glucose: <140 mg/dL
    - BMI: 18.5-24.9
    - BP: <120/80 mmHg
    """)