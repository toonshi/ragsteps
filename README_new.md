# Bright Steps - Intelligent Child Development Assistant

## Overview
Bright Steps is an innovative child development tracking system that combines modern AI techniques with expert knowledge to help parents and caregivers track, understand, and support their child's development journey. The system uses Retrieval-Augmented Generation (RAG) to provide personalized, evidence-based answers about child development.

## Development Categories

Bright Steps tracks development across key areas defined by leading pediatric organizations:

### 🏃‍♂️ Motor Skills
- **Gross Motor**: Large muscle movements like crawling, walking, running
- **Fine Motor**: Small muscle control for tasks like grasping, drawing, using utensils

### 🗣️ Speech and Language
- **Receptive Language**: Understanding words and directions
- **Expressive Language**: Using words, gestures, and facial expressions
- **Speech Sounds**: Pronunciation and articulation

### 👥 Social and Emotional
- **Social Interaction**: Playing with others, sharing, turn-taking
- **Emotional Expression**: Showing feelings, self-regulation
- **Attachment**: Bonding with caregivers and forming relationships

### 🧠 Cognitive Development
- **Problem Solving**: Finding solutions, understanding cause and effect
- **Memory**: Recalling events, learning routines
- **Attention**: Focusing on tasks, following directions
- **Early Learning**: Colors, numbers, shapes, letters

### 🥄 Self-Help Skills
- **Feeding**: Using utensils, drinking from cups
- **Dressing**: Managing clothes, shoes, buttons
- **Toileting**: Bathroom independence
- **Personal Care**: Washing hands, brushing teeth

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

### API Setup

#### OpenAI Configuration
1. Visit [OpenAI API Keys](https://platform.openai.com/account/api-keys)
2. Create a new API key
3. Add to your `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Cost Considerations**:
- GPT-3.5-turbo: ~$0.002 per query
- Embedding: ~$0.0001 per 1K tokens
- Set monthly limits in OpenAI dashboard

#### Pinecone Setup
1. Create account at [Pinecone](https://www.pinecone.io/)
2. Create a new project
3. Create an index:
   - Dimensions: 768 (DPR embedding size)
   - Metric: Cosine
   - Pod Type: p1.x1 (starter)
4. Add to your `.env`:
```env
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=your_index_name
```

**Rate Limits**:
- Free tier: 1 request/second
- Starter: 100 requests/second
- Monitor usage in Pinecone dashboard

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

## Data Sources

Bright Steps uses evidence-based developmental guidelines from leading organizations:

### CDC Developmental Milestones
- Age-specific milestones from 2 months to 5 years
- Updated guidelines (2022) based on latest research
- [CDC Milestone Checklist](https://www.cdc.gov/ncbddd/actearly/milestones/index.html)

### WHO Growth Standards
- International growth standards
- Evidence-based developmental norms
- [WHO Child Growth Standards](https://www.who.int/tools/child-growth-standards)

### AAP Recommendations
- American Academy of Pediatrics guidelines
- Best practices for child development
- [AAP Developmental Monitoring](https://www.aap.org/en/patient-care/developmental-monitoring-and-screening/)

### Expert Resources
- Zero to Three developmental guidelines
- Child development research publications
- Pediatric specialist recommendations

## Security & Privacy
- All profile data is stored locally
- API keys are secured in .env
- No personal data is sent to external services
- Regular security updates

## Deployment Options

### Local Deployment
1. Follow installation steps above
2. Run with `streamlit run`
3. Access via localhost

### Docker Deployment
```bash
# Build image
docker build -t bright-steps .

# Run container
docker run -p 8501:8501 bright-steps
```


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
