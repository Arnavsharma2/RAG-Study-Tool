#!/usr/bin/env python3
"""
Integration test for RAG Study Tool
Tests that all components are properly connected
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        import app
        print("✅ app.py imports successfully")
    except Exception as e:
        print(f"❌ Failed to import app.py: {e}")
        return False
    
    try:
        import rag_chatbot
        print("✅ rag_chatbot.py imports successfully")
    except Exception as e:
        print(f"❌ Failed to import rag_chatbot.py: {e}")
        return False
    
    try:
        import main
        print("✅ main.py imports successfully")
    except Exception as e:
        print(f"❌ Failed to import main.py: {e}")
        return False
    
    return True

def test_functions_exist():
    """Test that required functions exist."""
    print("\nTesting function existence...")
    try:
        from app import (
            process_uploaded_files,
            generate_quiz,
            study_chat,
            start_pomodoro,
            pause_pomodoro,
            reset_pomodoro,
            update_timer,
            get_wrong_answers,
            clear_wrong_answers,
            submit_quiz_results
        )
        print("✅ All app.py functions found")
    except ImportError as e:
        print(f"❌ Missing function in app.py: {e}")
        return False
    
    try:
        from rag_chatbot import (
            process_documents,
            create_study_agent,
            create_quiz_agent,
            load_pdf,
            load_docx,
            load_txt,
            load_markdown,
            load_image
        )
        print("✅ All rag_chatbot.py functions found")
    except ImportError as e:
        print(f"❌ Missing function in rag_chatbot.py: {e}")
        return False
    
    return True

def test_gradio_app():
    """Test that Gradio app is properly configured."""
    print("\nTesting Gradio app configuration...")
    try:
        from app import app
        
        # Check that app is a Gradio Blocks instance
        import gradio as gr
        if not isinstance(app, gr.Blocks):
            print("❌ app is not a Gradio Blocks instance")
            return False
        
        print("✅ Gradio app is properly configured")
        return True
    except Exception as e:
        print(f"❌ Failed to verify Gradio app: {e}")
        return False

def test_environment():
    """Test environment configuration."""
    print("\nTesting environment configuration...")
    
    # Check .env file
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    print("✅ .env file exists")
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set (app will not work)")
        return True  # Don't fail the test, just warn
    elif api_key == 'your_openai_api_key_here':
        print("⚠️  OPENAI_API_KEY is still the placeholder value")
        return True  # Don't fail the test, just warn
    else:
        print("✅ OPENAI_API_KEY is configured")
    
    return True

def test_component_connections():
    """Test that components are properly connected."""
    print("\nTesting component connections...")
    
    try:
        from app import current_vectorstore, study_agent, quiz_agent, wrong_answers, pomodoro_state
        print("✅ Global state variables initialized")
    except ImportError as e:
        print(f"❌ Missing global state variable: {e}")
        return False
    
    try:
        from rag_chatbot import llm, embeddings, text_splitter
        print("✅ RAG components initialized")
    except ImportError as e:
        print(f"❌ Missing RAG component: {e}")
        return False
    
    return True

def test_timer_integration():
    """Test that Pomodoro timer is properly integrated."""
    print("\nTesting Pomodoro timer integration...")
    
    try:
        from app import start_pomodoro, pause_pomodoro, reset_pomodoro, update_timer, pomodoro_state
        
        # Test timer initialization
        if pomodoro_state["time_left"] != 25 * 60:
            print(f"❌ Timer initial state incorrect: {pomodoro_state}")
            return False
        
        # Test start function
        result = start_pomodoro(25, 5)
        if not isinstance(result, tuple) or len(result) != 3:
            print("❌ start_pomodoro doesn't return proper tuple")
            return False
        
        # Reset state
        reset_pomodoro()
        
        print("✅ Pomodoro timer properly integrated")
        return True
    except Exception as e:
        print(f"❌ Timer integration test failed: {e}")
        return False

def main():
    """Run all integration tests."""
    print("=" * 60)
    print("RAG Study Tool - Integration Test")
    print("=" * 60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Functions", test_functions_exist),
        ("Gradio App", test_gradio_app),
        ("Environment", test_environment),
        ("Component Connections", test_component_connections),
        ("Timer Integration", test_timer_integration)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} test crashed: {e}")
            results.append((name, False))
        print()
    
    print("=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    passed = 0
    failed = 0
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:.<40} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Total: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All integration tests passed!")
        print("   The application is ready to run: python main.py")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Integration test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
