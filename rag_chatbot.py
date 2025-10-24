from dotenv import load_dotenv
import os
import tempfile
import uuid
from typing import List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from operator import add as add_messages
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_core.documents import Document
import docx2txt
import markdown
from PIL import Image
import pytesseract

# Load environment variables
load_dotenv()

# Initialize LLM and embeddings
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Text splitter configuration
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""]
)

def load_pdf(file_path: str) -> List[Document]:
    """Load and process PDF files."""
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        print(f"Loaded PDF: {len(pages)} pages")
        return pages
    except Exception as e:
        print(f"Error loading PDF {file_path}: {e}")
        return []

def load_docx(file_path: str) -> List[Document]:
    """Load and process DOCX files."""
    try:
        text = docx2txt.process(file_path)
        if text.strip():
            doc = Document(
                page_content=text,
                metadata={"source": os.path.basename(file_path), "file_type": "docx"}
            )
            print(f"Loaded DOCX: {len(text)} characters")
            return [doc]
        return []
    except Exception as e:
        print(f"Error loading DOCX {file_path}: {e}")
        return []

def load_txt(file_path: str) -> List[Document]:
    """Load and process TXT files."""
    try:
        loader = TextLoader(file_path, encoding='utf-8')
        docs = loader.load()
        print(f"Loaded TXT: {len(docs)} documents")
        return docs
    except Exception as e:
        print(f"Error loading TXT {file_path}: {e}")
        return []

def load_markdown(file_path: str) -> List[Document]:
    """Load and process Markdown files."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Convert markdown to HTML for better processing
        html_content = markdown.markdown(content)
        
        doc = Document(
            page_content=content,  # Keep original markdown for better chunking
            metadata={"source": os.path.basename(file_path), "file_type": "markdown", "html": html_content}
        )
        print(f"Loaded Markdown: {len(content)} characters")
        return [doc]
    except Exception as e:
        print(f"Error loading Markdown {file_path}: {e}")
        return []

def load_image(file_path: str) -> List[Document]:
    """Load and process images using OCR."""
    try:
        # Open image and extract text using OCR
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        
        if text.strip():
            doc = Document(
                page_content=text,
                metadata={"source": os.path.basename(file_path), "file_type": "image"}
            )
            print(f"Loaded Image: {len(text)} characters via OCR")
            return [doc]
        return []
    except Exception as e:
        print(f"Error loading image {file_path}: {e}")
        return []

def process_documents(file_paths: List[str]) -> Optional[Chroma]:
    """Process multiple uploaded files and create a unified vector store."""
    if not file_paths:
        return None
    
    all_documents = []
    file_info = []
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        file_ext = os.path.splitext(file_path)[1].lower()
        documents = []
        
        if file_ext == '.pdf':
            documents = load_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            documents = load_docx(file_path)
        elif file_ext == '.txt':
            documents = load_txt(file_path)
        elif file_ext == '.md':
            documents = load_markdown(file_path)
        elif file_ext in ['.png', '.jpg', '.jpeg']:
            documents = load_image(file_path)
        else:
            print(f"Unsupported file type: {file_ext}")
            continue
        
        if documents:
            all_documents.extend(documents)
            file_info.append({
                'filename': os.path.basename(file_path),
                'type': file_ext,
                'chunks': len(documents)
            })
    
    if not all_documents:
        print("No documents were successfully loaded.")
        return None
    
    # Split documents into chunks
    pages_split = text_splitter.split_documents(all_documents)
    
    # Add metadata to each chunk
    for i, doc in enumerate(pages_split):
        doc.metadata.update({
            'chunk_id': i,
            'total_chunks': len(pages_split)
        })
    
    # Create temporary vector store
    temp_dir = tempfile.mkdtemp()
    collection_name = f"study_docs_{uuid.uuid4().hex[:8]}"
    
    try:
        vectorstore = Chroma.from_documents(
            documents=pages_split,
            embedding=embeddings,
            persist_directory=temp_dir,
            collection_name=collection_name
        )
        print(f"Created vector store with {len(pages_split)} chunks from {len(file_info)} files")
        return vectorstore
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return None

def create_retriever_tool(vectorstore: Chroma):
    """Create a retriever tool for the given vector store."""
    retriever = vectorstore.as_retriever(
        search_type='similarity',
        search_kwargs={'k': 3}
    )

    @tool
    def retriever_tool(query: str) -> str:
        """
        Search and return relevant information from the uploaded study materials.
        Use this to find specific details about any topic covered in the documents.
        """
        docs = retriever.invoke(query)
        if not docs:
            return "I found no relevant information in the uploaded materials for that query. Please try rephrasing your question or ask about a different topic."
        
        results = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', 'Unknown')
            results.append(f"Source: {source}\n{doc.page_content}")
        
        return "\n\n---\n\n".join(results)
    
    return retriever_tool

def create_study_agent(vectorstore: Chroma):
    """Create a study assistant agent with strict adherence to uploaded materials."""
    retriever_tool = create_retriever_tool(vectorstore)
    tools = [retriever_tool]
    llm_with_tools = llm.bind_tools(tools)
    
    study_system_prompt = """
    You are a helpful study assistant. Your role is to help students learn and understand their study materials.

    IMPORTANT RULES:
    - ONLY answer questions based on the uploaded study materials
    - ALWAYS use the retriever tool to find relevant information before responding
    - If information is not in the uploaded materials, clearly state this
    - Cite specific sources when providing information
    - Be educational and encouraging
    - Help students understand concepts, not just memorize facts
    - Ask clarifying questions if the student's question is unclear

    When you find relevant information:
    - Explain it clearly and in your own words
    - Provide context and connections to other concepts
    - Suggest follow-up questions for deeper understanding
    - Always cite the source document

    If you cannot find relevant information in the materials:
    - Clearly state that the information is not available in the uploaded materials
    - Suggest what the student might look for in their materials
    - Offer to help with related topics that ARE covered
    """
    
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], add_messages]

    def should_continue(state: AgentState):
        """Check if the last message contains tool calls."""
        result = state['messages'][-1]
        return hasattr(result, 'tool_calls') and len(result.tool_calls) > 0

    def call_llm(state: AgentState) -> AgentState:
        """Call the LLM with the current state."""
        messages = list(state['messages'])
        messages = [SystemMessage(content=study_system_prompt)] + messages
        message = llm_with_tools.invoke(messages)
        return {'messages': [message]}

    def take_action(state: AgentState) -> AgentState:
        """Execute tool calls from the LLM's response."""
        tool_calls = state['messages'][-1].tool_calls
        results = []
        tools_dict = {tool.name: tool for tool in tools}
        
        for t in tool_calls:
            if t['name'] not in tools_dict:
                result = "Tool not available. Please try a different approach."
            else:
                result = tools_dict[t['name']].invoke(t['args'].get('query', ''))
            
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

        return {'messages': results}

    # Build the graph
    graph = StateGraph(AgentState)
    graph.add_node("llm", call_llm)
    graph.add_node("retriever_agent", take_action)

    graph.add_conditional_edges(
        "llm",
        should_continue,
        {True: "retriever_agent", False: END}
    )
    graph.add_edge("retriever_agent", "llm")
    graph.set_entry_point("llm")

    return graph.compile()

def create_quiz_agent(vectorstore: Chroma):
    """Create a quiz generation agent."""
    retriever_tool = create_retriever_tool(vectorstore)
    tools = [retriever_tool]
    llm_with_tools = llm.bind_tools(tools)
    
    quiz_system_prompt = """
    You are a quiz generation expert. Your role is to create comprehensive, educational quizzes based on the uploaded study materials.

    IMPORTANT RULES:
    - ONLY create questions based on the uploaded study materials
    - ALWAYS use the retriever tool to find relevant information before creating questions
    - Generate questions that test understanding, not just memorization
    - Include a mix of question types: multiple choice, true/false, and short answer
    - Make questions clear and unambiguous
    - Provide correct answers and explanations
    - Ensure questions cover different aspects of the material

    Question Types:
    1. Multiple Choice: 4 options, only one correct
    2. True/False: Clear statements that can be definitively answered
    3. Short Answer: Questions requiring brief explanations

    For each question:
    - Make it specific and focused
    - Avoid trick questions
    - Test different levels of understanding (basic facts, application, analysis)
    - Provide clear explanations for correct answers
    - Reference the source material

    Format your response as HTML with proper styling for a modern quiz interface.
    """
    
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], add_messages]
    
    def should_continue(state: AgentState):
        """Check if the last message contains tool calls."""
        result = state['messages'][-1]
        return hasattr(result, 'tool_calls') and len(result.tool_calls) > 0
    
    def call_llm(state: AgentState) -> AgentState:
        """Call the LLM with the current state."""
        messages = list(state['messages'])
        messages = [SystemMessage(content=quiz_system_prompt)] + messages
        message = llm_with_tools.invoke(messages)
        return {'messages': [message]}
    
    def take_action(state: AgentState) -> AgentState:
        """Execute tool calls from the LLM's response."""
        tool_calls = state['messages'][-1].tool_calls
        results = []
        tools_dict = {tool.name: tool for tool in tools}
        
        for t in tool_calls:
            if t['name'] not in tools_dict:
                result = "Tool not available. Please try a different approach."
            else:
                result = tools_dict[t['name']].invoke(t['args'].get('query', ''))
            
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        
        return {'messages': results}
    
    # Build the graph
    graph = StateGraph(AgentState)
    graph.add_node("llm", call_llm)
    graph.add_node("retriever_agent", take_action)
    
    graph.add_conditional_edges(
        "llm",
        should_continue,
        {True: "retriever_agent", False: END}
    )
    graph.add_edge("retriever_agent", "llm")
    graph.set_entry_point("llm")
    
    return graph.compile()

# CLI functionality (optional)
def run_cli():
    """Run the RAG agent in CLI mode (for testing)."""
    print("RAG Study Tool - CLI Mode")
    print("Upload files to use the web interface instead.")
    print("This CLI mode is for testing purposes only.")