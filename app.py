import gradio as gr
import os
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from rag_chatbot import process_documents, create_study_agent, create_quiz_agent

# Global state
current_vectorstore = None
study_agent = None
quiz_agent = None
wrong_answers = []
pomodoro_state = {"is_running": False, "time_left": 25*60, "is_break": False, "sessions_completed": 0}

def process_uploaded_files(files) -> Tuple[str, str]:
    """Process uploaded files and create vector store."""
    global current_vectorstore, study_agent, quiz_agent
    
    if not files:
        return "No files uploaded.", "Please upload study materials to get started."
    
    file_paths = [file.name for file in files]
    
    # Process documents
    vectorstore = process_documents(file_paths)
    
    if vectorstore is None:
        return "Error processing files.", "Failed to process the uploaded files. Please check file formats and try again."
    
    # Update global state
    current_vectorstore = vectorstore
    study_agent = create_study_agent(vectorstore)
    quiz_agent = create_quiz_agent(vectorstore)
    
    file_info = f"Successfully processed {len(file_paths)} file(s):\n"
    for file_path in file_paths:
        file_info += f"• {os.path.basename(file_path)}\n"
    
    return file_info, "Files processed successfully! You can now generate quizzes or ask questions."

def generate_quiz(num_questions: int, difficulty: str, question_types: List[str]) -> Tuple[str, str]:
    """Generate a quiz based on uploaded materials."""
    global quiz_agent, wrong_answers
    
    if quiz_agent is None:
        return "Please upload files first.", "No study materials available. Please upload files before generating a quiz."
    
    if not question_types:
        return "Please select at least one question type.", "Select question types to generate a quiz."
    
    # Create quiz prompt
    types_str = ", ".join(question_types)
    prompt = f"""
    Generate a {difficulty.lower()} quiz with {num_questions} questions based on the uploaded study materials.
    
    Question types to include: {types_str}
    
    Please provide ONLY the quiz content in the following JSON format:
    {{
        "title": "Quiz Title",
        "questions": [
            {{
                "id": 1,
                "type": "multiple_choice",
                "question": "Question text here?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": 0,
                "explanation": "Explanation of the correct answer"
            }},
            {{
                "id": 2,
                "type": "true_false",
                "question": "True or false statement?",
                "correct": true,
                "explanation": "Explanation of the correct answer"
            }},
            {{
                "id": 3,
                "type": "short_answer",
                "question": "Short answer question?",
                "correct": "Expected answer",
                "explanation": "Explanation of the correct answer"
            }}
        ]
    }}
    
    Make sure questions are based only on the uploaded materials and test understanding, not just memorization.
    Return ONLY the JSON, no other text.
    """
    
    try:
        from langchain_core.messages import HumanMessage
        result = quiz_agent.invoke({"messages": [HumanMessage(content=prompt)]})
        response_content = result['messages'][-1].content
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
        if json_match:
            quiz_data = json.loads(json_match.group())
            quiz_html = create_quiz_html(quiz_data)
        else:
            # Fallback: try to extract HTML if JSON parsing fails
            html_match = re.search(r'<div.*</div>', response_content, re.DOTALL)
            if html_match:
                quiz_html = html_match.group()
            else:
                quiz_html = f"<div class='quiz-container'><h2>Quiz Generation Error</h2><p>Could not parse quiz data. Raw response:</p><pre>{response_content}</pre></div>"
        
        # Clear previous wrong answers
        wrong_answers = []
        
        return quiz_html, "Quiz generated successfully! Answer the questions and get instant feedback."
    except Exception as e:
        return f"<div class='quiz-container'><h2>Error</h2><p>Failed to generate quiz: {str(e)}</p></div>", "Failed to generate quiz. Please try again."

def create_quiz_html(quiz_data: dict) -> str:
    """Create interactive HTML quiz from quiz data."""
    html = f"""
    <style>
    .quiz-container {{
        font-family: 'Google Sans', Arial, sans-serif !important;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        background: #ffffff !important;
        color: #333333 !important;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    
    .quiz-container h2 {{
        color: #1976d2 !important;
        text-align: center;
        margin-bottom: 30px;
        font-size: 28px;
    }}
    
    .quiz-question {{
        margin-bottom: 30px;
        padding: 20px;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        background: #fafafa !important;
        color: #333333 !important;
    }}
    
    .quiz-question h3 {{
        color: #1976d2 !important;
        margin-bottom: 15px;
        font-size: 18px;
    }}
    
    .quiz-question p {{
        color: #333333 !important;
        margin-bottom: 15px;
        font-size: 16px;
        line-height: 1.5;
    }}
    
    .quiz-options {{
        margin: 15px 0;
    }}
    
    .quiz-option {{
        display: block !important;
        margin: 10px 0;
        padding: 12px 15px;
        border: 2px solid #e0e0e0 !important;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
        background: #ffffff !important;
        color: #333333 !important;
        font-size: 16px !important;
        font-weight: normal !important;
    }}
    
    .quiz-option:hover {{
        background-color: #f0f8ff !important;
        border-color: #1976d2 !important;
    }}
    
    .quiz-option input[type="radio"] {{
        margin-right: 10px;
        accent-color: #1976d2;
        width: 18px !important;
        height: 18px !important;
        background-color: #ffffff !important;
        border: 2px solid #1976d2 !important;
        border-radius: 50% !important;
    }}
    
    .quiz-option input[type="radio"]:checked {{
        background-color: #1976d2 !important;
        border-color: #1976d2 !important;
    }}
    
    .quiz-option input[type="radio"]:hover {{
        border-color: #0d47a1 !important;
    }}
    
    .quiz-option span {{
        color: #333333 !important;
        font-size: 16px !important;
    }}
    
    .quiz-option.correct {{
        background-color: #e8f5e8 !important;
        border-color: #4caf50 !important;
        color: #2e7d32 !important;
    }}
    
    .quiz-option.correct span {{
        color: #2e7d32 !important;
    }}
    
    .quiz-option.wrong {{
        background-color: #ffebee !important;
        border-color: #f44336 !important;
        color: #c62828 !important;
    }}
    
    .quiz-option.wrong span {{
        color: #c62828 !important;
    }}
    
    .quiz-option input[type="text"] {{
        width: 100%;
        padding: 10px;
        border: 2px solid #e0e0e0 !important;
        border-radius: 4px;
        font-size: 16px !important;
        color: #333333 !important;
        background: #ffffff !important;
    }}
    
    .quiz-option input[type="text"]:focus {{
        outline: none;
        border-color: #1976d2 !important;
    }}
    
    .quiz-option input[type="text"].correct {{
        background-color: #e8f5e8 !important;
        border-color: #4caf50 !important;
    }}
    
    .quiz-option input[type="text"].wrong {{
        background-color: #ffebee !important;
        border-color: #f44336 !important;
    }}
    
    .quiz-submit {{
        background: #4caf50 !important;
        color: white !important;
        padding: 15px 30px;
        border: none !important;
        border-radius: 6px;
        cursor: pointer;
        font-size: 18px !important;
        font-weight: bold !important;
        margin-top: 30px;
        display: block;
        margin-left: auto;
        margin-right: auto;
        transition: background-color 0.2s;
    }}
    
    .quiz-submit:hover {{
        background: #45a049 !important;
    }}
    
    .quiz-submit:disabled {{
        background: #cccccc !important;
        cursor: not-allowed;
    }}
    
    .quiz-results {{
        margin-top: 30px;
        padding: 20px;
        background: #f5f5f5 !important;
        border-radius: 8px;
        color: #333333 !important;
    }}
    
    .quiz-results h3 {{
        color: #1976d2 !important;
        margin-bottom: 15px;
    }}
    
    .explanation {{
        margin-top: 15px;
        padding: 15px;
        background: #e3f2fd !important;
        border-radius: 6px;
        color: #333333 !important;
    }}
    
    .explanation p {{
        margin: 0;
        font-size: 14px;
        color: #333333 !important;
    }}
    
    .unanswered {{
        border-color: #ff9800 !important;
        background-color: #fff3e0 !important;
    }}
    </style>
    
    <div class="quiz-container">
        <h2>{quiz_data.get('title', 'Generated Quiz')}</h2>
        <form id="quiz-form">
    """
    
    for question in quiz_data.get('questions', []):
        q_id = question['id']
        q_type = question['type']
        q_text = question['question']
        
        html += f"""
        <div class="quiz-question" data-question-id="{q_id}">
            <h3>Question {q_id}</h3>
            <p>{q_text}</p>
        """
        
        if q_type == 'multiple_choice':
            html += '<div class="quiz-options">'
            for i, option in enumerate(question['options']):
                html += f"""
                <label class="quiz-option">
                    <input type="radio" name="q{q_id}" value="{i}" data-correct="{i == question['correct']}">
                    <span>{option}</span>
                </label>
                """
            html += '</div>'
            
        elif q_type == 'true_false':
            html += f"""
            <div class="quiz-options">
                <label class="quiz-option">
                    <input type="radio" name="q{q_id}" value="true" data-correct="{question['correct']}">
                    <span>True</span>
                </label>
                <label class="quiz-option">
                    <input type="radio" name="q{q_id}" value="false" data-correct="{not question['correct']}">
                    <span>False</span>
                </label>
            </div>
            """
            
        elif q_type == 'short_answer':
            html += f"""
            <div class="quiz-options">
                <input type="text" name="q{q_id}" placeholder="Your answer..." data-correct="{question['correct']}" style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 4px; font-size: 16px; color: #333333; background: #ffffff;">
            </div>
            """
        
        html += f"""
            <div class="explanation" style="display: none;">
                <p><strong>Explanation:</strong> {question['explanation']}</p>
            </div>
        </div>
        """
    
    html += """
            <button type="button" class="quiz-submit" id="submit-btn">Submit Quiz</button>
        </form>
        <div id="quiz-results" class="quiz-results" style="display: none;">
            <h3>Quiz Results</h3>
            <p id="score-display"></p>
            <button type="button" id="explain-btn">Show Explanations</button>
        </div>
    </div>
    
    <script>
    // Define functions immediately
    window.submitQuiz = function() {
        alert('Submit button clicked!');
        console.log('Submit quiz clicked!');
        
        const form = document.getElementById('quiz-form');
        if (!form) {
            alert('Quiz form not found!');
            return;
        }
        
        const questions = form.querySelectorAll('.quiz-question');
        let correct = 0;
        let total = questions.length;
        
        alert('Found ' + total + ' questions');
        
        questions.forEach(question => {
            const inputs = question.querySelectorAll('input');
            let answered = false;
            
            inputs.forEach(input => {
                if (input.type === 'radio' && input.checked) {
                    answered = true;
                    if (input.dataset.correct === 'true') {
                        correct++;
                        input.parentElement.classList.add('correct');
                    } else {
                        input.parentElement.classList.add('wrong');
                    }
                } else if (input.type === 'text' && input.value.trim()) {
                    answered = true;
                    const userAnswer = input.value.trim().toLowerCase();
                    const correctAnswer = input.dataset.correct.toLowerCase();
                    if (userAnswer === correctAnswer) {
                        correct++;
                        input.classList.add('correct');
                    } else {
                        input.classList.add('wrong');
                    }
                }
            });
            
            if (!answered) {
                question.classList.add('unanswered');
            }
        });
        
        const score = Math.round((correct / total) * 100);
        const scoreDisplay = document.getElementById('score-display');
        const resultsDiv = document.getElementById('quiz-results');
        
        if (scoreDisplay) {
            scoreDisplay.textContent = 'You scored ' + correct + '/' + total + ' (' + score + '%)';
        }
        if (resultsDiv) {
            resultsDiv.style.display = 'block';
        }
        
        alert('Score: ' + correct + '/' + total + ' (' + score + '%)');
        
        // Disable form
        form.querySelectorAll('input, button').forEach(el => el.disabled = true);
    };
    
    window.showExplanations = function() {
        document.querySelectorAll('.explanation').forEach(el => {
            el.style.display = 'block';
        });
    };
    
    // Initialize immediately
    (function() {
        console.log('Quiz script loading...');
        
        // Add event listeners
        setTimeout(function() {
            const submitBtn = document.getElementById('submit-btn');
            const explainBtn = document.getElementById('explain-btn');
            
            if (submitBtn) {
                submitBtn.addEventListener('click', window.submitQuiz);
                console.log('Submit button handler added');
            } else {
                console.log('Submit button not found');
            }
            
            if (explainBtn) {
                explainBtn.addEventListener('click', window.showExplanations);
                console.log('Explanations button handler added');
            }
        }, 100);
    })();
    </script>
    """
    
    return html

def study_chat(message: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
    """Handle study assistant chat."""
    global study_agent
    
    if study_agent is None:
        return "Please upload files first.", history
    
    if not message.strip():
        return "", history
    
    try:
        from langchain_core.messages import HumanMessage
        result = study_agent.invoke({"messages": [HumanMessage(content=message)]})
        response = result['messages'][-1].content
        
        history.append([message, response])
        return "", history
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        history.append([message, error_msg])
        return "", history

def start_pomodoro(work_minutes: int, break_minutes: int) -> Tuple[str, str, str]:
    """Start or reset the Pomodoro timer."""
    global pomodoro_state
    
    pomodoro_state = {
        "is_running": True,
        "time_left": work_minutes * 60,
        "is_break": False,
        "sessions_completed": pomodoro_state["sessions_completed"]
    }
    
    return f"Timer started! {work_minutes} minutes of focused study time.", "Work", f"Sessions completed: {pomodoro_state['sessions_completed']}"

def pause_pomodoro() -> Tuple[str, str, str]:
    """Pause or resume the Pomodoro timer."""
    global pomodoro_state
    
    if pomodoro_state["is_running"]:
        pomodoro_state["is_running"] = False
        return "Timer paused.", "Paused", f"Sessions completed: {pomodoro_state['sessions_completed']}"
    else:
        pomodoro_state["is_running"] = True
        return "Timer resumed.", "Work" if not pomodoro_state["is_break"] else "Break", f"Sessions completed: {pomodoro_state['sessions_completed']}"

def reset_pomodoro() -> Tuple[str, str, str]:
    """Reset the Pomodoro timer."""
    global pomodoro_state
    
    pomodoro_state = {
        "is_running": False,
        "time_left": 25 * 60,
        "is_break": False,
        "sessions_completed": 0
    }
    
    return "Timer reset.", "Ready", "Sessions completed: 0"

def update_timer() -> Tuple[str, str, str]:
    """Update the timer display (called by JavaScript)."""
    global pomodoro_state
    
    if not pomodoro_state["is_running"]:
        return f"Time left: {pomodoro_state['time_left']//60:02d}:{pomodoro_state['time_left']%60:02d}", "Paused", f"Sessions completed: {pomodoro_state['sessions_completed']}"
    
    if pomodoro_state["time_left"] > 0:
        pomodoro_state["time_left"] -= 1
        status = "Break" if pomodoro_state["is_break"] else "Work"
        return f"Time left: {pomodoro_state['time_left']//60:02d}:{pomodoro_state['time_left']%60:02d}", status, f"Sessions completed: {pomodoro_state['sessions_completed']}"
    else:
        # Timer finished
        if pomodoro_state["is_break"]:
            # Break finished, start work
            pomodoro_state["is_break"] = False
            pomodoro_state["time_left"] = 25 * 60
            pomodoro_state["sessions_completed"] += 1
            return "Break finished! Time to work.", "Work", f"Sessions completed: {pomodoro_state['sessions_completed']}"
        else:
            # Work finished, start break
            pomodoro_state["is_break"] = True
            pomodoro_state["time_left"] = 5 * 60
            return "Work session finished! Take a break.", "Break", f"Sessions completed: {pomodoro_state['sessions_completed']}"

def get_wrong_answers() -> str:
    """Get the list of wrong answers for review."""
    global wrong_answers
    
    if not wrong_answers:
        return "No wrong answers to review yet. Take a quiz first!"
    
    review_html = "<div class='wrong-answers-review'>"
    review_html += "<h2>Wrong Answer Review</h2>"
    
    for i, (question, user_answer, correct_answer, explanation) in enumerate(wrong_answers, 1):
        review_html += f"""
        <div class='wrong-answer-item'>
            <h3>Question {i}</h3>
            <p><strong>Question:</strong> {question}</p>
            <p><strong>Your Answer:</strong> <span class='wrong'>{user_answer}</span></p>
            <p><strong>Correct Answer:</strong> <span class='correct'>{correct_answer}</span></p>
            <p><strong>Explanation:</strong> {explanation}</p>
        </div>
        """
    
    review_html += "</div>"
    return review_html

def clear_wrong_answers() -> str:
    """Clear the wrong answers history."""
    global wrong_answers
    wrong_answers = []
    return "Wrong answers cleared."

# Custom CSS for styling
css = """
.quiz-container {
    font-family: 'Google Sans', Arial, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background: #ffffff;
    color: #333333;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.quiz-container h2 {
    color: #1976d2;
    text-align: center;
    margin-bottom: 30px;
    font-size: 28px;
}

.quiz-question {
    margin-bottom: 30px;
    padding: 20px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    background: #fafafa;
    color: #333333;
}

.quiz-question h3 {
    color: #1976d2;
    margin-bottom: 15px;
    font-size: 18px;
}

.quiz-question p {
    color: #333333;
    margin-bottom: 15px;
    font-size: 16px;
    line-height: 1.5;
}

.quiz-options {
    margin: 15px 0;
}

.quiz-option {
    display: block;
    margin: 10px 0;
    padding: 12px 15px;
    border: 2px solid #e0e0e0;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    background: #ffffff;
    color: #333333;
}

.quiz-option:hover {
    background-color: #f0f8ff;
    border-color: #1976d2;
}

.quiz-option input[type="radio"] {
    margin-right: 10px;
}

.quiz-option.correct {
    background-color: #e8f5e8;
    border-color: #4caf50;
    color: #2e7d32;
}

.quiz-option.wrong {
    background-color: #ffebee;
    border-color: #f44336;
    color: #c62828;
}

.quiz-option input[type="text"] {
    width: 100%;
    padding: 10px;
    border: 2px solid #e0e0e0;
    border-radius: 4px;
    font-size: 16px;
    color: #333333;
    background: #ffffff;
}

.quiz-option input[type="text"]:focus {
    outline: none;
    border-color: #1976d2;
}

.quiz-option input[type="text"].correct {
    background-color: #e8f5e8;
    border-color: #4caf50;
}

.quiz-option input[type="text"].wrong {
    background-color: #ffebee;
    border-color: #f44336;
}

.quiz-submit {
    background: #4caf50;
    color: white;
    padding: 15px 30px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 18px;
    font-weight: bold;
    margin-top: 30px;
    display: block;
    margin-left: auto;
    margin-right: auto;
    transition: background-color 0.2s;
}

.quiz-submit:hover {
    background: #45a049;
}

.quiz-submit:disabled {
    background: #cccccc;
    cursor: not-allowed;
}

.quiz-results {
    margin-top: 30px;
    padding: 20px;
    background: #f5f5f5;
    border-radius: 8px;
    color: #333333;
}

.quiz-results h3 {
    color: #1976d2;
    margin-bottom: 15px;
}

.explanation {
    margin-top: 15px;
    padding: 15px;
    background: #e3f2fd;
    border-radius: 6px;
    color: #333333;
}

.explanation p {
    margin: 0;
    font-size: 14px;
}

.unanswered {
    border-color: #ff9800 !important;
    background-color: #fff3e0 !important;
}

.wrong-answers-review {
    font-family: 'Google Sans', Arial, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    color: #333333;
}

.wrong-answer-item {
    margin-bottom: 30px;
    padding: 20px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    background: #fafafa;
    color: #333333;
}

.wrong-answer-item h3 {
    color: #1976d2;
    margin-bottom: 15px;
}

.wrong {
    color: #f44336;
    font-weight: bold;
}

.correct {
    color: #4caf50;
    font-weight: bold;
}

.pomodoro-timer {
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    margin: 20px 0;
    padding: 20px;
    background: #e3f2fd;
    border-radius: 8px;
    color: #1976d2;
}
"""

# Create the Gradio interface
with gr.Blocks(css=css, title="RAG Study Tool") as app:
    gr.Markdown("# 🎓 RAG Study Tool")
    gr.Markdown("Upload your study materials and create interactive quizzes or get help with Q&A!")
    
    with gr.Tabs():
        # Tab 1: Quiz Generator
        with gr.Tab("📝 Quiz Generator"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Upload Study Materials")
                    file_upload = gr.File(
                        file_count="multiple",
                        file_types=[".pdf", ".docx", ".txt", ".md", ".png", ".jpg", ".jpeg"],
                        label="Upload files (PDF, DOCX, TXT, MD, Images)"
                    )
                    process_btn = gr.Button("Process Files", variant="primary")
                    file_status = gr.Textbox(label="File Status", interactive=False)
                
                with gr.Column(scale=2):
                    gr.Markdown("### Quiz Configuration")
                    with gr.Row():
                        num_questions = gr.Slider(5, 50, value=10, step=1, label="Number of Questions")
                        difficulty = gr.Dropdown(["Easy", "Medium", "Hard"], value="Medium", label="Difficulty")
                    
                    question_types = gr.CheckboxGroup(
                        ["Multiple Choice", "True/False", "Short Answer"],
                        value=["Multiple Choice"],
                        label="Question Types"
                    )
                    
                    generate_btn = gr.Button("Generate Quiz", variant="primary")
                    quiz_status = gr.Textbox(label="Quiz Status", interactive=False)
            
            gr.Markdown("### Generated Quiz")
            quiz_display = gr.HTML(label="Interactive Quiz")
        
        # Tab 2: Study Assistant
        with gr.Tab("💬 Study Assistant"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Pomodoro Timer")
                    with gr.Row():
                        work_minutes = gr.Slider(5, 60, value=25, step=5, label="Work (minutes)")
                        break_minutes = gr.Slider(5, 30, value=5, step=5, label="Break (minutes)")
                    
                    with gr.Row():
                        start_btn = gr.Button("Start Timer", variant="primary")
                        pause_btn = gr.Button("Pause/Resume")
                        reset_btn = gr.Button("Reset")
                    
                    timer_display = gr.Textbox(label="Timer", interactive=False)
                    timer_status = gr.Textbox(label="Status", interactive=False)
                    sessions_display = gr.Textbox(label="Sessions", interactive=False)
                
                with gr.Column(scale=2):
                    gr.Markdown("### Chat with Study Materials")
                    study_chatbot = gr.Chatbot(label="Study Assistant", height=400)
                    study_input = gr.Textbox(label="Ask a question about your study materials", placeholder="What would you like to know?")
                    study_submit = gr.Button("Send", variant="primary")
        
        # Tab 3: Wrong Answer Review
        with gr.Tab("📊 Wrong Answer Review"):
            gr.Markdown("### Review Your Mistakes")
            review_btn = gr.Button("Load Wrong Answers", variant="primary")
            clear_btn = gr.Button("Clear History", variant="secondary")
            wrong_answers_display = gr.HTML(label="Wrong Answer Review")
    
    # Event handlers
    process_btn.click(
        process_uploaded_files,
        inputs=[file_upload],
        outputs=[file_status, quiz_status]
    )
    
    generate_btn.click(
        generate_quiz,
        inputs=[num_questions, difficulty, question_types],
        outputs=[quiz_display, quiz_status]
    )
    
    study_submit.click(
        study_chat,
        inputs=[study_input, study_chatbot],
        outputs=[study_input, study_chatbot]
    )
    
    study_input.submit(
        study_chat,
        inputs=[study_input, study_chatbot],
        outputs=[study_input, study_chatbot]
    )
    
    start_btn.click(
        start_pomodoro,
        inputs=[work_minutes, break_minutes],
        outputs=[timer_display, timer_status, sessions_display]
    )
    
    pause_btn.click(
        pause_pomodoro,
        outputs=[timer_display, timer_status, sessions_display]
    )
    
    reset_btn.click(
        reset_pomodoro,
        outputs=[timer_display, timer_status, sessions_display]
    )
    
    review_btn.click(
        get_wrong_answers,
        outputs=[wrong_answers_display]
    )
    
    clear_btn.click(
        clear_wrong_answers,
        outputs=[wrong_answers_display]
    )

if __name__ == "__main__":
    app.launch(share=True, debug=True)
