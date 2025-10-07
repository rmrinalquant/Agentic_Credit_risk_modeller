# ingest_sklearn.py
import os
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import SKLearnVectorStore  # returns dicts with keys: id, text, metadata :contentReference[oaicite:0]{index=0}
from src.test_parser import parse_tool_file
import uuid

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
path = os.path.join(base_path,"data", "Tool_knowledge_base.txt")
persist_dir = os.path.join(base_path,"data", "chroma_db")

#persist_dir.mkdir(parents=True, exist_ok=True)

print(path)

# 1) chunk/parse your TXT
tools = parse_tool_file(path)  # -> [{'id', 'text', 'metadata'}, ...] :contentReference[oaicite:1]{index=1}

ids = [str(uuid.uuid4()) for _ in tools]
meta_data = [t["metadata"] for t in tools]
texts = [t["text"] for t in tools]
print(texts[5])
# 2) make LangChain Documents
#docs = [
#    Document(page_content=t["text"], metadata={**t["metadata"], "id": t["id"]})
#    for t in tools
#]

# 3) embed + build store (cosine) and persist to disk
emb = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    encode_kwargs={"normalize_embeddings": True},  # good with cosine
)
vs = SKLearnVectorStore.from_texts(
    texts=texts,
    embedding=emb,
    metadatas=meta_data,
    ids=ids,
    metric="cosine",
    persist_path=str(persist_dir),
    serializer="json",
)
vs.persist()
#vs.persist()

print(f"✅ Indexed {len(texts)} chunks at {persist_dir}")
