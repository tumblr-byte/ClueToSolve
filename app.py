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

def show_basic_break_page():
    """Show break/rest page after basic completion"""
    st.markdown("""
    <div class="detective-header">
        <h1>🕶️ Investigation Break</h1>
        <p>You've completed the Basic level! Take a moment to rest or continue your investigation.</p>
    </div>
    """, unsafe_allow_html=True)

    # Show basic level stats and recommendations
    basic_responses = [r for r in st.session_state['responses'] if r['difficulty'] == 'basic']
    if basic_responses:
        basic_correct = sum(1 for r in basic_responses if r['is_correct'])
        basic_accuracy = basic_correct / len(basic_responses) if basic_responses else 0

        st.subheader("📊 Basic Level Performance")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Questions Completed", f"{len(basic_responses)}")
        with col2:
            st.metric("Accuracy", f"{basic_accuracy*100:.1f}%")
        with col3:
            avg_time = sum(r['time_spent'] for r in basic_responses) / len(basic_responses)
            st.metric("Avg Time", f"{avg_time:.1f}s")

        # Analyze basic level topics
        topics = {}
        for r in basic_responses:
            topic = r['topic']
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(r['is_correct'])

        st.subheader("🔍 Basic Level Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**💪 Strengths:**")
            for topic, results in topics.items():
                accuracy = sum(results) / len(results)
                if accuracy >= 0.7:
                    st.markdown(f"✅ {topic}: {accuracy*100:.1f}%")

        with col2:
            st.markdown("**🎯 Weaknesses:**")
            for topic, results in topics.items():
                accuracy = sum(results) / len(results)
                if accuracy <= 0.5:
                    st.markdown(f"⚠️ {topic}: {accuracy*100:.1f}%")

        # Recommendations
        if all(sum(results) / len(results) >= 0.7 for results in topics.values()):
            st.success("Excellent work on the basics! You're ready for the next level.")
        else:
            st.info("Review the topics you struggled with before continuing.")

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⏸️ Take a Break", type="secondary", use_container_width=True):
            st.info("Take your time! Come back when you're ready.")
            if st.button("Return to Home", key="break_home"):
                st.session_state['current_page'] = 'home'
                st.rerun()

    with col2:
        if st.button("▶️ Continue to Intermediate", type="primary", use_container_width=True):
            st.session_state['current_page'] = 'intermediate'
            st.session_state['current_question_index'] = 0
            st.rerun()

# Main app
def main():
    initialize_session_state()

    # Page routing
    if st.session_state['current_page'] == 'home':
        show_home_page()
    elif st.session_state['current_page'] == 'case_briefing':
        show_case_briefing_page()
    elif st.session_state['current_page'] == 'basic_break':
        show_basic_break_page()
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
    # Try to display logo if available
    try:
        from PIL import Image
        logo = Image.open('logo.png')
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(logo, width=200)
    except:
        pass  # Logo not found, continue without it

    st.markdown("""
    <div class="detective-header">
        <h1>� ClueToSolve</h1>
        <p>A Gamified Learning Platform for Class 10 Math Students</p>
        <p>🏆 Solve the clues and crack the case!</p>
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

    # Always show Start Journey button
    st.subheader("🎯 Your Mission")
    st.info("Follow the detective's progression: Start with Basic clues, then Intermediate evidence, and finally solve the Advanced case!")

    col1, col2 = st.columns(2)
    with col1:
        if st.session_state['basic_completed'] and st.session_state['intermediate_completed']:
            st.success("✅ Clues gathered! Evidence analyzed! Ready to crack the case!")
        else:
            if not st.session_state['basic_completed']:
                st.info("🔍 Gather Clues: Not completed")
            else:
                st.success("🔍 Gather Clues: Completed!")

            if not st.session_state['intermediate_completed']:
                st.info("🔎 Analyze Evidence: Not completed")
            else:
                st.success("🔎 Analyze Evidence: Completed!")

    with col2:
        if st.button("🚀 Start Journey", type="primary", use_container_width=True):
            # Start basic questions
            st.session_state['current_difficulty'] = 'basic'
            st.session_state['current_question_index'] = 0
            st.session_state['current_page'] = 'basic'
            st.rerun()

        if st.button("🏠 Back to Headquarters", use_container_width=True):
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

def get_explanation_from_gemini(question):
    """Generate a detailed explanation using Gemini AI"""
    if st.session_state['gemini_model'] is None:
        return "AI explanations are unavailable. Please check your configuration."

    try:
        prompt = f"""
        You are a helpful math tutor. Provide a detailed, step-by-step explanation for this question.

        Question: {question['question']}
        Options: {', '.join([f"{k}: {v}" for k, v in question['options'].items()])}
        Correct Answer: {question['answer']['correct_option']} - {question['options'][question['answer']['correct_option']]}

        Steps from the answer:
        {json.dumps(question['answer']['steps'], indent=2)}

        Explanation: {question['answer']['explanation']}

        Provide a comprehensive explanation that helps the student understand the concept, not just the answer.
        """

        response = st.session_state['gemini_model'].generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Failed to generate explanation: {str(e)}"

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
        raw_options = question['options']

        # Handle both dictionary and array formats for options
        if isinstance(raw_options, dict):
            options = raw_options
            option_keys = list(options.keys())
        elif isinstance(raw_options, list):
            # Convert array to dictionary format
            options = {
                "A": raw_options[0] if len(raw_options) > 0 else "",
                "B": raw_options[1] if len(raw_options) > 1 else "",
                "C": raw_options[2] if len(raw_options) > 2 else "",
                "D": raw_options[3] if len(raw_options) > 3 else ""
            }
            option_keys = ["A", "B", "C", "D"]
        else:
            # Fallback
            options = {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}
            option_keys = ["A", "B", "C", "D"]

        # Check if this question has already been answered
        has_answered = False
        answer_is_correct = False
        for r in st.session_state['responses']:
            if r['question_id'] == question['id']:
                has_answered = True
                answer_is_correct = r['is_correct']
                break

        # If not answered yet, show selection interface
        if not has_answered:
            # Radio buttons for answer
            selected_label = st.radio(
                "Choose your answer:",
                option_keys,
                key=f"q_{question['id']}"
            )

            # Submit button
            submit_disabled = selected_label is None
            if st.button("✅ Submit Answer", type="primary", disabled=submit_disabled, use_container_width=True):
                if selected_label:
                    save_answer(question, selected_label, options[selected_label])
                    st.rerun()

        # If answered, show result and explanation
        else:
            # Show selected answer
            selected_text = ""
            for r in st.session_state['responses']:
                if r['question_id'] == question['id']:
                    selected_text = f"{r['selected_option']}: {r['selected_text']}"
                    break

            st.info(f"**Your Answer:** {selected_text}")

            # Show result message
            if answer_is_correct:
                st.success("🎉 Excellent detective work! You got it right!")
            else:
                correct_answer = ""
                try:
                    if question.get('answer'):
                        correct_option = question['answer'].get('correct_option', '')
                        if isinstance(raw_options, dict):
                            correct_answer = f"{correct_option}: {raw_options.get(correct_option, 'Unknown')}"
                        else:
                            # Handle array format
                            if isinstance(raw_options, list):
                                index = ord(correct_option.upper()) - ord('A')
                                if 0 <= index < len(raw_options):
                                    correct_answer = f"{correct_option}: {raw_options[index]}"
                            else:
                                correct_answer = correct_option
                except:
                    correct_answer = "Unable to determine correct answer"

                st.error(f"❌ Oops detective! You missed this part.\n\n**Correct Answer:** {correct_answer}")

            # Show explanation from JSON
            try:
                if question.get('answer') and question['answer'].get('explanation'):
                    st.subheader("📚 Explanation")
                    st.write(question['answer']['explanation'])

                    if question['answer'].get('steps'):
                        st.subheader("🔢 Solution Steps")
                        steps = question['answer']['steps']
                        if isinstance(steps, dict):
                            for step_key, step_text in steps.items():
                                st.write(f"**{step_key.replace('_', ' ').title()}:** {step_text}")
                        else:
                            st.write(steps)
            except:
                st.info("Answer explanation will be shown below.")

            st.markdown("---")

            # Navigation buttons (after answer is shown)
            col1, col2, col3 = st.columns([1, 1, 3])

            with col1:
                if st.session_state['current_question_index'] > 0:
                    if st.button("⬅️ Previous", key="prev"):
                        st.session_state['current_question_index'] -= 1
                        st.session_state['question_start_time'] = None
                        st.rerun()

            with col2:
                next_label = "Next ➡️" if st.session_state['current_question_index'] < len(questions) - 1 else "Finish 🎯"
                if st.button(next_label, key="next"):
                    if st.session_state['current_question_index'] < len(questions) - 1:
                        st.session_state['current_question_index'] += 1
                        st.session_state['question_start_time'] = None
                        st.rerun()
                    else:
                        # Completed difficulty level
                        complete_difficulty_level()
                        st.rerun()

            with col3:
                if st.button("🔙 Back to Case", key="back_to_case"):
                    st.session_state['current_page'] = 'case_briefing'
                    st.rerun()

                # Gemini witness in sidebar (only show after first question and when answered)
                answered_questions = len([r for r in st.session_state['responses'] if r['difficulty'] == st.session_state['current_difficulty']])
                if answered_questions > 0:  # Show only after answering at least one question
                    with st.sidebar:
                        st.subheader("🕵️ Ask Witness")

                        # Create a form-like interface for hint type selection
                        hint_type_placeholder = st.empty()
                        hint_type = hint_type_placeholder.radio(
                            "What would you like help with?",
                            ["Hint (subtle guidance)", "Explanation (detailed answer)", "Cancel"],
                            key="hint_type_radio"
                        )

                        if st.button("🚨 Consult Witness", key="consult_witness"):
                            if hint_type == "Cancel":
                                st.info("Consultation cancelled. Good luck!")
                            else:
                                with st.spinner("Consulting the witness..."):
                                    if hint_type == "Hint (subtle guidance)":
                                        hint_response = get_hint_from_gemini()
                                    else:  # Explanation
                                        hint_response = get_explanation_from_gemini(question)
                                st.markdown(f'<div class="hint-box">**Witness Says:** {hint_response}</div>', unsafe_allow_html=True)

                        # Clear the radio selection after use (optional)
                        if st.button("Clear Selection", key="clear_hint"):
                            st.rerun()
def save_answer(question, selected_label, selected_text):
    """Save answer to session state"""
    question_id = question['id']

    # Safely get correct answer
    correct_answer = 'Unknown'
    try:
        if question.get('answer') and question['answer'].get('correct_option'):
            correct_answer = question['answer']['correct_option']
        else:
            # Try to infer correct answer from some other source or default
            correct_answer = 'A'  # Default fallback
    except:
        correct_answer = 'A'  # Fallback if anything goes wrong

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
        # After basic completion, show the break page before intermediate
        st.session_state['current_page'] = 'basic_break'
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


