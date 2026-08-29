# RAG Cơ Bản với LangChain

## RAG là gì?

**RAG = Retrieval-Augmented Generation**

- **Retrieval**: Tìm kiếm tài liệu liên quan
- **Augmented**: Thêm context vào câu hỏi  
- **Generation**: LLM tạo câu trả lời dựa trên context

## Tại sao cần RAG?

**LLM thuần** (không có RAG):
- Câu hỏi: "P/E ratio của VNM là bao nhiêu?"
- LLM: "Tôi không biết giá hiện tại của VNM" ❌

**LLM với RAG**:
1. Tìm kiếm: Tìm tài liệu về VNM
2. Thêm vào prompt: "Context: VNM có P/E = 17.9x. Question: P/E của VNM?"
3. LLM: "P/E của VNM là 17.9x" ✅

## 5 Bước RAG

### Bước 1: LOAD (Đọc tài liệu)

```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader

loader = DirectoryLoader(
    path="docs/",           # Thư mục chứa tài liệu
    glob="**/*.md",         # Chỉ load file .md
    loader_cls=TextLoader,  # Dùng TextLoader cho text files
)
documents = loader.load()
```

**Kết quả**: List các Document objects, mỗi cái có:
- `page_content`: Nội dung
- `metadata`: Thông tin thêm (source, etc.)

### Bước 2: SPLIT (Chia nhỏ)

**Tại sao cần split?**
- Documents dài → khó tìm kiếm chính xác
- Embedding model có giới hạn input
- Chunks nhỏ = context chính xác hơn

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,      # Mỗi chunk tối đa 200 ký tự
    chunk_overlap=20,    # Overlap giữa các chunks
)
chunks = text_splitter.split_documents(documents)
```

### Bước 3: EMBED + STORE

**Embedding là gì?**
- Chuyển text thành vector số
- "What is P/E?" → [0.1, 0.5, -0.3, ...]
- Texts giống nhau → vectors giống nhau

```python
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS

embeddings = AzureOpenAIEmbeddings(azure_deployment="text-embedding-3-large")
vectorstore = FAISS.from_documents(chunks, embeddings)
```

**FAISS** = Facebook AI Similarity Search
- Lưu vectors
- Tìm kiếm nhanh theo similarity

### Bước 4: SEARCH (Tìm kiếm)

```python
results = vectorstore.similarity_search(query, k=2)
```

- `k=2` = trả về 2 chunks liên quan nhất
- Dùng **cosine similarity** để so sánh vectors

### Bước 5: GENERATE (RAG hoàn chỉnh)

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Tạo retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# Template
template = """Answer based on context:
{context}

Question: {question}"""

prompt = ChatPromptTemplate.from_template(template)

# RAG chain (LCEL syntax)
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("What is P/E?")
```

## LCEL Syntax (LangChain Expression Language)

```python
chain = component1 | component2 | component3
```

Tương đương với:
```python
result = component3(component2(component1(input)))
```

**Ví dụ**:
```python
chain = prompt | llm | parser
# Tương đương
result = parser(llm(prompt(input)))
```

## Tóm tắt Pipeline

```
Documents (.md files)
    ↓ LOAD
Document objects
    ↓ SPLIT  
Chunks (200 chars each)
    ↓ EMBED
Vectors (3072 dims)
    ↓ STORE
FAISS Vector Store
    ↓ SEARCH (khi có query)
Top K relevant chunks
    ↓ AUGMENT
Context + Question
    ↓ GENERATE
LLM tạo câu trả lời
```

## Chạy

```bash
cd D:\2026\AI_Agent\ai_stock_analyst\rag_basic
python basic_rag.py
```

## Kết quả

```
Q: "When is RSI considered overbought?"
A: "RSI is considered overbought when it is above 70."

Q: "Explain P/E ratio with example"
A: "P/E = Stock Price / EPS. Example: 75,000 / 4,200 = 17.9x"
```
