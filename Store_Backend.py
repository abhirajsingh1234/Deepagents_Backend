import os
from pathlib import Path
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FilesystemBackend
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key = "")

# 1. SETUP DIRECTORIES (ONE-TIME, auto-created by backend)
DATA_DIR = Path("C:/Users/Abhiraj/Desktop/file_search_bureau_analysis/data")
DATA_DIR.mkdir(exist_ok=True)  # Just ensure root exists

# 2. SHARED STORE (persists across threads)
store = InMemoryStore()
checkpointer = MemorySaver()

# 3. SYSTEM PROMPT WITH SEMANTIC RULES
system_prompt = """You are a bureau file analysis agent. Follow these **FILE STORAGE RULES** automatically:

## STORAGE HIERARCHY
**`/memories/`** - PERMANENT (cross-conversation): preferences, insights, summaries, important notes and all kinds of memories.
every time you learn a new preference or important insight about the user, save it  as a different text file.

## AUTOMATIC RULES
- "remember", "preference", "always" → /memories/

## BEFORE WRITING: Plan in /workspace/plan.txt then execute."""

# **`/bureau_data/`** - RAW DATA (disk): CSVs, PDFs, reports, exports  
# **`/workspace/`** - TEMPORARY (ephemeral): calculations, drafts
# - CSV, Excel, PDF, "data", "report" → /bureau_data/ 
# - calculations, drafts, temp → /workspace/



# 4. COMPOSITE BACKEND (auto-creates folders)
backend = lambda rt: CompositeBackend(
    default=StateBackend(rt),  # /tmp/, unprefixed → ephemeral
    routes={
        "/memories/": StoreBackend(rt),  # Cross-thread InMemoryStore
    #     "/bureau_data/": FilesystemBackend(  # Real disk (auto-creates subdirs)
    #         root_dir=str(DATA_DIR),
    #         virtual_mode=True
    #     ),
    #     "/workspace/": StateBackend(rt),  # Ephemeral workspace
    }
)

# 5. CREATE AGENT
model = model  # Your model
agent = create_deep_agent(
    model=model,
    system_prompt=system_prompt,
    store=store,
    # checkpointer=checkpointer,
    backend=backend
)

config = {'configurable':{'thread_id':'1'}}

while True:

    query = input('you : ')
    if query.lower() == 'exit':
        break
    
    result1 = agent.invoke({
        "messages": [{
            "role": "user",
            "content": query
        }]
    }, config)

    print('onboarder : ',result1['messages'][-1].content)
    print('='*50)

for res in result1['messages']:
    res.pretty_print()
