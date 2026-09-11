from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_groq import ChatGroq
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage

MODEL_NAME = "openai/gpt-oss-20b"

SYSTEM_PROMPT = (
    "You are Sentinel, a security-monitoring reasoning agent. You receive "
    "detection events from a computer vision pipeline. Always check history "
    "first, then decide using these rules, in order:\n"
    "1. If history shows 2+ past events of this type at this camera, ALL "
    "false alarms, with no unusual factor in the current event -> DO NOT "
    "escalate, log as likely false alarm. Be decisive, not cautious.\n"
    "2. If there is no matching history, OR history includes past CONFIRMED "
    "real incidents -> escalate to security.\n"
    "3. Only flag for human review if history is genuinely MIXED "
    "(some real, some false) or there is no tool data at all to go on.\n"
    "Explain your reasoning briefly."
)

def build_graph(tools):
    llm = ChatGroq(model=MODEL_NAME).bind_tools(tools)

    def call_model(state: MessagesState):
        messages = state["messages"]
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        response = llm.invoke(messages)
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    conn = sqlite3.connect("sentinel_checkpoints.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    checkpointer.setup()
    return graph.compile(checkpointer=checkpointer)