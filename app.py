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
    
    Please create an interactive HTML quiz with:
    1. Clean, modern styling (similar to Google Forms)
    2. Question numbering
    3. Interactive elements (radio buttons, checkboxes, text inputs)
    4. Submit button
    5. JavaScript for instant feedback
    6. Score calculation
    7. Review mode for wrong answers
    
    Make sure questions are based only on the uploaded materials and test understanding, not just memorization.
    """
    
    try:
        from langchain_core.messages import HumanMessage
        result = quiz_agent.invoke({"messages": [HumanMessage(content=prompt)]})
        quiz_html = result['messages'][-1].content
        
        # Clear previous wrong answers
        wrong_answers = []
        
        return quiz_html, "Quiz generated successfully! Answer the questions and get instant feedback."
    except Exception as e:
        return f"Error generating quiz: {str(e)}", "Failed to generate quiz. Please try again."

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
            return "Break finished! Time to work.", "Work", f"Sessions completed: {pomodoro_state['sessions_completed']}"
        else:
            # Work finished, start break
            pomodoro_state["is_break"] = True
            pomodoro_state["time_left"] = 5 * 60
            pomodoro_state["sessions_completed"] += 1
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
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.quiz-question {
    margin-bottom: 30px;
    padding: 20px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    background: #fafafa;
}

.quiz-options {
    margin: 15px 0;
}

.quiz-option {
    margin: 10px 0;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.quiz-option:hover {
    background-color: #f0f0f0;
}

.quiz-option.selected {
    background-color: #e3f2fd;
    border-color: #2196f3;
}

.quiz-submit {
    background: #4caf50;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    margin-top: 20px;
}

.quiz-submit:hover {
    background: #45a049;
}

.quiz-results {
    margin-top: 20px;
    padding: 20px;
    background: #f5f5f5;
    border-radius: 8px;
}

.wrong-answers-review {
    font-family: 'Google Sans', Arial, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.wrong-answer-item {
    margin-bottom: 30px;
    padding: 20px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    background: #fafafa;
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
