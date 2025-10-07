from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from src.schemas import ActionPlan
from src.retriever import retriever
import re, json

# Use Groq/Cloudflare/OpenRouter/etc. by swapping base_url + model as needed
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",               # good + cheap for intent→JSON
    api_key = "AIzaSyBQRROj3zgkMRydfOYikBsazA7hXk3QPKE",
    temperature=0,
)

s_llm = llm.with_structured_output(ActionPlan)

# ---------- 3) Prompt ----------
PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a data-quality agent. Produce ONLY a JSON action plan conforming to the schema. "
     "Use the tools mentioned in context when relevant."),
    ("human",
     "USER QUERY:\n{query}\n\n"
     "TOOLS CONTEXT (top {k}):\n{context}\n\n"
     "Rules:\n- Return only JSON (no extra text)\n- Choose minimal steps\n- "
     "If unsure which id to use, pick the closest by name/tags")
])

def format_context(docs):
    lines = []
    for d in docs:
        tool_id =  d.metadata.get("name") or "unknown"
        tags = d.metadata.get("tags")
        # Extract description from text if available  
        mdesc = re.search(r"Description:\s*(.+?)(?:\n[A-Z][A-Za-z _]+:|\Z)", d.page_content, flags=re.S)
        desc = mdesc.group(1).strip() if mdesc else "No value"  
    
        lines.append(f"name: {tool_id}  \n  tags: {tags}\n  text: {desc}")

    return "\n".join(lines)

def plan_for(query: str) -> ActionPlan:
    docs = retriever.invoke(query)                          # retrieve
    ctx = format_context(docs)
    msg = PROMPT.format_messages(query=query, context=ctx, k=len(docs))
    return s_llm.invoke(msg)   


if __name__ == "__main__":
    pass
    # Example query
    #query = "for a pd model run a data quality check on the dataset."
    #plan = plan_for(query)

    #print("=== PLAN ===")
    #print(json.dumps(plan.model_dump(), indent=2))  # pretty-print JSON plan