from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END 
from langgraph.graph import  add_messages
from langgraph.prebuilt import ToolNode 
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from colorama import Fore 
from tool import stock_screener

from dotenv import load_dotenv, find_dotenv
import os 

# loading environment variables
if find_dotenv():
    load_dotenv(find_dotenv())
else:
    print("No .env file found")
    
API_KEY = os.getenv("GOOGLE_API_KEY")

# defining the llm 
# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", api_key = API_KEY, temperature=0.0)
llm = ChatOllama(model = "mistral:7b", temperature=0.0)

# llm with tools 
tools = [stock_screener] 
llm_with_tools = llm.bind_tools(tools)

#defining a tool node 
tool_node = ToolNode(tools)

# defining the agent state 
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    
# creating the simple chatbot 
def chatbot(state: AgentState) -> AgentState:
    # print(f"\nSTATE: {state['messages']}\n") , you can prin the state to see exactly how state changes look like
    
    return {"messages": [llm_with_tools.invoke(state['messages'])]}

# defining router for conditional edges 
def router(state: AgentState) -> str:
    last_message = state['messages'][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    else:
        return END

# initialising state graph 
graph = StateGraph(AgentState)

# adding nodes 
graph.add_node("chatbot", chatbot)
graph.add_node("tools", tool_node)
# defining edges 
graph.add_edge(START, "chatbot")
graph.add_edge("tools", "chatbot")
graph.add_conditional_edges("chatbot", router)

# compiling the graph with memory 
memory = InMemorySaver()
app = graph.compile(checkpointer=memory)

if __name__ == "__main__":
    while True:
        user_input = input(Fore.GREEN + "User: " + Fore.RESET)
        if user_input.strip().lower() in ['exit', 'quit']:
            break
        result = app.invoke({'messages': [{'role': 'user', 'content': user_input}]}, config={"configurable":{"thread_id":1234}})
        print(Fore.BLUE + "Agent: " + Fore.RESET + result['messages'][-1].content)