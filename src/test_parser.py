import re


def parse_tool_file(path):
    text = open(path).read()
    chunks = re.split(r"(?=Tool:\s*[A-Za-z_][A-Za-z0-9_]*)", text)
    tools = []
    for c in chunks:
        c = c.strip()
        if not c:
            continue
        name_match = re.search(r"Tool:\s*([A-Za-z_][A-Za-z0-9_]*)", c)
        name = name_match.group(1) if name_match else "unknown"
        #print("Tool Name",name)
        tags_match = re.search(r"Tags:\s*(.*)", c)
        #print("Full Tags Match",tags_match.group(1) if tags_match else "No match")

        tags = [t.strip() for t in tags_match.group(1).split(",")] if tags_match else ""
        #print("Tags:",tags)
    
        tools.append({
            "id": f"tool:{name}",
            "text": c,
            "metadata": {"name": name, "tags": ",".join(tags)}
        })
        
    return tools