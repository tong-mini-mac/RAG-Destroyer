import streamlit as st
import os
import time
import pandas as pd
import json
from core.Refinery import DataRefinery
from core.Orchestrator import RAGOrchestrator
from core.Exporter import FileExporter
from core.Monitor import BackgroundMonitor
from core.VaultWarden import VaultWarden
from core.AuditJudge import AuditJudge
from core.Utils import CONFIG, get_org_config, save_audit_event, ROOT_PATH, LLMInterface
import threading

# Page Config
st.set_page_config(page_title="RAG-Destroyer Industrial", page_icon="🏛️", layout="wide")

# Persistent Session Defaults for Multi-LLM
if "selected_provider" not in st.session_state:
    st.session_state.selected_provider = "Google"
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = CONFIG.get("GEMINI_API_KEY", "")
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = CONFIG.get("OPENAI_API_KEY", "")
if "anthropic_api_key" not in st.session_state:
    st.session_state.anthropic_api_key = CONFIG.get("ANTHROPIC_API_KEY", "")

# Initialize Core Services
@st.cache_resource
def get_services():
    return {
        "orchestrator": RAGOrchestrator(),
        "refinery": DataRefinery(),
        "exporter": FileExporter(),
        "judge": AuditJudge(),
        "warden": VaultWarden()
    }

services = get_services()

if "monitor_running" not in st.session_state:
    monitor = BackgroundMonitor()
    threading.Thread(target=monitor.start, daemon=True).start()
    st.session_state.monitor_running = True

if "current_result" not in st.session_state:
    st.session_state.current_result = None

# Sidebar Navigation
st.sidebar.title("🎮 Command Center")
page = st.sidebar.radio("Navigate to:", ["🧠 GURU Assistant", "📊 Audit Dashboard", "📽️ Showcase Clips", "🛠️ System Config"])

# Load Org Data
org_config = get_org_config()
depts = [d["name"] for d in org_config.get("departments", [])]
roles = [r["role"] for r in org_config.get("roles", [] )]

# Helper for PnP Status Checklist
def get_pnp_status():
    status = []
    # API Check
    api_ready = False
    if st.session_state.selected_provider == "Google" and st.session_state.gemini_api_key: api_ready = True
    elif st.session_state.selected_provider == "OpenAI" and st.session_state.openai_api_key: api_ready = True
    elif st.session_state.selected_provider == "Anthropic" and st.session_state.anthropic_api_key: api_ready = True
    
    status.append(("✅ API Keys Linked" if api_ready else "❌ API Keys Missing", api_ready))
    
    # Storage Check
    raw_exists = os.path.exists(CONFIG["RAW_DATA_PATH"])
    status.append(("✅ Raw Storage Pipeline Active" if raw_exists else "⚠️ Raw Folder Missing", raw_exists))
    
    vault_exists = os.path.exists(CONFIG["CLEANED_DATA_PATH"])
    status.append(("✅ Knowledge Vault Active" if vault_exists else "❌ Vault Missing", vault_exists))
    
    return status

if page == "🧠 GURU Assistant":
    st.title("🏛️ RAG-Destroyer: Financial Org Simulation")
    
    # Setup Checklist (Quick PnP View)
    with st.expander("🛠️ System Health & PnP Status", expanded=False):
        status_items = get_pnp_status()
        for label, ready in status_items:
            st.write(label)
    
    st.info(f"""
    **🏢 Financial Organization Simulation (Digital Banking)**
    This system uses the **Zero-Vector-DB** architecture to manage knowledge across departmental silos.
    Knowledge is partitioned into {len(depts)} Primary Silos:
    👉 **{', '.join(depts)}**
    """)
    
    st.divider()

    # Dropdowns for Identity Simulation
    col_p, col_d = st.columns(2)
    with col_p:
        selected_role = st.selectbox("👤 Identity Simulation (Select Position):", roles)
    with col_d:
        selected_dept = st.selectbox("📁 Active Department (Search Scope):", depts)

    # Security Context Logic
    role_info = next((r for r in org_config.get("roles", []) if r["role"] == selected_role), {})
    role_access = role_info.get("access", "SUBSET")
    
    if role_access == "ALL":
        allowed_search_subsets = "ALL"
        st.success(f"👑 {selected_role}: Master GURU Access (Full Org Visibility)")
    elif isinstance(role_access, list):
        allowed_search_subsets = role_access
        st.warning(f"🛡️ {selected_role}: Multi-Silo Access ({', '.join(allowed_search_subsets)})")
    else:
        allowed_search_subsets = [selected_dept]
        st.info(f"📁 Role: {selected_role} | Silo: {selected_dept} (Restricted Access)")

    # Expert Query Interface
    st.divider()
    query = st.chat_input(f"Enter your query as {selected_role}...")
    
    if query:
        with st.status("🚀 GURU is scouting the authorized silos...", expanded=True) as status:
            st.write("🔍 Identifying Swarm Keywords...")
            time.sleep(1)
            st.write("🤖 Dispatches Parallel Bots...")
            # Result synthesis
            result = services["orchestrator"].handle_request(query, allowed_search_subsets)
            st.session_state.last_query = query
            
            st.write("⚖️ Running AI QC Audit (Dual 5+5 Scoring)...")
            qc_result = services["judge"].evaluate(query, result['sources'], result['answer'])
            result['qc'] = qc_result
            st.session_state.current_result = result
            status.update(label="✅ Synthesis Complete!", state="complete", expanded=False)

    # Display Result
    if st.session_state.current_result:
        res = st.session_state.current_result
        st.chat_message("user").write(st.session_state.get("last_query", "Previous Request"))
        with st.chat_message("assistant"):
            st.write(res['answer'])
            
            # QC Dual Badge
            qc = res.get('qc', {})
            total_score = qc.get('qc_score', 0)
            acc_score = qc.get('accuracy_score', 0)
            lang_score = qc.get('language_score', 0)
            
            color = "green" if total_score >= 8 else "orange" if total_score >= 4 else "red"
            st.markdown(f"### **QC Audit Status:** :{color}[Total Score {total_score}/10]")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Context Accuracy", f"{acc_score}/5")
            c2.metric("Language & Tone", f"{lang_score}/5")
            c3.metric("Tone Grade", qc.get('tone_grade', 'N/A'))
            
            if qc.get('critique'):
                st.caption(f"**AI Judge Critique:** {qc['critique']}")
            
            with st.expander("📚 View Authorized Sources"):
                for doc in res['sources']:
                    st.info(f"**{doc['title']}** (ID: {doc.get('doc_id')}) - Relevance: {doc['relevance']}")

            # Feedback Form
            st.divider()
            st.subheader("📝 Accuracy Feedback (Demo Improvement)")
            f_col1, f_col2 = st.columns([1, 2])
            with f_col1:
                rating = st.slider("Rate Accuracy", 1, 10, 10)
            with f_col2:
                comment = st.text_input("Comments for Code Improvement")
            
            if st.button("💾 Save to Audit Trail"):
                audit_data = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "role": selected_role,
                    "provider": st.session_state.selected_provider,
                    "query": st.session_state.get("last_query", "N/A"),
                    "answer": res['answer'],
                    "user_rating": rating,
                    "user_comment": comment,
                    "qc_score": total_score,
                    "acc_score": acc_score,
                    "lang_score": lang_score
                }
                save_audit_event(audit_data)
                st.success("Audit data saved locally for demo analysis!")

elif page == "📊 Audit Dashboard":
    st.title("📊 Industrial Audit Dashboard")
    st.markdown("### Real-World Multi-Role Performance Audit")
    path = CONFIG["AUDIT_LOG_PATH"]
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        st.dataframe(df, width=None) # Corrected use_container_width to None
        
        st.divider()
        st.subheader("📈 Quality Analytics")
        if not df.empty:
            avg_qc = df["qc_score"].mean()
            st.progress(avg_qc/10, text=f"Average QC Score: {avg_qc:.2f}/10")
    else:
        st.warning("No audit logs found.")

elif page == "📽️ Showcase Clips":
    st.title("📽️ Technological Showcase")
    st.markdown("### Real-World Operations & Stress-Test Evidence")
    
    showcase_dir = os.path.join(ROOT_PATH, "assets", "showcase")
    
    if os.path.exists(showcase_dir):
        col1, col2 = st.columns(2)
        
        clips = sorted([f for f in os.listdir(showcase_dir) if f.endswith(".webp")])
        
        for i, clip in enumerate(clips):
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                title = clip.replace(".webp", "").replace("_", " ").split(" ", 1)[-1]
                st.subheader(f"Step {i+1}: {title}")
                st.image(os.path.join(showcase_dir, clip), use_column_width=True)
                st.caption(f"Captured during Industrial Stress Test - GURU in the box.")
    else:
        st.warning("Real showcase assets not found. Please run the Audit test first.")

elif page == "🛠️ System Config":
    st.title("🛠️ System Configuration")
    
    # 1. Multi-LLM Setup
    st.header("🔑 API Credentials (Plug & Play)")
    st.session_state.selected_provider = st.selectbox("Select Primary AI Provider", ["Google", "OpenAI", "Anthropic"], 
                                                        index=["Google", "OpenAI", "Anthropic"].index(st.session_state.selected_provider))
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.gemini_api_key = st.text_input("Gemini API Key", value=st.session_state.gemini_api_key, type="password")
        st.session_state.openai_api_key = st.text_input("OpenAI API Key", value=st.session_state.openai_api_key, type="password")
    with col2:
        st.session_state.anthropic_api_key = st.text_input("Anthropic API Key", value=st.session_state.anthropic_api_key, type="password")
        st.session_state.line_notify_token = st.text_input("LINE Notify Token", value=CONFIG.get("LINE_NOTIFY_TOKEN", ""), type="password")

    # 2. Knowledge Valve (Path Settings)
    st.divider()
    st.header("📁 Knowledge Valve (Storage Paths)")
    raw_path = st.text_input("Raw Data Ingestion Path", value=CONFIG["RAW_DATA_PATH"])
    vault_path = st.text_input("Cleaned Knowledge Vault Path", value=CONFIG["CLEANED_DATA_PATH"])
    
    if st.button("🔧 Apply Storage Config"):
        st.info("Storage configuration updated. Paths will be used for the current session.")

    # 3. Org Structure Data
    st.divider()
    st.header("🏢 Organization Structure Editor")
    config_tab1, config_tab2 = st.tabs(["📁 Departments", "👤 Roles"])
    with config_tab1:
        st.data_editor(pd.DataFrame(org_config['departments']), width=None)
    with config_tab2:
        st.data_editor(pd.DataFrame(org_config['roles']), width=None)

# Footer
st.sidebar.divider()
st.sidebar.caption(f"RAG-Destroyer Industrial | Build: {time.strftime('%Y%j')}")
st.sidebar.caption("Privacy: Local Vault & API Keys are NOT shared with GitHub.")

# Critical PnP Notification
if not st.session_state.gemini_api_key and st.session_state.selected_provider == "Google":
    st.sidebar.error("⚠️ Gemini API Key Missing. Setup required in Config.")
