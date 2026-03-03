
# CRM Intelligence Pipeline 🎯

An intelligent pipeline that transcribes, analyzes, and extracts insights from meetings/ calls and meetings using AI agents.

## 🚀 Features

- **Audio/Video Transcription** - Automatic speech-to-text using Faster Whisper
- **Intelligent Analysis** - Extract tasks, decisions, and key points using CrewAI agents
- **Sentiment Analysis** - Understand meeting mood and communication patterns
- **Task Extraction** - Identify action items, owners, and deadlines
- **Q&A System** - Chat with your meeting data using RAG
- **REST API** - FastAPI backend with comprehensive endpoints
- **Streamlit UI** - Beautiful dashboard for visualization

## 📋 Prerequisites

- Python 3.11+
- FFmpeg (for audio processing)
- CUDA-capable GPU (optional, for faster processing)

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/crm-intel-pipeline.git
cd crm-intel-pipeline


# Using conda (recommended)
conda create -n crm-intel python=3.11
conda activate crm-intel

# OR using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate



pip install -r requirements.txt


# Ubuntu/Debian
sudo apt-get install ffmpeg

# MacOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html


cp .env.example .env
# Edit .env with your API keys and settings


python -m app.main
# This will create the SQLite database in the data/ directory



streamlit run streamlit_app.py