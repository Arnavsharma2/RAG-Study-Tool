#!/usr/bin/env python3
"""
RAG Study Tool - Main Entry Point

This is the main entry point for the RAG Study Tool.
It launches the Gradio web interface with all features:
- Quiz Generator
- Study Assistant with Pomodoro Timer
- Wrong Answer Review
"""

from app import app

if __name__ == "__main__":
    print("🎓 Starting RAG Study Tool...")
    print("📚 Features available:")
    print("   • Upload multiple file formats (PDF, DOCX, TXT, MD, Images)")
    print("   • Generate interactive quizzes")
    print("   • Study assistant with Q&A")
    print("   • Pomodoro timer for focused study")
    print("   • Wrong answer review and tracking")
    print("\n🌐 Launching web interface...")
    
    app.launch(
        share=True,
        debug=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
