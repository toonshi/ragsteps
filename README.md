# Bright Steps - Intelligent Child Development Assistant

## Overview
Bright Steps is an innovative child development tracking system that combines modern AI techniques with expert knowledge to help parents and caregivers track, understand, and support their child's development journey. The system uses Retrieval-Augmented Generation (RAG) to provide personalized, evidence-based answers about child development.

## Key Features

### Profile Management
- 👶 Create and manage child profiles
- 📊 Track age-appropriate milestones
- 🏥 Record medical considerations
- 🎯 Monitor focus areas

### Development Tracking
- ✅ Age-appropriate milestone checklists
- 📈 Progress tracking over time
- 🎨 Multiple development categories
- 📝 Notes and observations

### AI-Powered Assistance
- 🧠 Intelligent question answering about child development
- 📚 Evidence-based information retrieval
- 🔍 Context-aware responses
- 👤 Profile-aware suggestions

### User Interface
- 💻 Clean, intuitive Streamlit interface
- 📱 Mobile-friendly design
- 🔄 Real-time updates
- 📊 Visual progress indicators

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Virtual environment (recommended)
- OpenAI API key
- Pinecone API key (for vector storage)

### Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd ragsteps
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv rags
rags\Scripts\activate

# Linux/Mac
python -m venv rags
source rags/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with:
```env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=your_index_name
```

### Running the Application

1. Start the Streamlit interface:
```bash
streamlit run web/main_streamlit_with_profiles.py
```

2. Open your browser:
- The interface will automatically open at `http://localhost:8501`

## Usage Guide

### Creating a Profile
1. Use the sidebar to create a new profile
2. Enter child's name and date of birth
3. Add any medical considerations
4. Specify current focus areas

### Tracking Development
1. Select a profile to load
2. View age-appropriate milestones
3. Check off completed milestones
4. Track progress over time

### Getting Development Advice
1. Ask questions about child development
2. Receive personalized, evidence-based answers
3. Get suggestions based on the child's profile

## Technical Details

### Components
- **Frontend**: Streamlit
- **Embeddings**: DPR (facebook/dpr-question_encoder-single-nq-base)
- **Vector Store**: Pinecone
- **LLM**: GPT-3.5-turbo
- **Profile Storage**: Local JSON files

### Project Structure
```
ragsteps/
├── web/                  # Web interface
│   └── main_streamlit_with_profiles.py
├── src/
│   ├── models/          # Data models
│   ├── rag/            # RAG implementation
│   └── utils/          # Utilities
├── data/               # Development data
└── user_data/         # User profiles
```

## Security & Privacy
- All profile data is stored locally
- API keys are secured in .env
- No personal data is sent to external services
- Regular security updates

## Troubleshooting

### Common Issues
1. **Profile Not Saving**
   - Check write permissions in user_data directory
   - Verify profile format

2. **RAG Not Responding**
   - Verify API keys in .env
   - Check internet connection
   - Confirm Pinecone index is running

3. **Milestone Tracking**
   - Ensure date of birth is correct
   - Check age calculations

## Contributing
We welcome contributions! Please feel free to submit pull requests or open issues for discussion.

## License
This project is licensed under the MIT License - see the LICENSE file for details.