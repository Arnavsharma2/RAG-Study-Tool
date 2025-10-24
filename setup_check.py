#!/usr/bin/env python3
"""
Setup verification script for RAG Study Tool
Checks dependencies and configuration before starting the application
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'gradio', 'langchain', 'langchain_openai', 'langchain_community',
        'langchain_chroma', 'chromadb', 'dotenv', 'docx2txt', 'pytesseract',
        'PIL', 'markdown', 'langgraph'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
            elif package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n⚠️  Missing packages detected!")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required keys."""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found")
        print("   A template .env file has been created.")
        print("   Please add your OpenAI API key to the .env file")
        return False
    
    print("✅ .env file exists")
    
    # Check if API key is set
    with open(env_path, 'r') as f:
        content = f.read()
        if 'your_openai_api_key_here' in content or 'OPENAI_API_KEY=' not in content:
            print("⚠️  OpenAI API key not configured in .env file")
            print("   Please set your OPENAI_API_KEY in the .env file")
            print("   Get your API key from: https://platform.openai.com/api-keys")
            return False
    
    print("✅ OpenAI API key appears to be configured")
    return True

def check_tesseract():
    """Check if Tesseract OCR is installed (required for image processing)."""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR is installed")
        return True
    except Exception:
        print("⚠️  Tesseract OCR not found (optional, needed for image text extraction)")
        print("   Install: sudo apt-get install tesseract-ocr (Linux)")
        print("   Install: brew install tesseract (macOS)")
        return True  # Non-critical, return True

def main():
    """Run all setup checks."""
    print("=" * 60)
    print("RAG Study Tool - Setup Verification")
    print("=" * 60)
    print()
    
    print("Checking Python version...")
    python_ok = check_python_version()
    print()
    
    print("Checking dependencies...")
    deps_ok = check_dependencies()
    print()
    
    print("Checking environment configuration...")
    env_ok = check_env_file()
    print()
    
    print("Checking optional dependencies...")
    check_tesseract()
    print()
    
    print("=" * 60)
    if python_ok and deps_ok and env_ok:
        print("✅ All checks passed! You're ready to run the application.")
        print("   Run: python main.py")
    else:
        print("⚠️  Some issues need to be resolved before running the application.")
        print("   Please fix the issues above and run this script again.")
    print("=" * 60)
    
    return python_ok and deps_ok and env_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
