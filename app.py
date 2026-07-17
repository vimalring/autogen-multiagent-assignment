import streamlit as st
import asyncio
import time
import datetime
import traceback
from agents_config import get_agents, ai_triage_router
from autogen_agentchat.messages import TextMessage, UserMessage

st.set_page_config(page_title="Enterprise Support Portal", page_icon="🏢", layout="wide")

# Polished custom styles
st.markdown("""
<style>
    .agent-header { font-size: 1.05rem; font-weight: 700; color: #1E3A8A; margin-bottom: 2px; }
    .user-header { font-size: 1.05rem; font-weight: 700; color: #065F46; margin-bottom: 2px; }
    .sidebar-title { font-size: 1.25rem; font-weight: 800; color: #0F172A; }
    .log-timestamp { font-family: monospace; font-size: 0.78rem; color: #64748B; }
</style>
""", unsafe_allow_html=True)

# State Management
if "messages" not in st.session_state:
    st.session_state.messages = []  
if "historical_routing" not in st.session_state:
    st.session_state.historical_routing = []  
if "current_agent" not in st.session_state:
    st.session_state.current_agent = "Unassigned"

# --- SIDEBAR PRESENTATION VIEWPORTS ---
with st.sidebar:
    st.markdown('<p class="sidebar-title">🧠 Orchestration Telemetry</p>', unsafe_allow_html=True)
    st.divider()
    
    st.subheader("Current Focus")
    status_placeholder = st.empty()
    if st.session_state.current_agent == "Unassigned":
        status_placeholder.info("Status: 💤 Standing By\n\nSystem engine idle.")
    else:
        status_placeholder.success(f"Status: 🟢 Active Context\n\nAssigned: **{st.session_state.current_agent}**")
        
    st.divider()
    
    st.subheader("Persistent Routing History")
    history_container = st.container()
    with history_container:
        if not st.session_state.historical_routing:
            st.caption("No diagnostic paths traced yet.")
        else:
            for item in reversed(st.session_state.historical_routing):
                st.markdown(f"<span class='log-timestamp'>[{item['time']}]</span><br>🗣️ **Query:** *{item['query']}*<br>➡️ **Target:** {item['agent']}<br>---", unsafe_allow_html=True)

    st.divider()
    st.subheader("Active Pipeline Progress")
    live_pipeline_container = st.container()

# --- MAIN CHAT LAYOUT ---
st.title("🏢 Enterprise Support Hub")
st.caption("Production Multi-Agent Contextual Ecosystem with Real-Time Tool Grounding")
st.divider()

chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            header_class = "user-header" if msg["role"] == "user" else "agent-header"
            st.markdown(f'<div class="{header_class}">{msg["agent"]}</div>', unsafe_allow_html=True)
            st.write(msg["content"])

def execute_coroutine(coro):
    """Safely runs async coroutines, dodging common Streamlit thread deadlocks."""
    try:
        loop = asyncio.get_running_loop()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

# Input Interaction Catch Block
if user_query := st.chat_input("How can I assist you today?"):
    
    # 1. Update UI with User Input
    st.session_state.messages.append({"role": "user", "agent": "Employee", "content": user_query})
    with chat_container:
        with st.chat_message("user"):
            st.markdown('<div class="user-header">Employee</div>', unsafe_allow_html=True)
            st.write(user_query)

    # Compile compressed text view of preceding history for Triage optimization
    history_summary = "\n".join([f"{m['agent']}: {m['content']}" for m in st.session_state.messages[-4:-1]])

    # 2. Open up the pipeline container to track steps live
    live_pipeline_container.empty()
    with live_pipeline_container:
        st.info("🔄 Triage Manager inspecting message thread...")
        
        # Determine agent assignment
        assigned_agent_name = execute_coroutine(ai_triage_router(user_query, history_summary))
        st.session_state.current_agent = assigned_agent_name
        
        status_placeholder.success(f"Status: 🟢 Active Context\n\nAssigned: **{assigned_agent_name}**")
        st.success(f"🎯 Router Match: Assigned to **{assigned_agent_name}**")

    # Save to history tracking data state
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.historical_routing.append({
        "time": timestamp,
        "query": user_query if len(user_query) < 25 else f"{user_query[:22]}...",
        "agent": assigned_agent_name
    })

    # 3. Dynamic Safe Agent Execution Framework
    async def get_agent_response(agent_name: str, query: str) -> str:
        agents = get_agents()
        target_agent = agents[agent_name]
        
        with live_pipeline_container:
            st.info(f"🚀 Initializing workspace runtime context for {agent_name}...")
        
        # Execute the full thread run safely without active stream slicing inside loop threads
        result = await target_agent.run(task=query)
        
        with live_pipeline_container:
            st.success("✅ Frame cycle processing complete.")
            
        if result.messages:
            # Return the last clean text content block
            return str(result.messages[-1].content)
        return "No response content generated by the agent."

    # 4. Final Output Pipeline Rendering with Thinking Animation & Stream Effect
    with chat_container:
        with st.chat_message("assistant"):
            st.markdown(f'<div class="agent-header">{assigned_agent_name}</div>', unsafe_allow_html=True)
            
            try:
                # 🧠 NEW: Dynamic Thinking Indicator Wrapper
                with st.spinner(f"🤔 {assigned_agent_name} is analyzing data and thinking..."):
                    # Fetch full answer safely from AutoGen run logic
                    raw_reply = execute_coroutine(get_agent_response(assigned_agent_name, user_query))
                
                # Yield words dynamically for typewriter streaming layout look
                def response_generator():
                    for word in raw_reply.split(" "):
                        yield word + " "
                        time.sleep(0.03)
                
                # Render writing stream layout cleanly
                final_compiled_reply = st.write_stream(response_generator())
                
            except Exception as e:
                error_trace = traceback.format_exc()
                with live_pipeline_container:
                    st.error(f"💥 Framework Run Execution Fault: {str(e)}")
                st.error("System encountered a generation fault while processing.")
                with st.expander("Telemetry Stack Trace"):
                    st.code(error_trace)
                final_compiled_reply = "Execution error halted."

    # Commit generated parameters into session histories
    st.session_state.messages.append({
        "role": "assistant",
        "agent": assigned_agent_name,
        "content": final_compiled_reply
    })
    st.rerun()