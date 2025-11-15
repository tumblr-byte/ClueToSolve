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

# Custom CSS for clean, professional design
def local_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Clean background */
    .main {
        background-color: #f8fafc;
    }
    
    .block-container {
        padding: 2rem 3rem;
        max-width: 1200px;
    }

    /* Professional Navigation Bar */
    .nav-bar {
        background: white;
        padding: 1rem 2rem;
        border-bottom: 1px solid #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: -2rem -3rem 2rem -3rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .nav-left {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo-img {
        width: 40px;
        height: 40px;
        border-radius: 8px;
    }
    
    .app-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
    }
    
    .nav-right {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .user-profile {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 1rem;
        background: #f1f5f9;
        border-radius: 8px;
    }
    
    .user-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        border: 2px solid #3b82f6;
    }
    
    .user-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: #334155;
    }

    /* Page Header */
    .page-header {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
    }
    
    .page-header h1 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }
    
    .page-header p {
        font-size: 1rem;
        margin: 0;
        opacity: 0.9;
    }
    
    .motto {
        background: #fef3c7;
        color: #92400e;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        margin-bottom: 2rem;
        border-left: 4px solid #f59e0b;
    }

    /* Case Cards */
    .case-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
        transition: all 0.2s;
    }
    
    .case-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    }
    
    .case-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .case-description {
        font-size: 0.9rem;
        color: #64748b;
        line-height: 1.6;
    }

    /* Hint Box */
    .hint-box {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .hint-content {
        color: #78350f;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* Progress Badge */
    .progress-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    .badge-complete {
        background: #d1fae5;
        color: #065f46;
    }
    
    .badge-pending {
        background: #fef3c7;
        color: #92400e;
    }
    
    .badge-locked {
        background: #f3f4f6;
        color: #6b7280;
    }

    /* Metric Cards */
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 0.25rem;
    }

    /* Buttons */
    .stButton > button {
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }

    .stButton > button:hover {
        background: #2563eb !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }

    /* Analysis Cards */
    .analysis-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .strength-item {
        background: #d1fae5;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: #065f46;
        font-size: 0.9rem;
    }
    
    .weakness-item {
        background: #fee2e2;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: #991b1b;
        font-size: 0.9rem;
    }
    
    .suspect-item {
        background: #fef3c7;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: #92400e;
        font-size: 0.9rem;
    }
    
    /* Rank Badge */
    .rank-badge {
        display: inline-block;
        padding: 1.5rem 2.5rem;
        border-radius: 12px;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 1rem 0;
    }
    
    /* Question Card */
    .question-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: #3b82f6 !important;
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
        'username': 'Markat'
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state['gemini_model'] is None:
        try:
            st.session_state['gemini_model'] = setup_vertex_ai()
        except Exception as e:
            pass

def show_navigation():
    """Show professional navigation bar"""
    # Try to load images, fallback to emoji if not found
    try:
        from PIL import Image
        import os
        
        logo_html = ""
        if os.path.exists('logo.png'):
            logo = Image.open('logo.png')
            st.sidebar.image(logo, width=1)  # Hidden trick to load image
            logo_html = '<img src="logo.png" class="logo-img" alt="Logo">'
        else:
            logo_html = '<div style="font-size: 2rem;">🔍</div>'
        
        avatar_html = ""
        if os.path.exists('default.jpg'):
            avatar = Image.open('default.jpg')
            st.sidebar.image(avatar, width=1)  # Hidden trick
            avatar_html = '<img src="default.jpg" class="user-avatar" alt="Profile">'
        else:
            avatar_html = '<div style="width: 36px; height: 36px; border-radius: 50%; background: #3b82f6; color: white; display: flex; align-items: center; justify-content: center; font-weight: 600;">M</div>'
    except:
        logo_html = '<div style="font-size: 2rem;">🔍</div>'
        avatar_html = '<div style="width: 36px; height: 36px; border-radius: 50%; background: #3b82f6; color: white; display: flex; align-items: center; justify-content: center; font-weight: 600;">M</div>'
    
    st.markdown(f"""
    <div class="nav-bar">
        <div class="nav-left">
            {logo_html}
            <h1 class="app-title">ClueToSolve</h1>
        </div>
        <div class="nav-right">
            <div class="user-profile">
                {avatar_html}
                <span class="user-name">Detective {st.session_state['username']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_motto():
    """Show motto banner"""
    st.markdown("""
    <div class="motto">
        💪 Use your strengths to overcome your weaknesses
    </div>
    """, unsafe_allow_html=True)

def get_smart_hint_from_gemini():
    """Generate intelligent hint based on previous performance"""
    if st.session_state['gemini_model'] is None:
        return "🤖 Detective AI is currently unavailable."

    questions = get_current_questions()
    if not questions or st.session_state['current_question_index'] >= len(questions):
        return "🤔 No clue to investigate right now."

    current_question = questions[st.session_state['current_question_index']]
    responses = st.session_state['responses']
    
    correct_responses = [r for r in responses if r['is_correct']]
    
    similar_topics = []
    current_topic = current_question.get('topic', '')
    
    for response in correct_responses:
        prev_topic = response.get('topic', '')
        if any(word in current_topic.lower() for word in prev_topic.lower().split()):
            similar_topics.append({
                'question_id': response['question_id'],
                'topic': prev_topic
            })
    
    hint_context = f"""You're a friendly detective mentor helping a nervous 10th grader.

Current Investigation: {current_question['question']}
Topic: {current_question.get('topic', 'Math')}

"""

    if similar_topics:
        similar_q_ids = ', '.join([f"Q{s['question_id']}" for s in similar_topics[:2]])
        hint_context += f"\n✨ They cracked similar cases: {similar_q_ids}"
    
    if correct_responses:
        strong_topics = {}
        for r in correct_responses:
            topic = r.get('topic', 'unknown')
            strong_topics[topic] = strong_topics.get(topic, 0) + 1
        best_topic = max(strong_topics, key=strong_topics.get)
        hint_context += f"\n💪 Their best skill: {best_topic}"

    prompt = f"""{hint_context}

Give a SHORT, CASUAL hint (2-3 sentences) with emojis that:
1. Reminds them of a similar case they solved
2. Shows how their strength helps here
3. Encourages without revealing the answer

Keep it friendly and natural. No bullet points."""

    try:
        response = st.session_state['gemini_model'].generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "🤖 Detective AI is gathering evidence..."

def load_chapters():
    """Load chapter structure from 1.json"""
    try:
        with open('1.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['chapters']
    except:
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
        except:
            return []
    return []

def get_current_questions():
    """Get questions for current difficulty level"""
    questions = load_questions_data(st.session_state['current_chapter'], st.session_state['current_subtopic'])
    return [q for q in questions if q['difficulty_level'] == st.session_state['current_difficulty']]

def show_home_page():
    """Display home page with cases"""
    show_navigation()
    
    st.markdown("""
    <div class="page-header">
        <h1>🕵️ Welcome, Detective!</h1>
        <p>Choose your case and start the investigation</p>
    </div>
    """, unsafe_allow_html=True)

    show_motto()

    chapters = load_chapters()

    for chapter_name, chapter_data in chapters.items():
        st.markdown(f"### 📁 {chapter_name}")

        cols = st.columns(2)
        for i, (subtopic_key, subtopic_data) in enumerate(chapter_data['subtopics'].items()):
            with cols[i % 2]:
                description = subtopic_data['description']
                
                st.markdown(f"""
                <div class="case-card">
                    <div class="case-title">🔍 {subtopic_key}</div>
                    <div class="case-description">{description}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Investigate", key=f"{chapter_name}_{subtopic_key}", use_container_width=True):
                    st.session_state['current_chapter'] = chapter_name
                    st.session_state['current_subtopic'] = subtopic_key
                    st.session_state['current_page'] = 'case_briefing'
                    st.session_state['responses'] = []
                    st.session_state['basic_completed'] = False
                    st.session_state['intermediate_completed'] = False
                    st.session_state['advanced_completed'] = False
                    st.rerun()

def show_case_briefing_page():
    """Show case briefing"""
    show_navigation()
    
    if not st.session_state['current_chapter'] or not st.session_state['current_subtopic']:
        st.error("No case selected!")
        if st.button("Back to Home"):
            st.session_state['current_page'] = 'home'
            st.rerun()
        return

    questions = load_questions_data(st.session_state['current_chapter'], st.session_state['current_subtopic'])
    advanced_questions = [q for q in questions if q['difficulty_level'] == 'advanced']

    if not advanced_questions:
        st.error("No case file found!")
        return

    case = advanced_questions[0]
    case_file = case.get('case_file', {})

    st.markdown(f"""
    <div class="page-header">
        <h1>{case.get('case_title', '🚨 Mystery Case')}</h1>
        <p>{case.get('case_number', 'Case #Unknown')}</p>
    </div>
    """, unsafe_allow_html=True)

    show_motto()

    st.markdown("### 📄 Case Briefing")
    st.info(case_file.get('briefing', 'No briefing available.'))

    st.markdown("### 🏛️ Crime Scene")
    st.warning(case_file.get('crime_scene', 'No scene description.'))

    if 'evidence_found' in case_file:
        st.markdown("### 🧪 Evidence")
        evidence = case_file['evidence_found']
        for key, value in evidence.items():
            st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

    if 'mystery' in case_file:
        st.markdown("### ❓ The Mystery")
        st.error(case_file['mystery'])

    st.markdown("### 🎯 Investigation Progress")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state['basic_completed']:
            st.markdown('<span class="progress-badge badge-complete">✅ Clues Gathered</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="progress-badge badge-pending">🔍 Gather Clues</span>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state['intermediate_completed']:
            st.markdown('<span class="progress-badge badge-complete">✅ Evidence Analyzed</span>', unsafe_allow_html=True)
        elif st.session_state['basic_completed']:
            st.markdown('<span class="progress-badge badge-pending">🔎 Analyze Evidence</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="progress-badge badge-locked">🔒 Locked</span>', unsafe_allow_html=True)
    
    with col3:
        if st.session_state['advanced_completed']:
            st.markdown('<span class="progress-badge badge-complete">✅ Case Solved</span>', unsafe_allow_html=True)
        elif st.session_state['intermediate_completed']:
            st.markdown('<span class="progress-badge badge-pending">🚨 Solve Case</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="progress-badge badge-locked">🔒 Locked</span>', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Start Investigation", type="primary", use_container_width=True):
            st.session_state['current_difficulty'] = 'basic'
            st.session_state['current_question_index'] = 0
            st.session_state['current_page'] = 'basic'
            st.rerun()

    with col2:
        if st.button("🏠 Back", use_container_width=True):
            st.session_state['current_page'] = 'home'
            st.rerun()

def show_basic_break_page():
    """Show break after basic level"""
    show_navigation()
    
    st.markdown("""
    <div class="page-header">
        <h1>🕵️ Investigation Checkpoint</h1>
        <p>Clues gathered! Ready to analyze evidence?</p>
    </div>
    """, unsafe_allow_html=True)

    show_motto()

    basic_responses = [r for r in st.session_state['responses'] if r['difficulty'] == 'basic']
    if basic_responses:
        basic_correct = sum(1 for r in basic_responses if r['is_correct'])
        basic_accuracy = basic_correct / len(basic_responses)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(basic_responses)}</div>
                <div class="metric-label">Clues Found</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{basic_accuracy*100:.0f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            avg_time = sum(r['time_spent'] for r in basic_responses) / len(basic_responses)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_time:.0f}s</div>
                <div class="metric-label">Avg Time</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏸️ Take a Break", use_container_width=True):
            st.info("Take your time! Come back when ready.")
    
    with col2:
        if st.button("▶️ Continue", type="primary", use_container_width=True):
            st.session_state['current_difficulty'] = 'intermediate'
            st.session_state['current_question_index'] = 0
            st.session_state['current_page'] = 'intermediate'
            st.rerun()

def show_intermediate_break_page():
    """Show break after intermediate level"""
    show_navigation()
    
    st.markdown("""
    <div class="page-header">
        <h1>🎯 Evidence Analyzed!</h1>
        <p>Ready for the final case?</p>
    </div>
    """, unsafe_allow_html=True)

    show_motto()

    inter_responses = [r for r in st.session_state['responses'] if r['difficulty'] == 'intermediate']
    if inter_responses:
        inter_correct = sum(1 for r in inter_responses if r['is_correct'])
        inter_accuracy = inter_correct / len(inter_responses)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(inter_responses)}</div>
                <div class="metric-label">Evidence Analyzed</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{inter_accuracy*100:.0f}%</div>
                <div class="metric-label">Accuracy</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            avg_time = sum(r['time_spent'] for r in inter_responses) / len(inter_responses)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_time:.0f}s</div>
                <div class="metric-label">Avg Time</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏸️ Take a Break", use_container_width=True):
            st.info("Rest up! The final case awaits.")
    
    with col2:
        if st.button("🚨 Solve Final Case", type="primary", use_container_width=True):
            st.session_state['current_difficulty'] = 'advanced'
            st.session_state['current_question_index'] = 0
            st.session_state['current_page'] = 'advanced'
            st.rerun()

def save_answer(question, selected_label, selected_text):
    """Save answer"""
    correct_answer = 'A'
    try:
        if question.get('answer') and question['answer'].get('correct_option'):
            correct_answer = question['answer']['correct_option']
    except:
        pass

    is_correct = selected_label == correct_answer
    time_spent = time.time() - st.session_state['question_start_time']

    response = {
        'question_id': question['id'],
        'difficulty': question['difficulty_level'],
        'topic': question.get('topic', ''),
        'selected_option': selected_label,
        'selected_text': selected_text,
        'correct_option': correct_answer,
        'is_correct': is_correct,
        'time_spent': time_spent
    }

    for i, r in enumerate(st.session_state['responses']):
        if r['question_id'] == question['id']:
            st.session_state['responses'][i] = response
            return

    st.session_state['responses'].append(response)

def complete_difficulty_level():
    """Handle completion"""
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

def show_quiz_page():
    """Quiz page"""
    show_navigation()
    
    questions = get_current_questions()
    if not questions:
        st.error("No questions found!")
        return

    difficulty = st.session_state['current_difficulty']
    headers = {
        'basic': "🔍 Gathering Clues",
        'intermediate': "🔎 Analyzing Evidence",
        'advanced': "🚨 Solving the Case"
    }

    st.markdown(f"""
    <div class="page-header">
        <h1>{headers[difficulty]}</h1>
        <p>Question {st.session_state['current_question_index'] + 1} of {len(questions)}</p>
    </div>
    """, unsafe_allow_html=True)

    show_motto()

    progress = (st.session_state['current_question_index'] + 1) / len(questions)
    st.progress(progress)

    if st.session_state['current_question_index'] < len(questions):
        question = questions[st.session_state['current_question_index']]

        if st.session_state['question_start_time'] is None:
            st.session_state['question_start_time'] = time.time()

        st.markdown('<div class="question-card">', unsafe_allow_html=True)
        st.markdown(f"### Question {st.session_state['current_question_index'] + 1}")
        st.write(question['question'])

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

            if st.button("✅ Submit", type="primary", use_container_width=True):
                if selected_label:
                    save_answer(question, selected_label, options[selected_label])
                    st.rerun()

        else:
            selected_text = ""
            for r in st.session_state['responses']:
                if r['question_id'] == question['id']:
                    selected_text = f"{r['selected_option']}. {r['selected_text']}"
                    break

            st.info(f"**Your Answer:** {selected_text}")

            if answer_is_correct:
                st.success("✅ Correct! Case clue secured!")
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

                st.error(f"❌ Not quite!\n\n**Correct Answer:** {correct_answer}")

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

            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                if st.session_state['current_question_index'] > 0:
                    if st.button("⬅️ Previous", key="prev"):
                        st.session_state['current_question_index'] -= 1
                        st.session_state['question_start_time'] = None
                        st.rerun()

            with col2:
                next_label = "Next ➡️" if st.session_state['current_question_index'] < len(questions) - 1 else "Finish"
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

        # Smart hints - ONLY in intermediate, ONLY after answering at least one
        if difficulty == 'intermediate' and not has_answered:
            answered_in_intermediate = len([r for r in st.session_state['responses'] 
                                           if r['difficulty'] == 'intermediate'])
            
            if answered_in_intermediate > 0:
                st.markdown("---")
                st.markdown("### 🤖 Need a Hint?")
                
                if st.button("💡 Get Detective Hint", key="get_hint"):
                    with st.spinner("Analyzing your investigation..."):
                        hint = get_smart_hint_from_gemini()
                    
                    st.markdown(f"""
                    <div class="hint-box">
                        <div class="hint-content">{hint}</div>
                    </div>
                    """, unsafe_allow_html=True)

def get_gemini_analysis(responses, topics):
    """Get AI analysis of strengths, weaknesses, and red herrings"""
    if st.session_state['gemini_model'] is None:
        return {
            'strengths_text': "Keep solving cases to discover your detective powers! 🌟",
            'weaknesses_text': "Practice makes perfect! The more cases you solve, the stronger you'll become. 💪",
            'red_herrings_text': "No tricky patterns yet - you're doing great! Keep investigating! 🔍"
        }
    
    # Prepare data for analysis
    strengths = []
    weaknesses = []
    mistakes = {}
    
    for topic, stats in topics.items():
        acc = stats['correct'] / stats['total']
        if acc >= 0.7:
            strengths.append(f"{topic} ({acc*100:.0f}%)")
        elif acc < 0.7:
            weaknesses.append(f"{topic} ({acc*100:.0f}%)")
    
    for r in responses:
        if not r['is_correct']:
            topic = r['topic']
            mistakes[topic] = mistakes.get(topic, 0) + 1
    
    # Create prompts for Gemini
    prompt = f"""You're a friendly detective mentor talking to a nervous 10th grader who just solved math problems.

Results:
- Total questions: {len(responses)}
- Correct: {sum(1 for r in responses if r['is_correct'])}
- Topics where they did well (70%+): {', '.join(strengths) if strengths else 'Still building'}
- Topics needing practice (<70%): {', '.join(weaknesses) if weaknesses else 'None'}
- Common mistake areas: {', '.join([f"{k} ({v} mistakes)" for k, v in sorted(mistakes.items(), key=lambda x: x[1], reverse=True)[:3]]) if mistakes else 'None'}

Write THREE SHORT sections (2-3 sentences each, use emojis, be encouraging):

1. STRENGTHS: Celebrate what they're good at in a fun way
2. PRACTICE AREAS: Gently suggest what to work on, connect to their strengths
3. RED HERRINGS: Explain confusing patterns they fell for (if any) in simple terms

Keep it super friendly, use simple words, and make them feel good! Format as:
STRENGTHS: [text]
PRACTICE: [text]
RED_HERRINGS: [text]"""

    try:
        response = st.session_state['gemini_model'].generate_content(prompt)
        text = response.text.strip()
        
        # Parse response
        result = {
            'strengths_text': "Great detective work! 🌟",
            'weaknesses_text': "Keep practicing! 💪",
            'red_herrings_text': "Stay alert for tricky clues! 🔍"
        }
        
        if "STRENGTHS:" in text:
            strengths_part = text.split("STRENGTHS:")[1].split("PRACTICE:")[0].strip()
            result['strengths_text'] = strengths_part
        
        if "PRACTICE:" in text:
            practice_part = text.split("PRACTICE:")[1].split("RED_HERRINGS:")[0].strip()
            result['weaknesses_text'] = practice_part
        
        if "RED_HERRINGS:" in text:
            red_part = text.split("RED_HERRINGS:")[1].strip()
            result['red_herrings_text'] = red_part
        
        return result
        
    except Exception as e:
        return {
            'strengths_text': "You're building your detective skills! Every case makes you stronger! 🌟",
            'weaknesses_text': "Practice the tough topics - even the best detectives need training! 💪",
            'red_herrings_text': "Watch out for tricky questions - they're testing your sharp mind! 🔍"
        }

def calculate_accuracy(responses, difficulty):
    """Calculate accuracy"""
    relevant = [r for r in responses if r['difficulty'] == difficulty]
    if not relevant:
        return 0.0
    correct = sum(1 for r in relevant if r['is_correct'])
    return correct / len(relevant)

def show_results_page():
    """Results page with AI-powered analysis"""
    show_navigation()
    
    st.markdown("""
    <div class="page-header">
        <h1>🎉 Case Closed!</h1>
        <p>Investigation complete - Here's your report</p>
    </div>
    """, unsafe_allow_html=True)

    show_motto()

    responses = st.session_state['responses']
    
    if not responses:
        st.warning("No evidence collected!")
        return

    total_correct = sum(1 for r in responses if r['is_correct'])
    total_questions = len(responses)
    accuracy = total_correct / total_questions
    avg_time = sum(r['time_spent'] for r in responses) / total_questions

    # Calculate by difficulty
    basic_responses = [r for r in responses if r['difficulty'] == 'basic']
    inter_responses = [r for r in responses if r['difficulty'] == 'intermediate']
    advanced_responses = [r for r in responses if r['difficulty'] == 'advanced']
    
    basic_correct = sum(1 for r in basic_responses if r['is_correct'])
    inter_correct = sum(1 for r in inter_responses if r['is_correct'])
    advanced_correct = sum(1 for r in advanced_responses if r['is_correct'])

    # Detective Rank
    if accuracy >= 0.9:
        rank = "🥇 Master Detective"
        rank_color = "#fbbf24"
    elif accuracy >= 0.8:
        rank = "🥈 Expert Detective"
        rank_color = "#94a3b8"
    elif accuracy >= 0.7:
        rank = "🥉 Senior Detective"
        rank_color = "#fb923c"
    elif accuracy >= 0.6:
        rank = "🎖️ Detective"
        rank_color = "#3b82f6"
    else:
        rank = "🔰 Junior Detective"
        rank_color = "#64748b"

    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <div class="rank-badge" style="background: {rank_color}; color: white;">
            {rank}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats - Show by difficulty level
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{basic_correct}/{len(basic_responses)}</div>
            <div class="metric-label">🔍 Clues Found</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{inter_correct}/{len(inter_responses)}</div>
            <div class="metric-label">🔎 Evidence Analyzed</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{advanced_correct}/{len(advanced_responses)}</div>
            <div class="metric-label">🚨 Cases Solved</div>
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
            <div class="metric-label">🔥 Streak</div>
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

    # Get AI Analysis
    with st.spinner("🤖 Detective AI is analyzing your investigation..."):
        ai_analysis = get_gemini_analysis(responses, topics)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💪 Your Strengths")
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        
        # Show AI analysis
        st.markdown(f'<div class="strength-item">{ai_analysis["strengths_text"]}</div>', unsafe_allow_html=True)
        
        # Show data
        strengths_found = False
        for topic, stats in topics.items():
            acc = stats['correct'] / stats['total']
            if acc >= 0.7:
                strengths_found = True
                st.markdown(f'<div class="strength-item">✅ {topic}: {acc*100:.0f}% ({stats["correct"]}/{stats["total"]})</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("### 🎯 Practice These")
        st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
        
        # Show AI analysis
        st.markdown(f'<div class="weakness-item">{ai_analysis["weaknesses_text"]}</div>', unsafe_allow_html=True)
        
        # Show data
        weaknesses_found = False
        for topic, stats in topics.items():
            acc = stats['correct'] / stats['total']
            if acc < 0.7:
                weaknesses_found = True
                st.markdown(f'<div class="weakness-item">⚠️ {topic}: {acc*100:.0f}% ({stats["correct"]}/{stats["total"]})</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Red Herrings with AI explanation
    st.markdown("### 🚩 Red Herrings (Confusion Points)")
    st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
    
    # Show AI analysis first
    st.markdown(f'<div class="suspect-item">{ai_analysis["red_herrings_text"]}</div>', unsafe_allow_html=True)
    
    # Show data
    mistake_patterns = {}
    for r in responses:
        if not r['is_correct']:
            key = f"{r['topic']}"
            mistake_patterns[key] = mistake_patterns.get(key, 0) + 1

    if mistake_patterns:
        sorted_mistakes = sorted(mistake_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
        for topic, count in sorted_mistakes:
            st.markdown(f'<div class="suspect-item">🔍 {topic}: {count} mistake(s) - Review this topic!</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Charts
    if len(responses) > 1:
        st.markdown("### 📈 Investigation Timeline")
        df = pd.DataFrame(responses)
        df['question_num'] = range(1, len(df) + 1)
        df['result'] = df['is_correct'].apply(lambda x: 'Correct' if x else 'Incorrect')
        
        fig = px.scatter(df, x='question_num', y='time_spent', 
                        color='result',
                        color_discrete_map={'Correct': '#10b981', 'Incorrect': '#ef4444'},
                        title="Time Spent per Question")
        fig.update_layout(
            xaxis_title="Question Number",
            yaxis_title="Time (seconds)",
            plot_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Accuracy by topic chart
        if topics:
            topic_df = pd.DataFrame([
                {'Topic': topic, 'Accuracy': stats['correct']/stats['total']*100}
                for topic, stats in topics.items()
            ])
            
            fig2 = px.bar(topic_df, x='Topic', y='Accuracy',
                         title="Accuracy by Topic",
                         color='Accuracy',
                         color_continuous_scale=['#ef4444', '#fbbf24', '#10b981'])
            fig2.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig2, use_container_width=True)

    # Recommendations
    st.markdown("### 🎯 Recommendations")
    
    questions = load_questions_data(st.session_state['current_chapter'], st.session_state['current_subtopic'])
    advanced_questions = [q for q in questions if q['difficulty_level'] == 'advanced']
    
    solved_case_ids = [r['question_id'] for r in responses if r['difficulty'] == 'advanced']
    unsolved_advanced = [q for q in advanced_questions if q['id'] not in solved_case_ids]
    
    if unsolved_advanced:
        st.markdown("### 🚨 Next Case in This Investigation")
        next_case = unsolved_advanced[0]
        st.markdown(f"""
        <div class="case-card">
            <div class="case-title">{next_case.get('case_title', 'Mystery Case')}</div>
            <div class="case-description">{next_case.get('case_number', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚨 Solve This Case", type="primary", use_container_width=True):
            st.session_state['current_difficulty'] = 'advanced'
            st.session_state['current_question_index'] = advanced_questions.index(next_case)
            st.session_state['current_page'] = 'advanced'
            st.rerun()

    # Other cases
    st.markdown("### 🔍 Explore Other Cases")
    chapters = load_chapters()
    current_chapter = st.session_state['current_chapter']
    current_subtopic = st.session_state['current_subtopic']
    
    if current_chapter in chapters:
        other_subtopics = [s for s in chapters[current_chapter]['subtopics'].keys() if s != current_subtopic]
        
        if other_subtopics:
            cols = st.columns(min(len(other_subtopics), 3))
            for i, subtopic in enumerate(other_subtopics[:3]):
                with cols[i]:
                    subtopic_data = chapters[current_chapter]['subtopics'][subtopic]
                    st.markdown(f"""
                    <div class="case-card">
                        <div class="case-title">{subtopic}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Investigate", key=f"rec_{subtopic}", use_container_width=True):
                        st.session_state['current_subtopic'] = subtopic
                        st.session_state['current_page'] = 'case_briefing'
                        st.session_state['responses'] = []
                        st.session_state['basic_completed'] = False
                        st.session_state['intermediate_completed'] = False
                        st.session_state['advanced_completed'] = False
                        st.rerun()

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state['current_page'] = 'home'
            st.session_state['current_chapter'] = None
            st.session_state['current_subtopic'] = None
            st.session_state['responses'] = []
            st.session_state['basic_completed'] = False
            st.session_state['intermediate_completed'] = False
            st.session_state['advanced_completed'] = False
            st.rerun()

    with col2:
        if st.button("📋 Review Answers", use_container_width=True):
            st.markdown("### 📋 Answer Review")
            for i, r in enumerate(responses, 1):
                status = "✅" if r['is_correct'] else "❌"
                with st.expander(f"Q{i}: {status} {r['topic']}"):
                    st.write(f"**Your answer:** {r['selected_option']}. {r['selected_text']}")
                    st.write(f"**Correct:** {r['correct_option']}")
                    st.write(f"**Time:** {r['time_spent']:.1f}s")

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

