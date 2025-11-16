# 🕵️ClueToSolve

A gamified learning platform for Class 10 Math students, designed as a detective-themed quiz application where students solve mathematical "cases" to unlock advanced problems.

## 🎯 Features

- **Detective Theme**: Solve math problems as detective cases
- **Progressive Difficulty**: Basic → Intermediate → Advanced questions
- **AI Hints**: Gemini-powered witness hints based on performance
- **Progress Tracking**: Detailed analytics and performance insights
- **Visual Analytics**: Plotly charts for performance visualization
- **Gamification**: Detective ranks, streaks, and achievements

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- GCP Project with Vertex AI enabled
- Service account key for Vertex AI

### Installation

1. **Clone and Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up Google Cloud Credentials**

Create a `config.json` file (copy from `config.json.example`):

```json
{
  "project_id": "your-gcp-project-id",
  "location": "us-central1",
  "credentials_path": "credentials.json"
}
```

3. **Download Service Account Key**

- Go to Google Cloud Console → IAM & Admin → Service Accounts
- Create a service account or use existing one
- Generate a JSON key
- Save the file as `credentials.json` in the project root

4. **Run the Application**

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## 📊 Chapters & Topics

### Triangle
- **Similarity Criterion**: AA, SAS, SSS similarity rules
- **Converse of Basic Proportionality Theorem**: Parallel lines and proportions

### Trigonometry
- **Trigonometric Identities**: Fundamental identities and proofs
- **Trigonometry Applications**: Heights and distances problems

## 🏗️ Architecture

```
math-detective/
├── app.py                 # Main Streamlit application
├── gemini.py             # Gemini AI integration
├── config.json           # GCP configuration (gitignored)
├── credentials.json      # GCP service account key (gitignored)
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── data/                # Question data
    ├── 1.json          # Chapter structure
    ├── triangle_similarity_questions.json
    ├── triangle_bpt_questions.json
    ├── trigo_identities_questions.json
    └── trigo_applications_questions.json
```

## 🎮 How to Use

1. **Home Page**: Select a chapter and subtopic to investigate
2. **Case Briefing**: Review the advanced case (locked until you complete basic questions)
3. **Investigation Flow**:
   - 🔍 **Basic Questions** (4 questions): Gather clues
   - 🔎 **Intermediate Questions** (3 questions): Analyze evidence
   - 🚨 **Advanced Questions** (1 questions): Crack the case
4. **AI Witness**: Click "Ask Witness" for personalized hints
5. **Results**: Review performance, analytics, and recommendations

## 🔧 Technical Details

### Technologies Used

- **Streamlit**: Web framework for the UI
- Built entirely with **Cline CLI**
- **Google Vertex AI (Gemini 2.0)**: AI-powered hints
- **Plotly**: Data visualization
- **Pandas**: Data manipulation

### Session State Structure
- Question responses and performance data
- Progress tracking (completed difficulty levels)
- AI model initialization
- Navigation state

### AI Hint Logic
The Gemini AI analyzes:
- Current question and topic
- Student's current performance patterns
- Strengths and weaknesses
- Time spent on questions

Provides contextual hints without revealing answers.

## 🎯 Detective Ranks

Based on overall accuracy:
- **Master Detective** (90%+): 🏆 Gold
- **Expert Investigator** (80%+): 🥈 Silver
- **Senior Detective** (70%+): 🥉 Bronze
- **Detective** (60%+): Standard
- **Apprentice Detective** (<60%): Starter

## 📈 Analytics Features

- **Real-time Progress**: Question-by-question tracking
- **Performance Metrics**: Accuracy, time spent, streaks
- **Topic Analysis**: Strengths and weaknesses identification
- **Visual Charts**: Scatter plots, bar charts, progress indicators
- **Recommendations**: Personalized practice suggestions

## 🔒 Security & Privacy

- No user authentication (demo-focused)
- All data stored in Streamlit session state
- No persistent storage or databases
- GCP credentials properly gitignored
- Suitable for demo and educational purposes

## 🚀 Deployment

### Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Set environment variables for GCP credentials
4. Deploy!

### Other Platforms
The app is container-ready and can be deployed on:
- AWS EC2
- Google Cloud Run
- Heroku
- Any platform supporting Python/Streamlit

## 🤝 Contributing

Feel free to contribute! Areas for improvement:
- Additional math chapters
- More question types
- Enhanced AI hint logic
- Mobile responsiveness
- Additional gamification features

## 📝 License

This project is educational and can be used/modified for learning purposes.

## 🙏 Acknowledgments

- Built for educational gamification
- Powered by Google Vertex AI
- Inspired by detective mystery novels
- Designed for Class 10 Mathematics curriculum


