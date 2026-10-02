"""Page: 3D Digital Twin (Three.js embedded)"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import streamlit.components.v1 as components
import json

from services.api_client import get_equipment_list
from components.ui_helpers import demo_warning

st.set_page_config(page_title="3D Digital Twin", page_icon="🌐", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html,[class*=css]{font-family:'Inter',sans-serif;}
</style>
""", unsafe_allow_html=True)

st.title("🌐 3D Digital Twin Visualization")
demo_warning()
st.caption(
    "Three.js plant scene — equipment colors reflect backend simulation status. "
    "Drag to rotate · Scroll to zoom · Click equipment to inspect."
)

# Load equipment states from backend
eq_list = get_equipment_list()
eq_states_json = "{}"
if eq_list:
    eq_dict = {e["equipment_id"]: {"status": e["status"], "name": e["name"]} for e in eq_list}
    eq_states_json = json.dumps(eq_dict)

# Read the Three.js HTML
threejs_path = os.path.join(os.path.dirname(__file__), "..", "threejs", "twin3d.html")
with open(threejs_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Inject backend state into the Three.js HTML so it reflects real equipment status
inject_script = f"""
<script>
window.addEventListener('load', function() {{
  setTimeout(function() {{
    var states = {eq_states_json};
    window.dispatchEvent(new MessageEvent('message', {{data: {{type:'equipment_states', states: states}}}}));
  }}, 800);
}});
</script>
"""
html_content = html_content.replace("</body>", inject_script + "</body>")

components.html(html_content, height=620, scrolling=False)

# ─── Equipment status table below 3D view ─────────────────────────────────────
if eq_list:
    st.markdown("---")
    st.markdown("### ⚙️ Equipment Status Summary")
    status_colors = {
        "RUNNING":"🟢","IDLE":"⚪","WARNING":"🟡","FAULT":"🔴","SIMULATION":"🔵"
    }
    rows = []
    for e in eq_list:
        rows.append({
            "ID": e["equipment_id"],
            "Name": e["name"],
            "Type": e["equipment_type"],
            "Status": status_colors.get(e["status"],"❔") + " " + e["status"],
        })
    import pandas as pd
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
