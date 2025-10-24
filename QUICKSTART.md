# 🚀 Quick Start Guide - RAG Study Tool

## Prerequisites
- Python 3.8 or higher
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

## Installation & Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key
1. Edit the `.env` file in the project root
2. Replace `your_openai_api_key_here` with your actual OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

### Step 3: Verify Setup
```bash
python setup_check.py
```

This will check that all dependencies are installed and configured correctly.

### Step 4: Run the Application
```bash
python main.py
```

The application will launch in your default web browser at `http://localhost:7860`

## First-Time Usage

### 1. Upload Study Materials
- Go to the **Quiz Generator** tab
- Click "Upload files" 
- Select your study materials (PDF, DOCX, TXT, MD, or images)
- Click **Process Files**
- Wait for the success message

### 2. Generate a Quiz
- Choose the number of questions (5-50)
- Select difficulty level (Easy/Medium/Hard)
- Pick question types (Multiple Choice, True/False, Short Answer)
- Click **Generate Quiz**
- Take the quiz and get instant feedback!

### 3. Use the Study Assistant
- Switch to the **Study Assistant** tab
- Start the Pomodoro timer for focused study sessions
- Ask questions about your materials in the chat
- Get AI-powered answers based on your documents

### 4. Review Wrong Answers
- Go to the **Wrong Answer Review** tab
- Click **Load Wrong Answers** to see your mistakes
- Study the explanations to improve understanding

## Troubleshooting

### "OpenAI API key not found"
- Make sure you've edited the `.env` file
- Check that your API key starts with `sk-`
- Verify there are no extra spaces or quotes

### "Error processing files"
- Check that files aren't corrupted or password-protected
- Ensure files are in supported formats (PDF, DOCX, TXT, MD, PNG, JPG)
- Try uploading one file at a time

### "No module named X"
- Run: `pip install -r requirements.txt`
- Make sure you're using Python 3.8 or higher

### Application won't start
- Run `python setup_check.py` to diagnose issues
- Check the terminal for error messages
- Verify all dependencies are installed

## Features Overview

### 📝 Quiz Generator
- Multi-format document support
- Customizable quiz parameters
- Interactive HTML quizzes
- Instant feedback and scoring

### 💬 Study Assistant  
- AI-powered Q&A based on your materials
- Source citations for all answers
- Pomodoro timer with session tracking
- Work and break period customization

### 📊 Wrong Answer Review
- Track all incorrect quiz answers
- Detailed explanations for each mistake
- Review history management
- Learn from your errors

## Tips for Best Results

1. **Upload Quality Materials**: The better your source documents, the better the AI's answers
2. **Use the Pomodoro Timer**: 25-minute focused sessions improve retention
3. **Review Wrong Answers**: Learning from mistakes is key to mastery
4. **Ask Specific Questions**: Get better answers by being precise in your queries
5. **Mix Question Types**: Use all question types for comprehensive testing

## Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review error messages in the terminal
- Verify your OpenAI API key is valid and has available credits
- Ensure you have a stable internet connection for API calls

---

**Happy Studying! 🎓📚**
