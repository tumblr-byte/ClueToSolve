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
    page_title="Math Detective",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for detective theme
def local_css():
    st.markdown("""
    <style>
    /* Detective theme colors */
    :root {
        --primary: #1e3a8a;
        --accent: #f97316;
        --success: #10b981;
        --warning: #fbbf24;
        --background: #f0f9ff;
    }

    .detective-header {
        background: linear-gradient(135deg, var(--primary), var(--accent));
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }

    .case-card {
        background: white;
        border: 2px solid var(--primary);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    .case-card.locked {
        border-color: #ef4444;
        opacity: 0.7;
    }

    .case-card.unlocked {
        border-color: var(--success);
    }

    .hint-box {
        background: var(--warning);
        color: black;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .results-card {
        background: var(--background);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .stButton > button {
        background: var(--primary) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s !important;
    }

    .stButton > button:hover {
        background: var(--accent) !important;
        transform: translateY(-2px) !important;
    }

    .stProgress > div > div > div {
        background-color: var(--success) !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
        'gemini_model': None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Initialize Gemini model if not done
    if st.session_state['gemini_model'] is None:
        try:
            st.session_state['gemini_model'] = setup_vertex_ai()
        except Exception as e:
            st.error(f"Failed to initialize AI model: {e}. Hints will be unavailable.")

# Main app
def main():
    initialize_session_state()

    # Page routing
    if st.session_state['current_page'] == 'home':
        show_home_page()
    elif st.session_state['current_page'] == 'case_briefing':
        show_case_briefing_page()
    elif st.session_state['current_page'] in ['basic', 'intermediate', 'advanced']:
        show_quiz_page()
    elif st.session_state['current_page'] == 'results':
        show_results_page()

# Placeholder functions to be implemented
def load_chapters():
    """Load chapter structure from 1.json"""
    with open('1.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['chapters']

def load_questions_data(chapter, subtopic_key):
    """Load questions for a subtopic"""
    cache_key = f"{chapter}_{subtopic_key}"
    if cache_key in st.session_state['questions_data']:
        return st.session_state['questions_data'][cache_key]

    chapters = load_chapters()
    if chapter in chapters and subtopic_key in chapters[chapter]['subtopics']:
        questions_file = chapters[chapter]['subtopics'][subtopic_key]['questions_file']
        with open(questions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        questions = data['questions']
        st.session_state['questions_data'][cache_key] = questions
        return questions
    return []

def show_home_page():
    st.markdown("""
    <div class="detective-header">
        <h1>🕵️ Math Detective</h1>
        <p>A Gamified Learning Platform for Class 10 Math Students</p>
        <p>🏆 Solve the clues and crank the case!</p>
    </div>
    """, unsafe_allow_html=True)

    chapters = load_chapters()

    for chapter_name, chapter_data in chapters.items():
        st.subheader(f"📚 {chapter_name}")

        cols = st.columns(2)
        for i, (subtopic_key, subtopic_data) in enumerate(chapter_data['subtopics'].items()):
            with cols[i % 2]:
                description = subtopic_data['description']

                # Check if unlocked (implement logic later)
                is_unlocked = True  # Placeholder

                classes = "case-card unlocked" if is_unlocked else "case-card locked"

                st.markdown(f"""
                <div class="{classes}">
                    <h4>🔍 {subtopic_key}</h4>
                    <p>{description}</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"Investigate {subtopic_key}", key=f"{chapter_name}_{subtopic_key}"):
                    st.session_state['current_chapter'] = chapter_name
                    st.session_state['current_subtopic'] = subtopic_key
                    st.session_state['current_page'] = 'case_briefing'
                    st.rerun()

def show_case_briefing_page():
    if not st.session_state['current_chapter'] or not st.session_state['current_subtopic']:
        st.error("No case selected!")
        if st.button("Back to Home"):
            st.session_state['current_page'] = 'home'
            st.rerun()
        return

    # Load advanced questions to show case file
    questions = load_questions_data(st.session_state['current_chapter'], st.session_state['current_subtopic'])
    advanced_questions = [q for q in questions if q['difficulty_level'] == 'advanced']

    if not advanced_questions:
        st.error("No advanced case found!")
        return

    case = advanced_questions[0]  # Assuming one advanced case per subtopic
    case_file = case.get('case_file', {})

    st.markdown("""
    <div class="detective-header">
        <h1>🚨 {case.get('case_title', 'Case File')}</h1>
        <p>Case #{case.get('case_number', 'Unknown')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Case file display
    st.subheader("📄 Case Briefing")
    st.info(case_file.get('briefing', 'No briefing available.'))

    st.subheader("🏛️ Crime Scene")
    st.write(case_file.get('crime_scene', 'No scene description.'))

    if 'evidence_found' in case_file and case_file['evidence_found']:
        st.subheader("🧪 Evidence Found")
        evidence = case_file['evidence_found']
        for key, value in evidence.items():
            st.write(f"**{key.replace('_', ' ').title()}:** {value}")

    if 'mystery' in case_file:
        st.subheader("❓ The Mystery")
        st.warning(case_file['mystery'])

    if st.session_state['basic_completed'] and st.session_state['intermediate_completed']:
        st.success("✅ Clues gathered! Evidence analyzed! Ready to crack the case!")
        if st.button("🚀 Start Investigation", type="primary"):
            # Start basic questions
            st.session_state['current_difficulty'] = 'basic'  # Start with basic even for briefing
            st.session_state['current_page'] = 'basic'
            st.session_state['current_question_index'] = 0
            st.rerun()
    else:
        st.error("🔒 Case locked! Solve the basic clues and analyze evidence first.")

        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state['basic_completed']:
                st.info("🔍 Gather Clues: Not completed")
            else:
                st.success("🔍 Gather Clues: Completed!")
        with col2:
            if not st.session_state['intermediate_completed']:
                st.info("🔎 Analyze Evidence: Not completed")
            else:
                st.success("🔎 Analyze Evidence: Completed!")

        if st.button("🏠 Back to Headquarters"):
            st.session_state['current_page'] = 'home'
            st.rerun()

def get_current_questions():
    """Get questions for current difficulty level"""
    questions = load_questions_data(st.session_state['current_chapter'], st.session_state['current_subtopic'])
    return [q for q in questions if q['difficulty_level'] == st.session_state['current_difficulty']]

def calculate_accuracy(responses, difficulty):
    """Calculate accuracy for a difficulty level"""
    relevant_responses = [r for r in responses if r['difficulty'] == difficulty]
    if not relevant_responses:
        return 0.0
    correct = sum(1 for r in relevant_responses if r['is_correct'])
    return correct / len(relevant_responses) if relevant_responses else 0.0

def get_hint_from_gemini():
    """Generate a hint using Gemini AI"""
    if st.session_state['gemini_model'] is None:
        return "AI hints are unavailable. Please check your configuration."

    questions = get_current_questions()
    if not questions or st.session_state['current_question_index'] >= len(questions):
        return "No question available for hint."

    current_question = questions[st.session_state['current_question_index']]

    # Prepare performance data
    responses = st.session_state['responses']
    topic = current_question.get('topic', 'unknown')

    # Calculate strengths and weaknesses
    all_topics = set()
    for q in questions:
        all_topics.add(q.get('topic', 'unknown'))

    strengths = []
    weaknesses = []

    for t in all_topics:
        topic_responses = [r for r in responses if r['topic'] == t]
        if topic_responses:
            accuracy = sum(1 for r in topic_responses if r['is_correct']) / len(topic_responses)
            if accuracy >= 0.7:
                strengths.append(t)
            elif accuracy <= 0.5:
                weaknesses.append(t)

    prompt = f"""
    You are a helpful math tutor assisting a Class 10 student.

    Student is on {st.session_state['current_difficulty']} level, question about "{topic}".
    Current question: "{current_question['question']}"

    Their strengths: {', '.join(strengths) if strengths else 'None identified yet'}
    Their weaknesses: {', '.join(weaknesses) if weaknesses else 'None identified yet'}

    Provide a helpful hint (2-3 sentences) based on their performance patterns. Don't give away the answer, but guide them toward the correct approach.
    """

    try:
        response = st.session_state['gemini_model'].generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Failed to generate hint: {str(e)}"

def show_quiz_page():
    questions = get_current_questions()
    if not questions:
        st.error("No questions found for this difficulty level!")
        if st.button("Back to Case Brief"):
            st.session_state['current_page'] = 'case_briefing'
            st.rerun()
        return

    # Header based on difficulty
    headers = {
        'basic': "🔍 Gathering Clues",
        'intermediate': "🔎 Analyzing Evidence",
        'advanced': "🚨 Cracking the Case!"
    }

    st.markdown(f"""
    <div class="detective-header">
        <h1>{headers[st.session_state['current_difficulty']]}</h1>
        <p>Question {st.session_state['current_question_index'] + 1} of {len(questions)}</p>
    </div>
    """, unsafe_allow_html=True)

    # Progress bar
    progress = (st.session_state['current_question_index'] + 1) / len(questions)
    st.progress(progress)

    # Current question
    if st.session_state['current_question_index'] < len(questions):
        question = questions[st.session_state['current_question_index']]

        # Track question start time
        if st.session_state['question_start_time'] is None:
            st.session_state['question_start_time'] = time.time()

        st.subheader(f"Question {st.session_state['current_question_index'] + 1}")
        st.write(question['question'])

        # Options
        options = question['options']
        option_keys = list(options.keys())

        # Get previous answer if exists
        previous_response = None
        for r in st.session_state['responses']:
            if r['question_id'] == question['id']:
                previous_response = r
                break

        selected_option = None
        if previous_response:
            selected_option = previous_response['selected_option']

        # Radio buttons for answer
        selected_label = st.radio(
            "Choose your answer:",
            option_keys,
            index=option_keys.index(selected_option) if selected_option else None,
            key=f"q_{question['id']}"
        )

        # Navigation buttons
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])

        with col1:
            if st.session_state['current_question_index'] > 0:
                if st.button("⬅️ Previous", key="prev"):
                    # Save current answer if selected
                    if selected_label:
                        save_answer(question, selected_label, options[selected_label])

                    st.session_state['current_question_index'] -= 1
                    st.session_state['question_start_time'] = None
                    st.rerun()

        with col2:
            next_disabled = selected_label is None
            next_label = "Next ➡️" if st.session_state['current_question_index'] < len(questions) - 1 else "Finish 🎯"

            if st.button(next_label, key="next", disabled=next_disabled):
                # Save answer
                if selected_label:
                    save_answer(question, selected_label, options[selected_label])

                if st.session_state['current_question_index'] < len(questions) - 1:
                    st.session_state['current_question_index'] += 1
                    st.session_state['question_start_time'] = None
                    st.rerun()
                else:
                    # Completed difficulty level
                    complete_difficulty_level()
                    st.rerun()

        with col3:
            if st.button("🔙 Back to Case"):
                st.session_state['current_page'] = 'case_briefing'
                st.rerun()

        with col4:
            # Gemini hint in sidebar
            with st.sidebar:
                st.subheader("🕵️ Ask Witness for Hint")
                if st.button("💡 Get Hint", key="hint"):
                    with st.spinner("Consulting the witness..."):
                        hint = get_hint_from_gemini()
                    st.markdown(f'<div class="hint-box">**Witness Says:** {hint}</div>', unsafe_allow_html=True)

                # Quick stats
                st.subheader("📊 Your Progress")
                responses = st.session_state['responses']
                total_answered = len(responses)
                correct = sum(1 for r in responses if r['is_correct'])

                if total_answered > 0:
                    accuracy = correct / total_answered * 100
                    st.metric("Accuracy", f"{accuracy:.1f}%")
                    st.metric("Answered", f"{correct}/{total_answered}")
                else:
                    st.info("Start answering to see progress!")
def save_answer(question, selected_label, selected_text):
    """Save answer to session state"""
    question_id = question['id']
    correct_answer = question['answer']['correct_option']
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

    # Update or add response
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
        st.session_state['current_difficulty'] = 'intermediate'
        st.session_state['current_question_index'] = 0
        st.session_state['current_page'] = 'intermediate' if not st.session_state['intermediate_completed'] else 'advanced'
    elif difficulty == 'intermediate':
        st.session_state['intermediate_completed'] = True
        st.session_state['current_difficulty'] = 'advanced'
        st.session_state['current_question_index'] = 0
        st.session_state['current_page'] = 'advanced'
    elif difficulty == 'advanced':
        st.session_state['advanced_completed'] = True
        st.session_state['current_page'] = 'results'

def calculate_overall_stats():
    """Calculate overall performance statistics"""
    responses = st.session_state['responses']

    if not responses:
        return {
            'total_questions': 0,
            'total_correct': 0,
            'accuracy': 0,
            'avg_time': 0,
            'detective_rank': 'Rookie',
            'rank_color': '#6b7280',
            'strengths': [],
            'weaknesses': [],
            'red_herrings': []
        }

    total_questions = len(responses)
    total_correct = sum(1 for r in responses if r['is_correct'])
    accuracy = total_correct / total_questions if total_questions > 0 else 0
    avg_time = sum(r['time_spent'] for r in responses) / total_questions if total_questions > 0 else 0

    # Determine rank
    if accuracy >= 0.9:
        rank = 'Master Detective'
        rank_color = '#ffd700'  # Gold
    elif accuracy >= 0.8:
        rank = 'Expert Investigator'
        rank_color = '#c0c0c0'  # Silver
    elif accuracy >= 0.7:
        rank = 'Senior Detective'
        rank_color = '#cd7f32'  # Bronze
    elif accuracy >= 0.6:
        rank = 'Detective'
        rank_color = '#1e3a8a'
    else:
        rank = 'Apprentice Detective'
        rank_color = '#6b7280'

    # Analyze topic performance
    topics = {}
    for r in responses:
        topic = r['topic']
        if topic not in topics:
            topics[topic] = []
        topics[topic].append(r['is_correct'])

    strengths = []
    weaknesses = []
    red_herrings = []

    for topic, results in topics.items():
        topic_accuracy = sum(results) / len(results)
        if topic_accuracy >= 0.7:
            strengths.append((topic, topic_accuracy))
        elif topic_accuracy <= 0.5:
            weaknesses.append((topic, topic_accuracy))

    # Red herrings: common mistakes (simplified version)
    mistake_patterns = {}
    for r in responses:
        if not r['is_correct']:
            key = f"{r['topic']}_{r['selected_option']}_{r['correct_option']}"
            mistake_patterns[key] = mistake_patterns.get(key, 0) + 1

    # Get top red herrings
    sorted_mistakes = sorted(mistake_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
    for pattern, count in sorted_mistakes:
        if count > 1:  # Only if mistake repeated
            topic, wrong, correct = pattern.split('_', 2)
            red_herrings.append(f"Common mistake in {topic}: choosing {wrong} instead of {correct}")

    return {
        'total_questions': total_questions,
        'total_correct': total_correct,
        'accuracy': accuracy,
        'avg_time': avg_time,
        'detective_rank': rank,
        'rank_color': rank_color,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'red_herrings': red_herrings
    }

def show_results_page():
    st.markdown("""
    <div class="detective-header">
        <h1>🎉 Case Closed!</h1>
        <p>Your investigation is complete. Here's your performance report.</p>
    </div>
    """, unsafe_allow_html=True)

    stats = calculate_overall_stats()

    # Rank badge
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h2 style="color: {stats['rank_color']}; font-size: 2.5rem;">{stats['detective_rank']}</h2>
        <p>🏆 Congratulations!</p>
    </div>
    """.format(stats=stats), unsafe_allow_html=True)

    # Stats cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Solved", f"{stats['total_correct']}/{stats['total_questions']}")

    with col2:
        st.metric("Accuracy", f"{stats['accuracy']*100:.1f}%")

    with col3:
        st.metric("Avg Time", f"{stats['avg_time']:.1f}s")

    with col4:
        # Calculate streak (simplified)
        responses = st.session_state['responses']
        streak = 0
        for r in reversed(responses):
            if r['is_correct']:
                streak += 1
            else:
                break
        st.metric("Current Streak", streak)

    # Progress bars for difficulty levels
    st.subheader("📈 Progress by Difficulty")

    basic_acc = calculate_accuracy(st.session_state['responses'], 'basic')
    inter_acc = calculate_accuracy(st.session_state['responses'], 'intermediate')
    adv_acc = calculate_accuracy(st.session_state['responses'], 'advanced')

    col1, col2, col3 = st.columns(3)

    with col1:
        st.progress(basic_acc)
        st.write(f"🔍 Basic: {basic_acc*100:.1f}%")

    with col2:
        st.progress(inter_acc)
        st.write(f"🔎 Intermediate: {inter_acc*100:.1f}%")

    with col3:
        st.progress(adv_acc)
        st.write(f"🚨 Advanced: {adv_acc*100:.1f}%")

    # Strengths and Weaknesses
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💪 Strengths")
        if stats['strengths']:
            for topic, acc in stats['strengths']:
                st.markdown(f"✅ **{topic}**: {acc*100:.1f}% accuracy")
        else:
            st.info("Keep solving cases to build strengths!")

    with col2:
        st.subheader("🎯 Weaknesses")
        if stats['weaknesses']:
            for topic, acc in stats['weaknesses']:
                st.markdown(f"⚠️ **{topic}**: {acc*100:.1f}% accuracy")
        else:
            st.success("Great! No major weaknesses detected!")

    # Red Herrings
    if stats['red_herrings']:
        st.subheader("🚩 Red Herrings")
        for herring in stats['red_herrings']:
            st.warning(herring)

    # Charts
    responses = st.session_state['responses']
    if responses:
        st.subheader("📊 Performance Analytics")

        # Data preparation
        df = pd.DataFrame(responses)

        # Time spent by difficulty
        fig_time = px.scatter(df, x='difficulty', y='time_spent',
                             color='is_correct',
                             color_discrete_map={True: '#10b981', False: '#ef4444'},
                             title="Time Spent vs Difficulty")
        fig_time.update_layout(xaxis_title="Difficulty", yaxis_title="Time (seconds)")
        st.plotly_chart(fig_time, use_container_width=True)

        # Accuracy by topic
        if 'topic' in df.columns:
            topic_stats = df.groupby('topic').agg({
                'is_correct': ['sum', 'count', lambda x: x.sum()/x.count()]
            }).round(3)

            fig_accuracy = go.Figure()
            topics = topic_stats.index
            accuracies = topic_stats[('is_correct', '<lambda_0>')] * 100

            fig_accuracy.add_trace(go.Bar(
                x=topics,
                y=accuracies,
                marker_color='#1e3a8a'
            ))

            fig_accuracy.update_layout(
                title="Accuracy by Topic",
                xaxis_title="Topic",
                yaxis_title="Accuracy (%)"
            )
            st.plotly_chart(fig_accuracy, use_container_width=True)

    # Recommendations
    st.subheader("🎯 Practice Recommendations")
    if stats['weaknesses']:
        weak_topics = [topic for topic, _ in stats['weaknesses']]
        st.info(f"Focus on these topics: {', '.join(weak_topics)}")
    else:
        st.success("Excellent work! Keep up the great solving!")

    # Navigation
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Solve Another Case"):
            # Reset session state for new case
            st.session_state['current_page'] = 'home'
            st.session_state['current_chapter'] = None
            st.session_state['current_subtopic'] = None
            st.session_state['current_difficulty'] = 'basic'
            st.session_state['current_question_index'] = 0
            st.session_state['responses'] = []
            st.session_state['question_start_time'] = None
            st.session_state['basic_completed'] = False
            st.session_state['intermediate_completed'] = False
            st.session_state['advanced_completed'] = False
            st.rerun()

    with col2:
        if st.button("📋 Review Answers"):
            st.subheader("📋 Answer Review")
            # Show review of answers
            for i, response in enumerate(responses, 1):
                with st.expander(f"Question {i}: {'✅' if response['is_correct'] else '❌'}"):
                    st.write(f"**Your answer:** {response['selected_text']}")
                    st.write(f"**Correct answer:** {response['correct_option']}")
                    st.write(f"**Time spent:** {response['time_spent']:.1f}s")

if __name__ == "__main__":
    main()
