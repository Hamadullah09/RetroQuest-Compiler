import streamlit as st
import graphviz
import json
import io
import contextlib
from lexer import Lexer, LexerError
from parser import Parser, ParserError
from semantic_analyzer import SemanticAnalyzer, SemanticError
from ir_generator import IRGenerator
from optimizer import Optimizer
from interpreter import Interpreter
from main import build_pipeline
from pathlib import Path

# --- IDENTITY ---
TEAM_MEMBERS = [
    "Hamadullah Arain (23K-0723)",
    "Tashkeel Pasha (23K-2014)",
    "Yousaf Bhatti (23K-0809)"
]
COURSE = "FAST-NUCES, CS4031 Compiler Construction, Spring 2026"

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="RetroQuest Pythonic IDE",
    page_icon="🐍",
    layout="wide",
)

# --- STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0D1117; color: #C9D1D9; }
    h1, h2, h3, .stTabs [data-baseweb="tab"] p { color: #00F5FF !important; }
    [data-testid="stSidebar"] { background-color: #010409; border-right: 1px solid #30363D; }
    .menu-header { font-size: 1.1rem; font-weight: bold; color: #FFBF00; margin-top: 20px; margin-bottom: 10px; border-bottom: 1px solid #30363D; padding-bottom: 5px; }
    .stTextArea textarea { background-color: #161B22 !important; color: #00F5FF !important; font-family: 'Fira Code', 'Courier New', monospace !important; border: 1px solid #30363D !important; }
    .log-stream { background-color: #161B22; color: #8B949E; padding: 10px; border-radius: 5px; font-family: 'Courier New', monospace; font-size: 0.85rem; border-left: 3px solid #00F5FF; white-space: pre-wrap; }
</style>
""", unsafe_allow_html=True)

# --- UTILS ---
def get_ast_viz(node):
    dot = graphviz.Digraph()
    dot.attr(bgcolor='#0D1117', fontcolor='#00F5FF')
    dot.attr('node', color='#00F5FF', fontcolor='#00F5FF', shape='box', style='rounded', fontname='Helvetica')
    dot.attr('edge', color='#8B949E')
    def add_node(n, parent=None, edge_label=""):
        if n is None: return
        node_id = str(id(n))
        label = type(n).__name__
        if hasattr(n, 'name'): label += f"\\n({n.name})"
        if hasattr(n, 'title'): label += f"\\n'{n.title}'"
        if hasattr(n, 'operator') and n.operator: label += f"\\n[{n.operator}]"
        if label == "Literal": label = f"Literal: {n.value}"
        elif label == "VariableReference": label = f"Var: {n.name}"
        dot.node(node_id, label)
        if parent: dot.edge(parent, node_id, label=edge_label)
        if hasattr(n, 'variables'):
            for v in n.variables: add_node(v, node_id, "var")
        if hasattr(n, 'scenes'):
            for s in n.scenes: add_node(s, node_id, "scene")
        if hasattr(n, 'statements'):
            for i, stm in enumerate(n.statements): add_node(stm, node_id, f"[{i}]")
        if hasattr(n, 'left'): add_node(n.left, node_id, "L")
        if hasattr(n, 'right'): add_node(n.right, node_id, "R")
        if hasattr(n, 'condition'): add_node(n.condition, node_id, "if")
        if hasattr(n, 'value') and not isinstance(n.value, (str, int, bool, float)) and n.value is not None:
            add_node(n.value, node_id, "val")
        return node_id
    add_node(node)
    return dot

# --- SESSION STATE ---
if 'code_buffer' not in st.session_state:
    try: st.session_state.code_buffer = Path("examples/python_adventure.py").read_text()
    except: st.session_state.code_buffer = 'game "Python Quest"\ndef start():\n    print("Hello!")\n    return'
if 'compile_results' not in st.session_state: st.session_state.compile_results = None
if 'logs' not in st.session_state: st.session_state.logs = ""
if 'interpreter_state' not in st.session_state: st.session_state.interpreter_state = None

def run_compilation(code):
    log_capture = io.StringIO()
    try:
        with contextlib.redirect_stdout(log_capture):
            results = build_pipeline(code)
        st.session_state.compile_results = results
        st.session_state.logs = log_capture.getvalue()
        return True
    except Exception as e:
        st.session_state.compile_results = None
        # Capture full error including type
        err_msg = f"[{type(e).__name__}] {str(e)}"
        st.session_state.logs = log_capture.getvalue() + f"\n\n🚨 {err_msg}"
        st.session_state.last_error = err_msg
        return False

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: #00F5FF;'>🐍 RetroQuest</h2>", unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="menu-header">🛠️ EXAMPLES</div>', unsafe_allow_html=True)
    
    example_files = list(Path("examples").glob("*.*"))
    example_names = [f.name for f in example_files]
    
    # Callback to handle example change
    def on_example_change():
        if st.session_state.ex_selector != "Select...":
            new_code = (Path("examples") / st.session_state.ex_selector).read_text()
            st.session_state.code_buffer = new_code
            run_compilation(new_code) # Auto-analyze on load
            st.session_state.interpreter_state = None # Reset runtime

    st.selectbox("Load Example", ["Select..."] + example_names, key="ex_selector", on_change=on_example_change)

    st.divider()
    st.markdown("### Team")
    for m in TEAM_MEMBERS: st.write(f"👤 {m}")
    
    st.divider()
    if st.session_state.compile_results:
        ir_json = json.dumps(st.session_state.compile_results[4], indent=2)
        st.download_button("📥 Export IR", ir_json, file_name="deploy.json", use_container_width=True)

# --- MAIN UI ---
st.markdown("<h1>🕹️ Visual IDE <span style='color: #FFBF00;'>Pro</span></h1>", unsafe_allow_html=True)

col_editor, col_viz = st.columns([1.1, 0.9])

with col_editor:
    st.markdown("### 📝 Editor")
    # Use code_buffer directly in text_area
    code_input = st.text_area("editor", value=st.session_state.code_buffer, height=450, label_visibility="collapsed")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 ANALYZE CODE", use_container_width=True):
            st.session_state.last_error = None
            if run_compilation(code_input): 
                st.success("✅ Compilation Successful!")
            else: 
                st.error(f"❌ {st.session_state.last_error}")
            st.session_state.code_buffer = code_input
    with c2:
        if st.button("▶️ RUN STORY", use_container_width=True):
            if st.session_state.compile_results:
                _, _, _, _, opt_ir, _ = st.session_state.compile_results
                st.session_state.interpreter_state = {
                    'ir': opt_ir, 'current_scene': opt_ir.get('entry_scene', 'start'),
                    'variables': json.loads(json.dumps(opt_ir.get('variables', {}))),
                    'history': [], 'ended': False, 'waiting_for_choice': False, 'choices': []
                }
            else: st.warning("Analyze first!")

with col_viz:
    st.markdown("### 🎮 Live Session")
    if st.session_state.interpreter_state:
        state = st.session_state.interpreter_state
        with st.container(border=True):
            if not state['ended'] and not state['waiting_for_choice']:
                scenes = state['ir']['scenes']
                if state['current_scene'] not in scenes:
                    state['history'].append(f"Scene {state['current_scene']} missing!")
                    state['ended'] = True
                else:
                    stmts = scenes[state['current_scene']]
                    for i, s in enumerate(stmts):
                        if s['type'] == 'ShowStatement':
                            val = s['value']
                            if isinstance(val, dict) and 'var' in val: val = state['variables'].get(val['var'], '??')
                            state['history'].append(str(val))
                        elif s['type'] == 'SetStatement': state['variables'][s['name']] = s['value']
                        elif s['type'] == 'GotoStatement':
                            state['current_scene'] = s['target']
                            st.rerun()
                        elif s['type'] == 'ChoiceStatement':
                            state['waiting_for_choice'] = True
                            state['choices'] = [stm for stm in stmts[i:] if stm['type'] == 'ChoiceStatement']
                            break
                        elif s['type'] == 'EndStatement':
                            state['history'].append("🏁 FINISHED")
                            state['ended'] = True
                            break
            
            for line in state['history'][-10:]:
                st.markdown(f"<p style='color: #00F5FF; font-family: monospace; margin: 2px;'>{line}</p>", unsafe_allow_html=True)
            
            if state['waiting_for_choice']:
                for idx, c in enumerate(state['choices']):
                    if st.button(f"👉 {c['text']}", key=f"c_{idx}_{state['current_scene']}"):
                        state['current_scene'] = c['target']; state['waiting_for_choice'] = False
                        st.rerun()
            if state['ended']:
                if st.button("🔄 REPLAY"): st.session_state.interpreter_state = None; st.rerun()
    else: st.info("Compile & Run to play.")
    
    with st.expander("🔍 Watcher", expanded=False):
        if st.session_state.interpreter_state: st.json(st.session_state.interpreter_state['variables'])
        else: st.write("No active session.")

# --- TABS ---
st.divider()
tabs = st.tabs(["💎 Lexical", "🌴 Syntax", "🧠 Semantic", "📡 IR", "📜 Logs"])

if st.session_state.compile_results:
    tokens, program, symbols, ir, optimized_ir, stats = st.session_state.compile_results
    with tabs[0]: st.dataframe([{"Type": t.type.name, "Lexeme": t.value, "Line": t.line} for t in tokens], use_container_width=True)
    with tabs[1]: st.graphviz_chart(get_ast_viz(program))
    with tabs[2]:
        c1, c2 = st.columns(2)
        with c1: st.write("**Variables**"); st.json(symbols.to_dict()["variables"])
        with c2: st.write("**Scenes**"); st.write(symbols.to_dict()["scenes"])
    with tabs[3]: st.json(optimized_ir)
    with tabs[4]: st.markdown(f'<div class="log-stream">{st.session_state.logs}</div>', unsafe_allow_html=True)
else:
    for t in tabs:
        with t: st.info("Run analysis to see results.")

st.markdown("<div style='text-align: center; color: #30363D; padding: 20px;'>RetroQuest Pythonic IDE | FAST-NUCES 2026</div>", unsafe_allow_html=True)
