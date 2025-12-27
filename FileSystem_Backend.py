from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FilesystemBackend
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
import os

#Initializations----------------------------------------------------

model = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key = "")

system_prompt = '''you are expert at managing file systems '''

Composite_backend = lambda rt: CompositeBackend(
    default = StateBackend(rt),
    routes = {
        "/memory/": StoreBackend(rt),
        }
)

config = {'configurable':{'thread_id':'1'}}

#model---------------------------------------------------------------

agent = create_deep_agent(
    model=model,
    system_prompt=system_prompt,
    # backend=Composite_backend,
    backend = FilesystemBackend(root_dir='./agent_data/', virtual_mode=True),
    store=InMemoryStore(),
    checkpointer=InMemorySaver(),
    # middleware=[
    #     FilesystemMiddleware(
    #         backend=None,  # Optional: custom backend (defaults to StateBackend)
    #         system_prompt="Write to the filesystem when...",  # Optional custom addition to the system prompt
    #         custom_tool_descriptions={
    #             "ls": "Use the ls tool when...",
    #             "read_file": "Use the read_file tool to..."
    #         }  # Optional: Custom descriptions for filesystem tools
    #     ),
    # ],
)

#Run agent----------------------------------------------------------

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
