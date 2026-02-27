from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# Configure Gemini
GOOGLE_API_KEY = "AIzaSyDse6le5A18A94Z--vuEL3pYAteCeFSnjs"
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize session state with more detailed health profile
if 'health_profile' not in st.session_state:
    st.session_state.health_profile = {
        'goals': 'Lose 10 pounds in 3 months\nImprove cardiovascular health',
        'conditions': 'None',
        'routines': '30-minute walk 3x/week',
        'preferences': 'Vegetarian\nLow carb',
        'restrictions': 'No dairy\nNo nuts',
        'age': '30',
        'gender': 'Female',
        'height': '5\'6"',
        'weight': '150 lbs',
        'activity_level': 'Moderately active'
    }

# Function to get Gemini response with enhanced error handling
def get_gemini_response(input_prompt, image_data=None):
    model = genai.GenerativeModel('gemini-2.5-flash')
    content = [input_prompt]

    if image_data:
        content.extend(image_data)

    try:
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Convert uploaded image to Gemini format
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }]
        return image_parts
    return None

# App layout with professional styling
st.set_page_config(
    page_title="",
    layout="wide",
    page_icon="⚡NutriFlow AI",
    initial_sidebar_state="expanded"
)
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #2E8B57;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4682B4;
        margin-top: 1rem;
    }
    .tab-content {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f9f9f9;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚡NutriFlow AI</div>', unsafe_allow_html=True)
st.markdown("**Empower your health journey with personalized, AI-driven meal planning and nutrition insights.**")

# Sidebar for health profile with advanced fields
with st.sidebar:
    st.markdown('<div class="sub-header">📋 Your Health Profile</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.text_input("Age", value=st.session_state.health_profile['age'])
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state.health_profile['gender']))
        height = st.text_input("Height (e.g., 5'6\")", value=st.session_state.health_profile['height'])
    with col2:
        weight = st.text_input("Weight (e.g., 150 lbs)", value=st.session_state.health_profile['weight'])
        activity_level = st.selectbox("Activity Level", ["Sedentary", "Lightly active", "Moderately active", "Very active"], index=["Sedentary", "Lightly active", "Moderately active", "Very active"].index(st.session_state.health_profile['activity_level']))

    health_goals = st.text_area("Health Goals", value=st.session_state.health_profile['goals'])
    medical_conditions = st.text_area("Medical Conditions", value=st.session_state.health_profile['conditions'])
    fitness_routines = st.text_area("Fitness Routines", value=st.session_state.health_profile['routines'])
    food_preferences = st.text_area("Food Preferences", value=st.session_state.health_profile['preferences'])
    restrictions = st.text_area("Dietary Restrictions", value=st.session_state.health_profile['restrictions'])

    if st.button("Update Profile", use_container_width=True):
        st.session_state.health_profile = {
            'goals': health_goals,
            'conditions': medical_conditions,
            'routines': fitness_routines,
            'preferences': food_preferences,
            'restrictions': restrictions,
            'age': age,
            'gender': gender,
            'height': height,
            'weight': weight,
            'activity_level': activity_level
        }
        st.success("Profile updated successfully!")

# Main content area with enhanced tabs
tab1, tab2, tab3, tab4 = st.tabs(["🍽️ Meal Planning", "🔍 Food Analysis", "💡 Health Insights", "📊 Progress Tracker"])

# ---------- TAB 1 : MEAL PLANNING ----------
with tab1:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">🍽️ Personalized Meal Planning</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Your Current Needs")
        user_input = st.text_area(
            "Describe any specific requirements for your meals",
            placeholder="e.g., I need quick meals for work, or focus on high-protein options"
        )
        meal_duration = st.selectbox("Meal Plan Duration", ["3 Days", "7 Days", "14 Days"], index=1)
        meal_type = st.multiselect("Meal Types", ["Breakfast", "Lunch", "Dinner", "Snacks"], default=["Breakfast", "Lunch", "Dinner", "Snacks"])
    
    with col2:
        st.write("### Your Health Profile Summary")
        st.json({k: v for k, v in st.session_state.health_profile.items() if k in ['goals', 'preferences', 'restrictions']})
    
    if st.button("Generate Personalized Meal Plan", use_container_width=True):
        if not any(st.session_state.health_profile.values()):
            st.warning("Please complete your health profile in the sidebar first.")
        else:
            with st.spinner("Crafting your personalized meal plan..."):
                prompt = f"""
You are a professional nutritionist. Create a highly personalized {meal_duration.lower()} meal plan based on the following detailed health profile:

- Age: {st.session_state.health_profile['age']}
- Gender: {st.session_state.health_profile['gender']}
- Height: {st.session_state.health_profile['height']}
- Weight: {st.session_state.health_profile['weight']}
- Activity Level: {st.session_state.health_profile['activity_level']}
- Health Goals: {st.session_state.health_profile['goals']}
- Medical Conditions: {st.session_state.health_profile['conditions']}
- Fitness Routines: {st.session_state.health_profile['routines']}
- Food Preferences: {st.session_state.health_profile['preferences']}
- Dietary Restrictions: {st.session_state.health_profile['restrictions']}

Additional requirements: {user_input if user_input else "None provided"}
Meal Types: {', '.join(meal_type)}

Provide:
1. A detailed {meal_duration.lower()} meal plan with {', '.join(meal_type).lower()}, including recipes and ingredients.
2. Nutritional breakdown for each day (calories, macros: protein, carbs, fats).
3. Contextual explanations for why each meal was chosen, tailored to the profile.
4. Comprehensive shopping list organized by category (e.g., Produce, Proteins).
5. Preparation tips, time-saving suggestions, and storage advice.
6. Estimated total cost and budget-friendly alternatives.

Format the output professionally with clear headings, bullet points, and tables where appropriate. Ensure the plan is balanced, sustainable, and aligned with health goals.
"""
                response = get_gemini_response(prompt)
                
                st.markdown('<div class="sub-header">Your Personalized Meal Plan</div>', unsafe_allow_html=True)
                st.markdown(response)
                
                st.download_button(
                    label="📥 Download Meal Plan",
                    data=response,
                    file_name="personalized_meal_plan.txt",
                    mime="text/plain",
                    use_container_width=True
                )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- TAB 2 : FOOD ANALYSIS ----------
with tab2:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">🔍 Advanced Food Analysis</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload an image of your food for detailed analysis",
        type=["jpg", "jpeg", "png"]
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Food Image", use_column_width=True)
        
        if st.button("Analyze Food", use_container_width=True):
            with st.spinner("Analyzing your food with AI precision..."):
                image_data = input_image_setup(uploaded_file)
                
                prompt = f"""
You are an expert nutritionist. Analyze this food image in detail, considering the user's profile: {st.session_state.health_profile}.

Provide:
- Estimated calories and macronutrient breakdown (protein, carbs, fats).
- Micronutrient highlights (vitamins, minerals).
- Potential health benefits and any concerns (e.g., allergens, interactions with conditions).
- Portion size recommendations and alternatives.
- Suggestions for integration into a meal plan.

If multiple items, analyze each separately and provide an overall assessment.
"""
                response = get_gemini_response(prompt, image_data)
                
                st.markdown('<div class="sub-header">Food Analysis Results</div>', unsafe_allow_html=True)
                st.markdown(response)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- TAB 3 : HEALTH INSIGHTS ----------
with tab3:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">💡 Expert Health Insights</div>', unsafe_allow_html=True)
    
    health_query = st.text_input(
        "Ask any health or nutrition-related question",
        placeholder="e.g., How can I improve my gut health with my current diet?"
    )
    
    if st.button("Get Expert Insights", use_container_width=True):
        if not health_query:
            st.warning("Please enter a health question.")
        else:
            with st.spinner("Researching and providing science-backed insights..."):
                prompt = f"""
You are a certified nutritionist and health expert. Provide detailed, evidence-based insights on: {health_query}

Incorporate the user's health profile: {st.session_state.health_profile}

Structure your response:
1. Clear, science-backed explanation.
2. Practical, personalized recommendations.
3. Precautions or contraindications.
4. References to studies or guidelines (e.g., from WHO, NIH).
5. Suggested foods, supplements, or lifestyle changes.
6. How it aligns with their meal plan.

Use professional, accessible language.
"""
                response = get_gemini_response(prompt)
                
                st.markdown('<div class="sub-header">Expert Health Insights</div>', unsafe_allow_html=True)
                st.markdown(response)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- TAB 4 : PROGRESS TRACKER ----------
with tab4:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">📊 Progress Tracker</div>', unsafe_allow_html=True)
    
    st.write("Track your meal planning progress and health metrics.")
    
    # Simple progress inputs (can be expanded with charts)
    current_weight = st.number_input("Current Weight (lbs)", value=float(st.session_state.health_profile['weight'].split()[0]) if st.session_state.health_profile['weight'] else 150.0)
    meals_logged = st.number_input("Meals Logged This Week", min_value=0, value=0)
    goals_achieved = st.text_area("Goals Achieved This Week", placeholder="e.g., Lost 2 lbs, completed 5 workouts")
    
    if st.button("Log Progress", use_container_width=True):
        st.success("Progress logged! (In a full app, this would save to a database.)")
        st.write(f"**Summary:** Weight: {current_weight} lbs, Meals: {meals_logged}, Achievements: {goals_achieved}")
    
    # Placeholder for charts
    st.write("### Progress Charts (Placeholder)")
    st.info("Integrate with libraries like Plotly for visual progress tracking.")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("**Professional AI Meal Planner** - Powered by Google Gemini. Consult a healthcare professional for personalized medical advice.")