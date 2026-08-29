"""
RAG Cơ Bản với LangChain
=========================

RAG = Retrieval-Augmented Generation
- Retrieval: Tìm kiếm tài liệu liên quan
- Augmented: Thêm context vào câu hỏi
- Generation: LLM tạo câu trả lời dựa trên context

3 bước chính:
1. LOAD: Đọc tài liệu từ files
2. SPLIT: Chia nhỏ tài liệu thành chunks
3. EMBED + SEARCH: Tạo vectors, tìm chunks liên quan
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv(Path(__file__).parent.parent / ".env")

# Set env vars cho LangChain Azure
os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_AI_API_KEY", "")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT", "")
os.environ["AZURE_OPENAI_API_VERSION"] = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
os.environ["OPENAI_API_VERSION"] = os.environ["AZURE_OPENAI_API_VERSION"]


def step1_load_documents():
    """
    BƯỚC 1: LOAD DOCUMENTS
    ====================
    Đọc tất cả .md files trong thư mục docs/
    """
    print("\n" + "=" * 50)
    print("BƯỚC 1: LOAD DOCUMENTS")
    print("=" * 50)
    
    from langchain_community.document_loaders import DirectoryLoader, TextLoader
    
    # Load tất cả .md files trong thư mục docs/
    loader = DirectoryLoader(
        path=str(Path(__file__).parent / "docs"),
        glob="**/*.md",  # Chỉ load file .md
        loader_cls=TextLoader,  # Dùng TextLoader cho .md
    )
    
    documents = loader.load()
    
    print(f"Đã load {len(documents)} documents:")
    for doc in documents:
        print(f"  - File: {Path(doc.metadata['source']).name}")
        print(f"    Nội dung: {doc.page_content[:100]}...")
    
    return documents


def step2_split_documents(documents):
    """
    BƯỚC 2: SPLIT DOCUMENTS
    =======================
    Chia tài liệu thành chunks nhỏ để dễ tìm kiếm
    
    Tại sao cần split?
    - Documents có thể dài (hàng nghìn từ)
    - Embedding model có giới hạn input
    - Chunks nhỏ = tìm kiếm chính xác hơn
    """
    print("\n" + "=" * 50)
    print("BƯỚC 2: SPLIT DOCUMENTS")
    print("=" * 50)
    
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    # Tạo splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,  # Mỗi chunk tối đa 200 ký tự
        chunk_overlap=20,  # Overlap 20 ký tự giữa các chunks
    )
    
    # Split documents
    chunks = text_splitter.split_documents(documents)
    
    print(f"Đã chia thành {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"  - Chunk {i+1}: {len(chunk.page_content)} ký tự")
        print(f"    \"{chunk.page_content[:80]}...\"")
    
    return chunks


def step3_create_embeddings_and_store(chunks):
    """
    BƯỚC 3: EMBEDDINGS + VECTOR STORE
    =================================
    
    Embedding là gì?
    - Chuyển text thành vector số (list of floats)
    - Ví dụ: "What is P/E?" → [0.1, 0.5, -0.3, ...]
    - Texts giống nhau → vectors giống nhau
    
    Vector Store là gì?
    - Database lưu vectors
    - Tìm kiếm nhanh theo similarity
    - FAISS là một trong những thư viện phổ biến nhất
    """
    print("\n" + "=" * 50)
    print("BƯỚC 3: EMBEDDINGS + VECTOR STORE")
    print("=" * 50)
    
    from langchain_openai import AzureOpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    
    # Tạo embeddings model
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment="text-embedding-3-large",
    )
    
    print("Đang tạo embeddings cho các chunks...")
    print("(Mỗi chunk được chuyển thành vector 3072 chiều)")
    
    # Tạo vector store từ chunks
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    print(f"Đã tạo FAISS vector store với {len(chunks)} vectors")
    
    return vectorstore


def step4_search(vectorstore, query):
    """
    BƯỚC 4: SEARCH SIMILAR DOCUMENTS
    =================================
    
    Cách hoạt động:
    1. Chuyển query thành vector
    2. So sánh với tất cả vectors trong store
    3. Trả về K vectors gần nhất (similarity search)
    """
    print("\n" + "=" * 50)
    print("BƯỚC 4: SEARCH")
    print("=" * 50)
    
    print(f"Query: \"{query}\"")
    
    # Tìm kiếm 2 chunks liên quan nhất
    results = vectorstore.similarity_search(query, k=2)
    
    print(f"\nTìm thấy {len(results)} chunks liên quan:")
    for i, doc in enumerate(results):
        print(f"\n  Result {i+1}:")
        print(f"    \"{doc.page_content}\"")
    
    return results


def step5_generate_answer(vectorstore, query):
    """
    BƯỚC 5: GENERATE ANSWER (RAG hoàn chỉnh)
    =========================================
    
    RAG pipeline:
    1. User hỏi câu hỏi
    2. Tìm kiếm tài liệu liên quan (Retrieval)
    3. Ghép context + câu hỏi (Augmented)
    4. Gửi cho LLM để tạo câu trả lời (Generation)
    """
    print("\n" + "=" * 50)
    print("BƯỚC 5: GENERATE ANSWER (RAG)")
    print("=" * 50)
    
    from langchain_openai import AzureChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
    
    # Tạo LLM
    llm = AzureChatOpenAI(
        azure_deployment="gpt-4o",
        temperature=0,
    )
    
    # Tạo retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    
    # Template prompt
    template = """Answer the question based ONLY on the following context.
If you don't know, say "I don't know".

Context:
{context}

Question: {question}

Answer:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # Hàm format documents
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Tạo RAG chain (LCEL syntax)
    rag_chain = (
        {
            "context": retriever | format_docs,  # Lấy docs và format
            "question": RunnablePassthrough(),    # Pass question nguyên xi
        }
        | prompt    # Tạo prompt
        | llm      # Gọi LLM
        | StrOutputParser()  # Lấy text output
    )
    
    print(f"Question: \"{query}\"")
    print("\nĐang chạy RAG pipeline...")
    
    # Chạy chain
    answer = rag_chain.invoke(query)
    
    print(f"\nAnswer: {answer}")
    
    return answer


def main():
    print("=" * 50)
    print("  RAG CƠ BẢN VỚI LANGCHAIN")
    print("=" * 50)
    print("\nRAG = Retrieval-Augmented Generation")
    print("Thêm context vào LLM để có câu trả lời chính xác hơn")
    
    # Bước 1: Load documents
    documents = step1_load_documents()
    
    # Bước 2: Split
    chunks = step2_split_documents(documents)
    
    # Bước 3: Embeddings + Vector store
    vectorstore = step3_create_embeddings_and_store(chunks)
    
    # Bước 4: Test search
    query1 = "What is P/E ratio?"
    step4_search(vectorstore, query1)
    
    # Bước 5: RAG hoàn chỉnh
    query2 = "When is RSI considered overbought?"
    step5_generate_answer(vectorstore, query2)
    
    # Test thêm
    query3 = "Explain P/E ratio with example"
    step5_generate_answer(vectorstore, query3)
    
    print("\n" + "=" * 50)
    print("  HOÀN THÀNH!")
    print("=" * 50)


if __name__ == "__main__":
    main()
