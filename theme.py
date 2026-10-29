import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

CURRENCY = "PKR"

SURFACE = "#111821"
BORDER = "#1E2937"
TEXT = "#E6E8EB"
MUTED = "#8B95A5"
ACCENT = "#C9A24B"
SLATE = "#3B4B63"
BLUE = "#6B93D6"
POS = "#3FB68B"
NEG = "#E5645A"
CATEGORICAL = [ACCENT, "#4F7CAC", "#3FA796", "#8E7CC3", "#D9776B", "#8B95A5"]

_GRID = "#18212C"

pio.templates["executive"] = go.layout.Template(
    layout=dict(
        font=dict(family="Inter, sans-serif", color="#C9CFD8", size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=CATEGORICAL,
        title=dict(font=dict(size=14, color=TEXT), x=0.01, xanchor="left"),
        margin=dict(l=14, r=24, t=52, b=14),
        xaxis=dict(gridcolor=_GRID, zeroline=False, linecolor=BORDER,
                   tickfont=dict(color=MUTED), automargin=True),
        yaxis=dict(gridcolor=_GRID, zeroline=False, linecolor=BORDER,
                   tickfont=dict(color=MUTED), automargin=True),
        hoverlabel=dict(bgcolor=SURFACE, bordercolor=BORDER, font=dict(color=TEXT)),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED)),
    )
)
pio.templates.default = "executive"


def fmt_compact(value):
    value = float(value)
    for limit, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(value) >= limit:
            return f"{value / limit:,.1f}{suffix}"
    return f"{value:,.0f}"


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, .stApp, p, h1, h2, h3, h4, label, button, input, textarea,
[data-testid="stMarkdownContainer"] { font-family: 'Inter', sans-serif; }

footer { visibility: hidden; }
.block-container { padding-top: 3.5rem; max-width: 1400px; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideIn { from { opacity: 0; transform: translateX(-16px); } to { opacity: 1; transform: translateX(0); } }
@keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }

[data-testid="stSidebar"] { border-right: 1px solid #1E2937; }
[data-testid="stSidebarContent"] { animation: slideIn 0.4s ease-out both; }
[data-testid="stSidebar"] [data-testid="stExpander"] {
  border: 1px solid #1E2937; border-radius: 10px; background: transparent;
  transition: border-color 0.2s ease;
}
[data-testid="stSidebar"] [data-testid="stExpander"]:hover { border-color: rgba(201,162,75,0.5); }
[data-testid="stSidebar"] .stButton button {
  border: 1px solid #2A3646; border-radius: 10px; transition: all 0.2s ease;
}
[data-testid="stSidebar"] .stButton button:hover { border-color: #C9A24B; color: #C9A24B; }

.brand { display: flex; align-items: center; gap: 12px; padding: 4px 0 14px 0; }
.brand-logo {
  width: 38px; height: 38px; border-radius: 10px; display: grid; place-items: center;
  background: rgba(201,162,75,0.14); border: 1px solid rgba(201,162,75,0.35); color: #C9A24B;
}
.brand-logo svg { width: 20px; height: 20px; }
.brand-name { font-weight: 650; font-size: 0.98rem; line-height: 1.2; }
.brand-tag { font-size: 0.7rem; color: #8B95A5; letter-spacing: 0.1em; text-transform: uppercase; }
.record-count { font-size: 0.78rem; color: #8B95A5; text-align: center; padding-top: 10px; }
.record-count b { color: #E6E8EB; }

[data-testid="stCaptionContainer"] { margin: 10px 0 4px 0; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 0 0 14px 0; }
.side-label { font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase; color: #8B95A5; margin: 4px 0 8px 2px; font-weight: 600; }
.side-foot { font-size: 0.7rem; color: #5F6B7C; text-align: center; line-height: 1.6; padding: 14px 0 4px 0; }
.chip.on { color: #E6D3A0; border-color: rgba(201,162,75,0.6); background: rgba(201,162,75,0.1); }
.chip {
  font-size: 0.7rem; padding: 3px 10px; border-radius: 999px; color: #AEB6C2;
  background: #111821; border: 1px solid #1E2937;
}

.brand-logo svg, .kpi-icon svg, .hl-head svg, .empty-icon svg {
  stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round;
}

.topbar {
  display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 8px;
  margin-bottom: 18px; padding-bottom: 14px; border-bottom: 1px solid #1E2937;
  animation: fadeUp 0.4s ease-out both;
}
.topbar-title { font-size: 1.6rem; font-weight: 650; letter-spacing: -0.02em; }
.topbar-sub { color: #8B95A5; font-size: 0.88rem; margin-top: 2px; }
.topbar-meta { color: #8B95A5; font-size: 0.8rem; text-align: right; }

.section-title { font-size: 1rem; font-weight: 600; margin: 28px 0 2px 0; letter-spacing: -0.01em; }
.section-caption { color: #8B95A5; font-size: 0.84rem; margin: 0 0 10px 0; }

.kpi-card {
  background: #111821; border: 1px solid #1E2937; border-radius: 12px; padding: 16px 18px;
  height: 150px; animation: fadeUp 0.4s ease-out both; transition: border-color 0.2s ease;
}
.kpi-card:hover { border-color: rgba(201,162,75,0.55); }
.kpi-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.kpi-icon {
  width: 32px; height: 32px; border-radius: 8px; display: grid; place-items: center;
  background: rgba(201,162,75,0.12); color: #C9A24B;
}
.kpi-icon svg { width: 17px; height: 17px; }
.kpi-label { font-size: 0.72rem; color: #8B95A5; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 500; }
.kpi-value { font-size: 1.7rem; font-weight: 650; letter-spacing: -0.02em; margin: 2px 0; color: #E6E8EB; }
.kpi-sub { font-size: 0.78rem; color: #8B95A5; }
.kpi-delta { font-size: 0.74rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; }
.kpi-delta.up { color: #3FB68B; background: rgba(63,182,139,0.12); }
.kpi-delta.down { color: #E5645A; background: rgba(229,100,90,0.12); }

.hl-card {
  background: #111821; border: 1px solid #1E2937; border-radius: 12px; padding: 14px 18px;
  animation: fadeUp 0.4s ease-out both; transition: border-color 0.2s ease;
}
.hl-card:hover { border-color: rgba(201,162,75,0.55); }
.hl-head { display: flex; align-items: center; gap: 8px; color: #8B95A5; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; }
.hl-head svg { width: 15px; height: 15px; color: #C9A24B; }
.hl-name { font-size: 1.05rem; font-weight: 600; margin: 8px 0 2px 0; overflow-wrap: anywhere; }
.hl-sub { font-size: 0.78rem; color: #8B95A5; }
.hl-bar { height: 4px; border-radius: 2px; background: #1B2430; margin-top: 10px; overflow: hidden; }
.hl-bar span { display: block; height: 100%; background: #C9A24B; border-radius: 2px; }

.panel {
  background: #111821; border: 1px solid #1E2937; border-radius: 12px; padding: 16px 22px;
  margin: 14px 0 4px 0; animation: fadeUp 0.4s ease-out both;
}
.panel-title { font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.08em; color: #8B95A5; font-weight: 600; margin-bottom: 6px; }
.insight { display: flex; gap: 12px; padding: 9px 0; border-top: 1px solid #1E2937; font-size: 0.9rem; line-height: 1.5; color: #C9CFD8; }
.insight::before { content: ""; flex: 0 0 6px; height: 6px; border-radius: 50%; background: #C9A24B; margin-top: 8px; }

.callout {
  background: #111821; border: 1px solid #1E2937; border-left: 3px solid var(--c);
  border-radius: 10px; padding: 14px 18px; margin: 14px 0; animation: fadeUp 0.4s ease-out both;
}
.callout.pos { --c: #3FB68B; }
.callout.neu { --c: #C9A24B; }
.callout-title { font-weight: 600; margin-bottom: 4px; }
.callout-body { color: #AEB6C2; font-size: 0.9rem; line-height: 1.5; }

div[data-testid="stPlotlyChart"] {
  background: #111821; border: 1px solid #1E2937; border-radius: 12px; padding: 6px;
  animation: fadeUp 0.45s ease-out both; transition: border-color 0.2s ease;
}
div[data-testid="stPlotlyChart"]:hover { border-color: #2A3646; }

div[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #1E2937; }
button[data-baseweb="tab"] { font-weight: 500; font-size: 0.9rem; padding: 8px 14px; transition: color 0.2s ease, background 0.2s ease; }
button[data-baseweb="tab"]:hover { background: rgba(255,255,255,0.03); }
button[data-baseweb="tab"][aria-selected="true"] { color: #C9A24B; }
div[data-testid="stTabs"] [role="tabpanel"] { animation: fadeUp 0.35s ease-out both; }

.skeleton {
  height: 340px; border-radius: 12px; border: 1px solid #1E2937;
  background: linear-gradient(90deg, #111821 25%, #1A2430 50%, #111821 75%);
  background-size: 200% 100%; animation: shimmer 1.4s linear infinite;
}
.empty-state {
  text-align: center; padding: 48px 24px; border-radius: 12px; margin: 12px 0;
  border: 1px dashed #2A3646; background: #111821; animation: fadeUp 0.4s ease-out both;
}
.empty-icon { color: #8B95A5; }
.empty-icon svg { width: 34px; height: 34px; }
.empty-title { font-weight: 600; font-size: 1.05rem; margin-top: 10px; }
.empty-sub { color: #8B95A5; font-size: 0.88rem; margin-top: 4px; }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; animation-delay: 0s !important; }
}
</style>
"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)
