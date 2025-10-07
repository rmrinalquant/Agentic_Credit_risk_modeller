import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import SKLearnVectorStore
import re

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
path = os.path.join(base_path,"data", "Tool_knowledge_base.txt")
persist_dir = os.path.join(base_path,"data", "chroma_db")

emb = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", encode_kwargs={"normalize_embeddings": True})

vs = SKLearnVectorStore(
    embedding=emb,
    persist_path=str(persist_dir),
    serializer="json",
    metric="cosine",
)
retriever = vs.as_retriever(search_kwargs={"k": 4})


if __name__ == "__main__":
    pass
    #for d in retriever.invoke("for a pd model run a data quality check on the dataset."):
    #print(d.metadata.get("name"), d.metadata.get("tags"), "|", d.page_content, "…")

        #mdesc = re.search(r"Description:\s*(.+?)(?:\n[A-Z][A-Za-z _]+:|\Z)", d.page_content, flags=re.S)
        #desc = mdesc.group(1).strip() if mdesc else "No value"  
        #print("desc:", desc)
        #print(d.metadata)