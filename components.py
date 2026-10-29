import html

import streamlit as st

_ICONS = {
    "revenue": '<polyline points="3 17 9 11 13 15 21 7"/><polyline points="15 7 21 7 21 13"/>',
    "units": '<path d="M21 8l-9-5-9 5v8l9 5 9-5z"/><path d="M3 8l9 5 9-5"/><path d="M12 13v8"/>',
    "bag": '<path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18"/>'
           '<path d="M16 10a4 4 0 0 1-8 0"/>',
    "activity": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "store": '<path d="M3 9l1.5-5h15L21 9"/><path d="M4 9v11h16V9"/><path d="M9 20v-6h6v6"/>'
             '<path d="M3 9h18"/>',
    "gem": '<path d="M6 3h12l4 6-10 12L2 9z"/><path d="M2 9h20"/><path d="M8 9l4 12 4-12-4-6z"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>'
             '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
}


def _icon(name):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{_ICONS[name]}</svg>'


def _render(markup):
    st.markdown(markup, unsafe_allow_html=True)


def sidebar_brand():
    _render(
        f'<div class="brand"><div class="brand-logo">{_icon("gem")}</div><div>'
        '<div class="brand-name">Jewellery Analytics</div>'
        '<div class="brand-tag">Sales Intelligence</div></div></div>'
    )


def page_header(title, subtitle, meta=""):
    _render(
        f'<div class="topbar"><div><div class="topbar-title">{html.escape(title)}</div>'
        f'<div class="topbar-sub">{html.escape(subtitle)}</div></div>'
        f'<div class="topbar-meta">{html.escape(meta)}</div></div>'
    )


def section_title(text, caption=""):
    markup = f'<div class="section-title">{html.escape(text)}</div>'
    if caption:
        markup += f'<div class="section-caption">{html.escape(caption)}</div>'
    _render(markup)


def filter_chips(items):
    chips = "".join(f'<span class="chip{" on" if active else ""}">{html.escape(text)}</span>'
                    for text, active in items)
    _render(f'<div class="chips">{chips}</div>')


def sidebar_label(text):
    _render(f'<div class="side-label">{html.escape(text)}</div>')


def sidebar_footer(source, through):
    _render(f'<div class="side-foot">Source: {html.escape(source)}<br>'
            f'Data through {html.escape(through)}</div>')


def skeleton():
    _render('<div class="skeleton"></div>')


def empty_state(title, sub):
    _render(
        f'<div class="empty-state"><div class="empty-icon">{_icon("search")}</div>'
        f'<div class="empty-title">{html.escape(title)}</div>'
        f'<div class="empty-sub">{html.escape(sub)}</div></div>'
    )


def _delta_chip(delta):
    if delta is None:
        return ""
    kind, arrow = ("up", "▲") if delta >= 0 else ("down", "▼")
    return f'<span class="kpi-delta {kind}">{arrow} {abs(delta):.1f}% vs prev.</span>'


def kpi_card(icon, label, value, sub="", delta=None, delay=0.0):
    _render(
        f'<div class="kpi-card" style="animation-delay:{delay}s">'
        f'<div class="kpi-top"><div class="kpi-icon">{_icon(icon)}</div>{_delta_chip(delta)}</div>'
        f'<div class="kpi-label">{html.escape(label)}</div>'
        f'<div class="kpi-value">{html.escape(str(value))}</div>'
        f'<div class="kpi-sub">{html.escape(sub)}</div></div>'
    )


def highlight_card(icon, label, name, sub, share_pct, delay=0.0):
    width = max(0.0, min(float(share_pct), 100.0))
    _render(
        f'<div class="hl-card" style="animation-delay:{delay}s">'
        f'<div class="hl-head">{_icon(icon)}{html.escape(label)}</div>'
        f'<div class="hl-name">{html.escape(name)}</div>'
        f'<div class="hl-sub">{html.escape(sub)}</div>'
        f'<div class="hl-bar"><span style="width:{width:.1f}%"></span></div></div>'
    )


def insights_panel(items):
    rows = "".join(f'<div class="insight"><div>{html.escape(item)}</div></div>' for item in items)
    _render(f'<div class="panel"><div class="panel-title">Key insights</div>{rows}</div>')


def callout(title, body, kind="neu"):
    _render(
        f'<div class="callout {kind}"><div class="callout-title">{html.escape(title)}</div>'
        f'<div class="callout-body">{html.escape(body)}</div></div>'
    )


def record_count(shown, total):
    _render(f'<div class="record-count"><b>{shown:,}</b> of {total:,} records</div>')
