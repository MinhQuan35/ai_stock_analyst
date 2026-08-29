"""
LangChain Agent - Main stock analyst agent
"""
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_agent as create_lc_agent
from langchain_community.callbacks import get_openai_callback
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from pathlib import Path

from .config import (
    AZURE_API_KEY, AZURE_ENDPOINT, AZURE_API_VERSION,
    CHAT_DEPLOYMENT, EMBEDDING_DEPLOYMENT,
)
from .tools import TOOLS


SYSTEM_PROMPT = """You are an AI Stock Analyst - Expert in Vietnamese and global stock markets.

Tasks:
1. Fundamental analysis (P/E, P/B, Dividend Yield)
2. Technical analysis (MA, RSI, MACD)
3. Investment suggestions based on goals
4. Profit potential calculations

Rules:
- ALWAYS include disclaimer: "This is analysis only, not investment advice"
- Never promise returns
- Use tools for accurate calculations
- Reply in English
- Ask for more info if missing"""


def get_llm(temperature: float = 0):
    """Get Azure OpenAI LLM."""
    # Use environment variables
    return AzureChatOpenAI(
        azure_deployment=CHAT_DEPLOYMENT,
        temperature=temperature,
    )


def get_embeddings():
    """Get Azure OpenAI embeddings."""
    return AzureOpenAIEmbeddings(
        azure_deployment=EMBEDDING_DEPLOYMENT,
    )


def create_agent():
    """Create a stock analyst agent with tool calling."""
    # Use new LangChain 1.2+ API
    # Use init_chat_model to support Azure
    from langchain.chat_models import init_chat_model
    
    llm = init_chat_model(
        f"azure_openai:{CHAT_DEPLOYMENT}",
        azure_deployment=CHAT_DEPLOYMENT,
    )
    
    agent = create_lc_agent(
        model=llm,
        tools=TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )
    
    return agent


def chat(message: str):
    """Chat with the agent."""
    agent = create_agent()
    
    with get_openai_callback() as cb:
        result = agent.invoke({
            "messages": [{"role": "user", "content": message}]
        })
        metrics = {
            "input_tokens": cb.prompt_tokens,
            "output_tokens": cb.completion_tokens,
            "total_tokens": cb.total_tokens,
            "total_cost_usd": cb.total_cost,
        }
    
    # Get the last assistant message
    messages = result.get("messages", [])
    output = messages[-1].content if messages else "No response"
    
    return {
        "response": output,
        "metrics": metrics,
    }


def create_rag_chain(data_dir: str = None):
    """Create RAG chain with knowledge base."""
    if data_dir is None:
        data_dir = str(Path(__file__).parent.parent / "data" / "knowledge")
    
    # Load documents
    loader = DirectoryLoader(
        data_dir,
        glob="**/*.md",
        loader_cls=TextLoader,
    )
    documents = loader.load()
    
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = text_splitter.split_documents(documents)
    
    # Create vector store
    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Create retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    return retriever, vectorstore


def rag_chat(message: str, retriever=None):
    """Chat with RAG context."""
    if retriever is None:
        retriever, _ = create_rag_chain()
    
    from langchain.chat_models import init_chat_model
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
    
    llm = init_chat_model(
        f"azure_openai:{CHAT_DEPLOYMENT}",
        azure_deployment=CHAT_DEPLOYMENT,
    )
    
    # Simple RAG using LCEL
    template = """Answer the question based only on the following context:

{context}

Question: {question}
"""
    prompt = ChatPromptTemplate.from_template(template)
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    with get_openai_callback() as cb:
        answer = rag_chain.invoke(message)
        # Get source documents separately
        source_docs = retriever.invoke(message)
        metrics = {
            "input_tokens": cb.prompt_tokens,
            "output_tokens": cb.completion_tokens,
            "total_cost_usd": cb.total_cost,
        }
    
    return {
        "response": answer,
        "sources": [doc.metadata.get("source", "") for doc in source_docs],
        "metrics": metrics,
    }
