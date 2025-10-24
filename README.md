# 🎓 RAG Study Tool

A comprehensive study tool that uses Retrieval-Augmented Generation (RAG) to help students learn from their study materials. Upload documents, generate interactive quizzes, get AI-powered study assistance, and track your learning progress.

## ✨ Features

### 📝 Quiz Generator
- **Multi-format Support**: Upload PDFs, Word documents, text files, Markdown, and images (with OCR)
- **Interactive Quizzes**: Generate HTML quizzes with instant feedback
- **Customizable**: Choose number of questions, difficulty level, and question types
- **Question Types**: Multiple choice, true/false, and short answer questions
- **Wrong Answer Tracking**: Review and learn from your mistakes

### 💬 Study Assistant
- **AI-Powered Q&A**: Ask questions about your uploaded materials
- **Source Citations**: All answers are based on your uploaded documents
- **Pomodoro Timer**: Built-in timer for focused study sessions
- **Session Tracking**: Monitor your study progress

### 📊 Wrong Answer Review
- **Mistake Analysis**: Review all your incorrect quiz answers
- **Detailed Explanations**: Understand why answers were wrong
- **Retry Options**: Practice with questions you got wrong
- **Progress Tracking**: See improvement over time

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd RAG-Study-Tool
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Open your browser** and go to the URL shown in the terminal (usually `http://localhost:7860`)

## 📚 Supported File Formats

- **PDF** (.pdf) - Text extraction from PDF documents
- **Word Documents** (.docx, .doc) - Microsoft Word files
- **Text Files** (.txt) - Plain text documents
- **Markdown** (.md) - Markdown formatted files
- **Images** (.png, .jpg, .jpeg) - OCR text extraction from images

## 🎯 How to Use

### 1. Upload Study Materials
- Go to the "Quiz Generator" or "Study Assistant" tab
- Click "Upload files" and select your study materials
- Click "Process Files" to analyze your documents
- Wait for the confirmation message

### 2. Generate Quizzes
- In the "Quiz Generator" tab:
  - Choose number of questions (5-50)
  - Select difficulty level (Easy/Medium/Hard)
  - Pick question types (Multiple Choice, True/False, Short Answer)
  - Click "Generate Quiz"
  - Answer questions and get instant feedback

### 3. Study with AI Assistant
- In the "Study Assistant" tab:
  - Use the Pomodoro timer for focused study sessions
  - Ask questions about your materials in the chat
  - Get detailed answers with source citations
  - Track your study sessions

### 4. Review Mistakes
- In the "Wrong Answer Review" tab:
  - Click "Load Wrong Answers" to see your quiz mistakes
  - Review explanations for each wrong answer
  - Use "Clear History" to reset your progress

## ⚙️ Configuration

### Pomodoro Timer Settings
- **Work Sessions**: 5-60 minutes (default: 25 minutes)
- **Break Sessions**: 5-30 minutes (default: 5 minutes)
- **Session Tracking**: Automatic counting of completed sessions

### Quiz Settings
- **Questions**: 5-50 questions per quiz
- **Difficulty**: Easy, Medium, or Hard
- **Types**: Mix of multiple choice, true/false, and short answer

## 🔧 Technical Details

### Architecture
- **RAG System**: Uses LangChain and ChromaDB for document processing
- **AI Models**: OpenAI GPT-4o-mini for question generation and Q&A
- **Vector Database**: ChromaDB for efficient document retrieval
- **Web Interface**: Gradio for modern, interactive UI

### File Processing
- Documents are chunked into smaller pieces for better retrieval
- Each chunk includes metadata about source file and position
- Vector embeddings are created using OpenAI's text-embedding-3-small model

### Security
- All processing happens locally (except AI API calls)
- No data is stored permanently
- Temporary vector stores are created per session

## 🛠️ Development

### Project Structure
```
RAG-Study-Tool/
├── main.py              # Main entry point
├── app.py               # Gradio web interface
├── rag_chatbot.py       # Core RAG functionality
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Key Components
- **rag_chatbot.py**: Core RAG system with file loaders and AI agents
- **app.py**: Gradio interface with three main tabs
- **main.py**: Application launcher

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. Please check the license file for details.

## 🆘 Troubleshooting

### Common Issues

**"No module named 'gradio'"**
- Run: `pip install -r requirements.txt`

**"OpenAI API key not found"**
- Create a `.env` file with your OpenAI API key

**"Error processing files"**
- Check that your files are in supported formats
- Ensure files are not corrupted or password-protected

**"Quiz generation failed"**
- Make sure you've uploaded and processed files first
- Check that your documents contain readable text

### Getting Help
- Check the terminal output for error messages
- Ensure all dependencies are installed correctly
- Verify your OpenAI API key is valid and has credits

## 🎉 Features Roadmap

- [ ] Spaced repetition system for flashcards
- [ ] Study group collaboration features
- [ ] Voice input/output for accessibility
- [ ] Advanced analytics and progress tracking
- [ ] Export quizzes as PDF
- [ ] Integration with popular note-taking apps

---

**Happy Studying! 🎓📚**