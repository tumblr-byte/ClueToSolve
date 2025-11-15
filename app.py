import streamlit as st
import json
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from gemini import setup_vertex_ai

# Page configuration
st.set_page_config(
    page_title="ClueToSolve",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful detective theme
def local_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Detective theme colors */
    :root {
        --primary: #1e3a8a;
        --accent: #f97316;
        --success: #10b981;
        --warning: #fbbf24;
        --danger: #ef4444;
        --background: #f0f9ff;
        --dark: #1f2937;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Profile section */
    .profile-section {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
        margin-bottom: 2rem;
        border: 3px solid var(--primary);
    }
    
    .profile-img {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        border: 4px solid var(--accent);
        margin: 0 auto;
    }
    
    .profile-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary);
        margin-top: 0.5rem;
    }
    
    .profile-motto {
        font-size: 0.9rem;
        color: #6b7280;
        font-style: italic;
        margin-top: 0.3rem;
    }

    /* Detective header */
    .detective-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
        animation: fadeIn 0.8s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .detective-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .detective-header p {
        font-size: 1.1rem;
        opacity: 0.95;
    }

    /* Case cards */
    .case-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid var(--primary);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .case-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        border-left-width: 8px;
    }

    .case-card.locked {
        border-left-color: var(--danger);
        opacity: 0.6;
        cursor: not-allowed;
    }
    
    .case-card.locked:hover {
        transform: none;
    }

    .case-card.unlocked {
        border-left-color: var(--success);
    }
    
    .case-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .case-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 0.5rem;
    }
    
    .case-description {
        font-size: 0.95rem;
        color: #6b7280;
        line-height: 1.6;
    }

    /* Hint box - Beautiful and concise */
    .hint-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid var(--warning);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 10px rgba(251, 191, 36, 0.2);
    }
    
    .hint-content {
        color: #92400e;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .hint-header {
        font-weight: 600;
        color: #78350f;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }

    /* Progress indicators */
    .progress-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.3rem;
    }
    
    .progress-complete {
        background: #d1fae5;
        color: #065f46;
    }
    
    .progress-pending {
        background: #fef3c7;
        color: #92400e;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: var(--primary) !important;
        border: 2px solid var(--primary) !important;
    }

    /* Metrics */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-top: 4px solid var(--primary);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6b7280;
        margin-top: 0.3rem;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
    }
    
    /* Question card */
    .question-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Analysis cards */
    .analysis-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 2px solid #bae6fd;
    }
    
    .strength-item {
        background: #d1fae5;
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid var(--success);
    }
    
    .weakness-item {
        background: #fee2e2;
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid var(--danger);
    }
    
    .suspect-item {
        background: #fef3c7;
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid var(--warning);
    }
    
    /* Rank badge */
    .rank-badge {
        display: inline-block;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-size: 2rem;
        font-weight: 700;
        margin: 1rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* Radio buttons */
    .stRadio > label {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 2px solid #e5e7eb;
        transition: all 0.3s;
    }
    
    .stRadio > label:hover {
        border-color: var(--primary);
        background: #f0f9ff;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Initialize session state
def initialize_session_state():
    defaults = {
        'current_page': 'home',
        'current_chapter': None,
        'current_subtopic': None,
        'current_difficulty': 'basic',
        'current_question_index': 0,
        'questions_data': {},
        'responses': [],
        'question_start_time': None,
        'basic_completed': False,
        'intermediate_completed': False,
        'advanced_completed': False,
        'gemini_model': None,
        'username': 'Markat',
        'user_photo': 'default.jpg'
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Initialize Gemini model if not done
    if st.session_state['gemini_model'] is None:
        try:
            st.session_state['gemini_model'] = setup_vertex_ai()
        except Exception as e:
            st.error(f"AI Detective unavailable: {e}")

def show_profile_section():
    """Show user profile section"""
    st.markdown(f"""
    <div class="profile-section">
        <div class="profile-name">🕵️ Detective {st.session_state['username']}</div>
        <div class="profile-motto">💪 Use your strengths to overcome your weaknesses</div>
    </div>
    """, unsafe_allow_html=True)

def get_smart_hint_from_gemini():
    """Generate intelligent hint based on user's previous performance"""
    if st.session_state['gemini_model'] is None:
        return "🤖 AI Detective is taking a coffee break!"

    questions = get_current_questions()
    if not questions or st.session_state['current_question_index'] >= len(questions):
        return "🤔 No question to hint at right now!"

    current_question = questions[st.session_state['current_question_index']]
    responses = st.session_state['responses']
    
    # Analyze previous correct answers
    correct_responses = [r for r in responses if r['is_correct']]
    
    # Find similar topics from previous correct answers
    similar_topics = []
    current_topic = current_question.get('topic', '')
    
    for response in correct_responses:
        prev_topic = response.get('topic', '')
        # Simple similarity check
        if any(word in current_topic.lower() for word in prev_topic.lower().split()):
            similar_topics.append({
                'question_id': response['question_id'],
                'topic': prev_topic
            })
    
    # Build context for Gemini
    hint_context = f"""You're a friendly AI detective helping a 10th grader who's a bit nervous about exams.

Current Question: {current_question['question']}
Topic: {current_question.get('topic', 'Math')}

"""

    if similar_topics:
        hint_context += f"\n✨ They solved similar questions before: {', '.join([f'Q{s['question_id']}' for s in similar_topics[:2]])}"
    
    if correct_responses:
        strong_topics = {}
        for r in correct_responses:
            topic = r.get('topic', 'unknown')
            strong_topics[topic] = strong_topics.get(topic, 0) + 1
        best_topic = max(strong_topics, key=strong_topics.get)
        hint_context += f"\n💪 Their strength: {best_topic}"

    prompt = f"""{hint_context}

Give a SHORT, FRIENDLY hint (2-3 sentences max) using emojis that:
1. Reminds them of a similar question they solved correctly (if any)
2. Connects their strength to this problem
3. Encourages without revealing the answer

Keep it casual, teen-friendly, and motivating! No bullet points, just natural chat."""

    try:
        response = st.session_state['gemini_model'].generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"🤖 Oops! Detective AI is having technical difficulties: {str(e)}"

def show_intermediate_break_page():
    """Show break page after intermediate completion"""
    st.markdown("""
    <div class="detective-header">
        <h1>🎯 Evidence Analyzed!</h1>
        <p>You've mastered the intermediate level! Ready for the final case?</p>
    </div>
    """, unsafe_allow_html=True)

    show_profile_section()

    # Intermediate performance
    inter_responses = [r for r in st.session_state['responses'] if r['difficulty'] == 'intermediate']
    if inter_responses:
        inter_correct = sum(1 for r in inter_responses if r['is_correct'])
        inter_accuracy = inter_correct / len(inter_responses)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(inter_responses)}</div>
                <div class="metric-label">🎯 Evidence Analyzed</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{inter_accuracy*100:.0f}%</div>
                <div class="metric-label">📊 Accuracy Rate</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            avg_time = sum(r['time_spent'] for r in inter_responses) / len(inter_responses)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_time:.0f}s</div>
                <div class="metric-label">⏱️ Avg Time</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏸️ Take a Break", use_container_width=True):
            st.info("💤 Rest up, detective! The final case will be waiting.")
            if st.button("🏠 Return Home"):
                st.session_state['current_page'] = 'home'
                st.rerun()
    
    with col2:
        if st.button("🚨 Crack the Final Case!", type="primary", use_container_width=True):
            st.session_state['current_page'] = 'advanced'
            st.session_state['current_question_index'] = 0
            st.rerun()

def show_basic_break_page():
    """Show break/rest page after basic completion"""
    st.markdown("""
    <div class="detective-header">
        <h1>🕵️ Investigation Checkpoint</h1>
        <p>Basic clues gathered! Take a breather or dive deeper into the case.</p>
    </div>
    """, unsafe_allow_html=True)

    show_profile_section()

    # Basic level stats
    basic_responses = [r for r in st.session_state['responses'] if r['difficulty'] == 'basic']
    if basic_responses:
        basic_correct = sum(1 for r in basic_responses if r['is_correct'])
        basic_accuracy = basic_correct / len(basic_responses)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(basic_responses)}</div>
                <div class="metric-label">🔍 Clues Found</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{basic_accuracy*100:.0f}%</div>
                <div class="metric-label">🎯 Success Rate</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            avg_time = sum(r['time_spent'] for r in basic_responses) / len(basic_responses)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_time:.0f}s</div>
                <div class="metric-label">⚡ Speed</div>
            </div>
            """, unsafe_allow_html=True)

        # Quick analysis
        topics = {}
        for r in basic_responses:
            topic = r['topic']
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(r['is_correct'])

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown("**💪 Your Strengths:**")
            for topic, results in topics.items():
                accuracy = sum(results) / len(results)
                if accuracy >= 0.7:
                    st.markdown(f'<div class="strength-item">✅ {topic} - {accuracy*100:.0f}%</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
            st.markdown("**🎯 Need Practice:**")
            for topic, results in topics.items():
                accuracy = sum(results) / len(results)
                if accuracy < 0.7:
                    st.markdown(f'<div class="weakness-item">⚠️ {topic} - {accuracy*100:.0f}%</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏸️ Take a Break", use_container_width=True):
            st.info("💤 Recharge your detective skills! Come back when ready.")
    
    with col2:
        if st.button("▶️ Continue to Intermediate", type="primary", use_container_width=True):
            st.session_state['current_page'] = 'intermediate'
            st.session_state['current_question_index'] = 0
            st.rerun()

# Main app functions
def load_chapters():
    """Load chapter structure from 1.json"""
    try:
        with open('1.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['chapters']
    except FileNotFoundError:
        st.error("❌ Case files (1.json) not found!")
        return {}

def load_questions_data(chapter, subtopic_key):
    """Load questions for a subtopic"""
    cache_key = f"{chapter}_{subtopic_key}"
    if cache_key in st.session_state['questions_data']:
        return st.session_state['questions_data'][cache_key]

    chapters = load_chapters()
    if chapter in chapters and subtopic_key in chapters[chapter]['subtopics']:
        questions_file = chapters[chapter]['subtopics'][subtopic_key]['questions_file']
        try:
            with open(questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            questions = data['questions']
            st.session_state['questions_data'][cache_key] = questions
            return questions
        except FileNotFoundError:
            st.error(f"❌ Question file {questions_file} not found!")
            return []
    return []

def show_home_page():
    """Display home page with cases"""
    st.markdown("""
    <div class="detective-header">
        <h1>🔍 ClueToSolve</h1>
        <p>A Gamified Learning Journey for Fearless Detectives</p>
        <p>💪 Use your strengths to overcome your weaknesses</p>
    </div>
    """, unsafe_allow_html=True)

    show_profile_section()

    chapters = load_chapters()

    for chapter_name, chapter_data in chapters.items():
        st.markdown(f"### 📚 {chapter_name}")

        cols = st.columns(2)
        for i, (subtopic_key, subtopic_data) in enumerate(chapter_data['subtopics'].items()):
            with cols[i % 2]:
                description = subtopic_data['description']
                
                st.markdown(f"""
                <div class="case-card unlocked">
                    <div class="case-icon">🔍</div>
                    <div class="case-title">{subtopic_key}</div>
                    <div class="case-description">{description}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"🚨 Investigate {subtopic_key}", key=f"{chapter_name}_{subtopic_key}", use_container_width=True):
                    st.session_state['current_chapter'] = chapter_name
                    st.session_state['current_subtopic'] = subtopic_key
                    st.session_state['current_page'] = 'case_briefing'
                    st.session_state['responses'] = []
                    st.session_state['basic_completed'] = False
                    st.session_state['intermediate_completed'] = False
                    st.session_state['advanced_completed'] = False
                    st.rerun()

def show_case_briefing_page():
    """Show case briefing with mission details"""
    if not st.session_state['current_chapter'] or not st.session_state['current_subtopic']:
        st.error("❌ No case selected!")
        if st.button("🏠 Back to Home"):
            st.session_state['current_page'] = 'home'
            st.rerun()
        return

    questions = load_questions_data(st.session_state['current_chapter'], st.session_state['current_subtopic'])
    advanced_questions = [q for q in questions if q['difficulty_level'] == 'advanced']

    if not advanced_questions:
        st.error("❌ No advanced case found!")
        return

    case = advanced_questions[0]
    case_file = case.get('case_file', {})

    st.markdown(f"""
    <div class="detective-header">
        <h1>{case.get('case_title', '🚨 Mystery Case')}</h1>
        <p>{case.get('case_number', 'Case #Unknown')}</p>
    </div>
    """, unsafe_allow_html=True)

    show_profile_section()

    # Case briefing
    st.markdown("### 📄 Case Briefing")
    st.info(case_file.get('briefing', 'No briefing available.'))

    st.markdown("### 🏛️ Crime Scene")
    st.warning(case_file.get('crime_scene', 'No scene description.'))

    if 'evidence_found' in case_file:
        st.markdown("### 🧪 Evidence Found")
        evidence = case_file['evidence_found']
        for key, value in evidence.items():
            st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

    if 'mystery' in case_file:
        st.markdown("### ❓ The Mystery")
        st.error(case_file['mystery'])

    # Mission status
    st.markdown("### 🎯 Investigation Progress")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = "✅ Complete" if st.session_state['basic_completed'] else "🔒 Locked"
        badge_class = "progress-complete" if st.session_state['basic_completed'] else "progress-pending"
        st.markdown(f'<span class="progress-badge {badge_class}">🔍 Basic Clues {status}</span>', unsafe_allow_html=True)
    
    with col2:
        status = "✅ Complete" if st.session_state['intermediate_completed'] else "🔒 Locked"
        badge_class = "progress-complete" if st.session_state['intermediate_completed'] else "progress-pending"
        st.markdown(f'<span class="progress-badge {badge_class}">🔎 Evidence {status}</span>', unsafe_allow_html=True)
    
    with col3:
        status = "✅ Complete" if st.session_state['advanced_completed'] else "🔒 Locked"
        badge_class = "progress-complete" if st.session_state['advanced_completed'] else "progress-pending"
        st.markdown(f'<span class="progress-badge {badge_class}">🚨 Final Case {status}</span>', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Start Investigation", type="primary", use_container_width=True):
            st.session_state['current_difficulty'] = 'basic'
            st.session_state['current_question_index'] = 0
            st.session_state['current_page'] = 'basic'
            st.rerun()

    with col2:
        if st.button("🏠 Back to Headquarters", use_container_width=True):
            st.session_state['current_page'] = 'home'
            st.rerun()

def get_current_questions():
    """Get questions for current difficulty level"""
    questions = load_questions_data(st.session_state['current_chapter'], st.session_state['current_subtopic'])
    return [q for q in questions if q['difficulty_level'] == st.session_state['current_difficulty']]

def show_quiz_page():
    """Enhanced quiz page with smart hints"""
    questions = get_current_questions()
    if not questions:
        st.error("❌ No questions found!")
        if st.button("🔙 Back"):
            st.session_state['current_page'] = 'case_briefing'
            st.rerun()
        return

    difficulty = st.session_state['current_difficulty']
    headers = {
        'basic': "🔍 Gathering Clues",
        'intermediate': "🔎 Analyzing Evidence",
        'advanced': "🚨 Cracking the Case!"
    }

    st.markdown(f"""
    <div class="detective-header">
        <h1>{headers[difficulty]}</h1>
        <p>Question {st.session_state['current_question_index'] + 1} of {len(questions)}</p>
    </div>
    """, unsafe_allow_html=True)

    show_profile_section()

    # Progress bar
    progress = (st.session_state['current_question_index'] + 1) / len(questions)
    st.progress(progress)

    if st.session_state['current_question_index'] < len(questions):
        question = questions[st.session_state['current_question_index']]

        if st.session_state['question_start_time'] is None:
            st.session_state['question_start_time'] = time.time()

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown(f"### Question {st.session_state['current_question_index'] + 1}")
        st.write(question['question'])

        # Handle options
        raw_options = question['options']
        if isinstance(raw_options, dict):
            options = raw_options
            option_keys = list(options.keys())
        elif isinstance(raw_options, list):
            options = {chr(65+i): raw_options[i] for i in range(len(raw_options))}
            option_keys = list(options.keys())
        else:
            options = {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}
            option_keys = ["A", "B", "C", "D"]

        # Check if answered
        has_answered = False
        answer_is_correct = False
        for r in st.session_state['responses']:
            if r['question_id'] == question['id']:
                has_answered = True
                answer_is_correct = r['is_correct']
                break

        if not has_answered:
            selected_label = st.radio(
                "Choose your answer:",
                option_keys,
                format_func=lambda x: f"{x}. {options[x]}",
                key=f"q_{question['id']}"
            )

            if st.button("✅ Submit Answer", type="primary", use_container_width=True):
                if selected_label:
                    save_answer(question, selected_label, options[selected_label])
                    st.rerun()

        else:
            # Show result
            selected_text = ""
            for r in st.session_state['responses']:
                if r['question_id'] == question['id']:
                    selected_text = f"{r['selected_option']}. {r['selected_text']}"
                    break

            st.info(f"**Your Answer:** {selected_text}")

            if answer_is_correct:
                st.success("🎉 Brilliant detective work! Case clue secured!")
            else:
                correct_answer = ""
                try:
                    if question.get('answer'):
                        correct_option = question['answer'].get('correct_option', '')
                        if isinstance(raw_options, dict):
                            correct_answer = f"{correct_option}. {raw_options.get(correct_option, 'Unknown')}"
                        elif isinstance(raw_options, list):
                            index = ord(correct_option.upper()) - ord('A')
                            if 0 <= index < len(raw_options):
                                correct_answer = f"{correct_option}. {raw_options[index]}"
                except:
                    correct_answer = "Unable to determine"

                st.error(f"❌ Not quite, detective!\n\n**Correct Answer:** {correct_answer}")

            # Show explanation
            try:
                if question.get('answer') and question['answer'].get('explanation'):
                    st.markdown("### 📚 Explanation")
                    st.write(question['answer']['explanation'])

                    if question['answer'].get('steps'):
                        st.markdown("### 🔢 Solution Steps")
                        steps = question['answer']['steps']
                        if isinstance(steps, dict):
                            for step_key, step_text in steps.items():
                                st.markdown(f"**{step_key.replace('_', ' ').title()}:** {step_text}")
            except:
                pass

            st.markdown('</div>', unsafe_allow_html=True)

            # Navigation
            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                if st.session_state['current_question_index'] > 0:
                    if st.button("⬅️ Previous", key="prev"):
                        st.session_state['current_question_index'] -= 1
                        st.session_state['question_start_time'] = None
                        st.rerun()

            with col2:
                next_label = "Next ➡️" if st.session_state['current_question_index'] < len(questions) - 1 else "Finish 🎯"
                if st.button(next_label, key="next", type="primary"):
                    if st.session_state['current_question_index'] < len(questions) - 1:
                        st.session_state['current_question_index'] += 1
                        st.session_state['question_start_time'] = None
                        st.rerun()
                    else:
                        complete_difficulty_level()
                        st.rerun()

            with col3:
                if st.button("🔙 Back to Case", key="back_to_case"):
                    st.session_state['current_page'] = 'case_briefing'
                    st.rerun()

        # Smart Gemini hints - ONLY in intermediate level, ONLY after answering at least one question
        if difficulty == 'intermediate':
            answered_in_intermediate = len([r for r in st.session_state['responses'] 
                                           if r['difficulty'] == 'intermediate'])
            
            if answered_in_intermediate > 0 and not has_answered:
                st.markdown("---")
                st.markdown("### 🤖 Need a Detective Hint?")
                
                if st.button("💡 Get Smart Hint", key="get_hint"):
                    with st.spinner("🔍 Analyzing your investigation history..."):
                        hint = get_smart_hint_from_gemini()
                    
                    st.markdown(f"""
                    <div class="hint-box">
                        <div class="hint-header">💡 Detective AI says:</div>
                        <div class="hint-content">{hint}</div>
                    </div>
                    """, unsafe_allow_html=True)

def save_answer(question, selected_label, selected_text):
    """Save answer to session state"""
    question_id = question['id']

    correct_answer = 'A'
    try:
        if question.get('answer') and question['answer'].get('correct_option'):
            correct_answer = question['answer']['correct_option']
    except:
        pass

    is_correct = selected_label == correct_answer
    time_spent = time.time() - st.session_state['question_start_time']

    response = {
        'question_id': question_id,
        'difficulty': question['difficulty_level'],
        'topic': question.get('topic', ''),
        'selected_option': selected_label,
        'selected_text': selected_text,
        'correct_option': correct_answer,
        'is_correct': is_correct,
        'time_spent': time_spent
    }

    # Update or add
    for i, r in enumerate(st.session_state['responses']):
        if r['question_id'] == question_id:
            st.session_state['responses'][i] = response
            return

    st.session_state['responses'].append(response)

def complete_difficulty_level():
    """Handle completion of a difficulty level"""
    difficulty = st.session_state['current_difficulty']

    if difficulty == 'basic':
        st.session_state['basic_completed'] = True
        st.session_state['current_page'] = 'basic_break'
    elif difficulty == 'intermediate':
        st.session_state['intermediate_completed'] = True
        st.session_state['current_page'] = 'intermediate_break'
    elif difficulty == 'advanced':
        st.session_state['advanced_completed'] = True
        st.session_state['current_page'] = 'results'

def calculate_accuracy(responses, difficulty):
    """Calculate accuracy for a difficulty level"""
    relevant = [r for r in responses if r['difficulty'] == difficulty]
    if not relevant:
        return 0.0
    correct = sum(1 for r in relevant if r['is_correct'])
    return correct / len(relevant)

def show_results_page():
    """Beautiful results page with analysis"""
    st.markdown("""
    <div class="detective-header">
        <h1>🎉 Case Solved!</h1>
        <p>Your investigation report is ready, Detective!</p>
    </div>
    """, unsafe_allow_html=True)

    show_profile_section()

    responses = st.session_state['responses']
    
    if not responses:
        st.warning("No responses recorded!")
        return

    total_correct = sum(1 for r in responses if r['is_correct'])
    total_questions = len(responses)
    accuracy = total_correct / total_questions
    avg_time = sum(r['time_spent'] for r in responses) / total_questions

    # Detective Rank
    if accuracy >= 0.9:
        rank = "🥇 Master Detective"
        rank_color = "#ffd700"
    elif accuracy >= 0.8:
        rank = "🥈 Expert Investigator"
        rank_color = "#c0c0c0"
    elif accuracy >= 0.7:
        rank = "🥉 Senior Detective"
        rank_color = "#cd7f32"
    elif accuracy >= 0.6:
        rank = "🎖️ Detective"
        rank_color = "#1e3a8a"
    else:
        rank = "🔰 Apprentice Detective"
        rank_color = "#6b7280"

    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <div class="rank-badge" style="background: {rank_color}; color: white;">
            {rank}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_correct}/{total_questions}</div>
            <div class="metric-label">✅ Cases Solved</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{accuracy*100:.0f}%</div>
            <div class="metric-label">🎯 Accuracy</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_time:.0f}s</div>
            <div class="metric-label">⏱️ Avg Time</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        streak = 0
        for r in reversed(responses):
            if r['is_correct']:
                streak += 1
            else:
                break
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{streak}</div>
            <div class="metric-label">🔥 Current Streak</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Analysis by topic
    topics = {}
    for r in responses:
        topic = r['topic']
        if topic not in topics:
            topics[topic] = {'correct': 0, 'total': 0}
        topics[topic]['total'] += 1
        if r['is_correct']:
            topics[topic]['correct'] += 1

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💪 Your Strengths")
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        strengths_found = False
        for topic, stats in topics.items():
            acc = stats['correct'] / stats['total']
            if acc >= 0.7:
                strengths_found = True
                st.markdown(f'<div class="strength-item">✅ {topic} - {acc*100:.0f}% ({stats["correct"]}/{stats["total"]})</div>', unsafe_allow_html=True)
        if not strengths_found:
            st.info("Keep solving to build your strengths!")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("### 🎯 Needs Practice")
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        weaknesses_found = False
        for topic, stats in topics.items():
            acc = stats['correct'] / stats['total']
            if acc < 0.7:
                weaknesses_found = True
                st.markdown(f'<div class="weakness-item">⚠️ {topic} - {acc*100:.0f}% ({stats["correct"]}/{stats["total"]})</div>', unsafe_allow_html=True)
        if not weaknesses_found:
            st.success("🌟 No weaknesses! You're a star!")
        st.markdown('</div>', unsafe_allow_html=True)

    # Red Herrings (Common Confusion Points)
    st.markdown("### 🚩 Red Herrings (Common Confusion Points)")
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    
    mistake_patterns = {}
    for r in responses:
        if not r['is_correct']:
            key = f"{r['topic']}"
            mistake_patterns[key] = mistake_patterns.get(key, 0) + 1

    if mistake_patterns:
        sorted_mistakes = sorted(mistake_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
        for topic, count in sorted_mistakes:
            st.markdown(f'<div class="suspect-item">🔍 Review {topic} - {count} mistake(s) here</div>', unsafe_allow_html=True)
    else:
        st.success("🎯 No confusion detected! Perfect clarity!")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Performance chart
    if len(responses) > 1:
        st.markdown("### 📊 Investigation Timeline")
        df = pd.DataFrame(responses)
        df['question_num'] = range(1, len(df) + 1)
        df['result'] = df['is_correct'].apply(lambda x: 'Correct ✅' if x else 'Incorrect ❌')
        
        fig = px.scatter(df, x='question_num', y='time_spent', 
                        color='result',
                        color_discrete_map={'Correct ✅': '#10b981', 'Incorrect ❌': '#ef4444'},
                        title="Time Spent per Question",
                        labels={'question_num': 'Question Number', 'time_spent': 'Time (seconds)'})
        st.plotly_chart(fig, use_container_width=True)

    # Recommendations
    st.markdown("### 🎯 Detective Recommendations")
    
    # Load all questions to recommend next case
    questions = load_questions_data(st.session_state['current_chapter'], st.session_state['current_subtopic'])
    advanced_questions = [q for q in questions if q['difficulty_level'] == 'advanced']
    
    # Check if there are more advanced cases
    solved_case_ids = [r['question_id'] for r in responses if r['difficulty'] == 'advanced']
    unsolved_advanced = [q for q in advanced_questions if q['id'] not in solved_case_ids]
    
    if unsolved_advanced:
        st.markdown("### 🚨 Recommended Next Case")
        next_case = unsolved_advanced[0]
        st.markdown(f"""
        <div class="case-card unlocked">
            <div class="case-title">{next_case.get('case_title', 'Mystery Case')}</div>
            <div class="case-description">{next_case.get('case_number', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚨 Solve This Case", type="primary", use_container_width=True):
            # Reset to advanced level
            st.session_state['current_difficulty'] = 'advanced'
            st.session_state['current_question_index'] = advanced_questions.index(next_case)
            st.session_state['current_page'] = 'advanced'
            st.rerun()

    # Recommend other crime scenes (other subtopics)
    st.markdown("### 🔍 Explore Other Crime Scenes")
    chapters = load_chapters()
    current_chapter = st.session_state['current_chapter']
    current_subtopic = st.session_state['current_subtopic']
    
    if current_chapter in chapters:
        other_subtopics = [s for s in chapters[current_chapter]['subtopics'].keys() if s != current_subtopic]
        
        if other_subtopics:
            cols = st.columns(len(other_subtopics))
            for i, subtopic in enumerate(other_subtopics):
                with cols[i]:
                    subtopic_data = chapters[current_chapter]['subtopics'][subtopic]
                    st.markdown(f"""
                    <div class="case-card unlocked">
                        <div class="case-icon">🔍</div>
                        <div class="case-title">{subtopic}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Investigate {subtopic[:15]}...", key=f"rec_{subtopic}"):
                        st.session_state['current_subtopic'] = subtopic
                        st.session_state['current_page'] = 'case_briefing'
                        st.session_state['responses'] = []
                        st.session_state['basic_completed'] = False
                        st.session_state['intermediate_completed'] = False
                        st.session_state['advanced_completed'] = False
                        st.rerun()

    st.markdown("---")

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🏠 Return to Headquarters", use_container_width=True):
            st.session_state['current_page'] = 'home'
            st.session_state['current_chapter'] = None
            st.session_state['current_subtopic'] = None
            st.session_state['responses'] = []
            st.session_state['basic_completed'] = False
            st.session_state['intermediate_completed'] = False
            st.session_state['advanced_completed'] = False
            st.rerun()

    with col2:
        if st.button("📋 Review All Answers", use_container_width=True):
            st.markdown("### 📋 Complete Answer Review")
            for i, r in enumerate(responses, 1):
                status = "✅" if r['is_correct'] else "❌"
                with st.expander(f"Question {i}: {status} {r['topic']}"):
                    st.write(f"**Your answer:** {r['selected_option']}. {r['selected_text']}")
                    st.write(f"**Correct answer:** {r['correct_option']}")
                    st.write(f"**Time spent:** {r['time_spent']:.1f}s")
                    st.write(f"**Result:** {'Correct!' if r['is_correct'] else 'Incorrect'}")

# Main app routing
def main():
    initialize_session_state()

    if st.session_state['current_page'] == 'home':
        show_home_page()
    elif st.session_state['current_page'] == 'case_briefing':
        show_case_briefing_page()
    elif st.session_state['current_page'] == 'basic_break':
        show_basic_break_page()
    elif st.session_state['current_page'] == 'intermediate_break':
        show_intermediate_break_page()
    elif st.session_state['current_page'] in ['basic', 'intermediate', 'advanced']:
        show_quiz_page()
    elif st.session_state['current_page'] == 'results':
        show_results_page()

if __name__ == "__main__":
    main()

