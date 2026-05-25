import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from components.FileReader import (
    get_sample_files,
    ingest_uploaded_files,
    ingest_sample_files,
    get_usb_files,
    detectMounts,
    load_tracking_index,
    EmptyUploads,
)
from components.Search import run_search
from components.reporter import generate_txt_report, generate_csv_report, report_filename

st.set_page_config(
    page_title="ForensicAI",
    page_icon="⬛",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

:root { color-scheme: light only !important; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
.stApp, .main, .block-container {
    background-color: #ffffff !important;
    color:            #000000 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

#MainMenu, footer, header        { visibility: hidden; }
section[data-testid="stSidebar"] { display: none !important; }

.block-container {
    max-width: 720px !important;
    padding: 60px 32px 80px 32px !important;
}

/* title */
.page-title {
    font-family: 'IBM Plex Mono', monospace;
    border-top: 3px solid #000;
    border-bottom: 3px solid #000;
    padding: 26px 0 22px 0;
    margin-bottom: 44px;
}
.page-title .eyebrow {
    font-size: .61rem; font-weight: 600;
    letter-spacing: 4px; text-transform: uppercase;
    color: #888; margin-bottom: 10px;
}
.page-title h1 {
    font-size: 2rem; font-weight: 700;
    line-height: 1.15; letter-spacing: -.5px; color: #000;
}

/* search input */
.stTextInput > label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: .58rem !important; font-weight: 700 !important;
    letter-spacing: 4px !important; text-transform: uppercase !important;
    color: #000 !important;
}
.stTextInput > div > div > input {
    border-radius: 0 !important;
    border: 1.5px solid #000 !important;
    border-top: 3px solid #000 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1rem !important;
    color: #000 !important;
    background: #fff !important;
    padding: 14px 16px !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input:focus {
    box-shadow: 4px 4px 0 #000 !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder {
    color: #bbb !important; font-size: .88rem !important;
}

/* divider */
.rule { border: none; border-top: 1px solid #000; margin: 34px 0; }

/* section label */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .58rem; font-weight: 700;
    letter-spacing: 4px; text-transform: uppercase;
    color: #000; margin-bottom: 14px; display: block;
}

/* card buttons */
.stButton > button {
    background:    #ffffff !important;
    color:         #000000 !important;
    border:        none !important;
    border-radius: 0 !important;
    padding:       0 !important;
    width:         100% !important;
    text-align:    left !important;
    font-family:   inherit !important;
    cursor:        pointer !important;
    box-shadow:    none !important;
    min-height:    110px !important;
}
.stButton > button:hover,
.stButton > button:focus {
    background: #000000 !important;
    color:      #ffffff !important;
    border:     none !important;
    box-shadow: none !important;
}
.stButton > button:hover p,
.stButton > button:focus p { color: #ffffff !important; }

.s

/* grid 
# .grid-wrap { border: 1.5px solid #000; margin-bottom: 16px; }
# .cell-tl   { border-right: 1px solid #000; border-bottom: 1px solid #000; }
# .cell-tr   { border-bottom: 1px solid #000; }
# .cell-bl   { border-right: 1px solid #000; }
# .cell-br   { }*/
            
.grid-wrap.tight-grid { 
    border: 1.5px solid #000; 
    margin-bottom: 16px; 
    padding: 6px 6px 12px 6px;  
}

.cell-tl, .cell-tr {
    border-right: 1px solid #000; 
    border-bottom: 1px solid #000;
}

.cell-tr {
    border-right: none !important;
}

[data-testid="stHorizontalBlock"] {
    gap: 6px !important;     
}

[data-testid="stHorizontalBlock"]       { gap: 0 !important; }
[data-testid="stHorizontalBlock"] > div { padding: 0 !important; min-width: 0 !important; }

/* source indicator */
.source-indicator {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .7rem; color: #555;
    border-left: 2px solid #000;
    padding-left: 10px; margin-top: 10px; line-height: 1.8;
}

/* file table */
.idx-table {
    width: 100%; border-collapse: collapse;
    font-family: 'IBM Plex Mono', monospace;
    font-size: .72rem; margin-top: 12px;
}
.idx-table th {
    text-align: left; padding: 7px 10px;
    border-bottom: 2px solid #000;
    font-size: .6rem; letter-spacing: 2px;
    text-transform: uppercase; color: #000;
    background: #fff;
}
.idx-table td {
    padding: 7px 10px;
    border-bottom: 1px solid #e0e0e0;
    color: #333; background: #fff;
}
.idx-table tr:last-child td { border-bottom: none; }
.type-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .58rem; font-weight: 700;
    border: 1px solid #000; padding: 1px 7px;
    text-transform: uppercase; letter-spacing: 1px;
}

/* dialog */
[data-testid="stDialog"] > div,
div[role="dialog"] {
    background:    #ffffff !important;
    color:         #000000 !important;
    border:        2px solid #000 !important;
    border-radius: 0 !important;
    box-shadow:    8px 8px 0 rgba(0,0,0,.15) !important;
}
[data-testid="stDialog"] button[aria-label="Close"] {
    color: #000 !important; background: transparent !important;
}
.dlg-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .58rem; font-weight: 700;
    letter-spacing: 4px; text-transform: uppercase;
    color: #888; margin-bottom: 6px;
}
.dlg-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.1rem; font-weight: 700; color: #000;
    padding-bottom: 16px; border-bottom: 1.5px solid #000; margin-bottom: 20px;
}
.dlg-note {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .65rem; color: #999;
    border-left: 2px solid #ccc;
    padding-left: 10px; margin-top: 14px; line-height: 1.7;
}

[data-testid="stDialog"] .stFileUploader label,
[data-testid="stDialog"] .stMultiSelect  label,
[data-testid="stDialog"] .stCheckbox     label,
[data-testid="stDialog"] .stSelectbox    label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: .6rem !important; font-weight: 700 !important;
    letter-spacing: 3px !important; text-transform: uppercase !important;
    color: #000 !important;
}
[data-testid="stDialog"] [data-testid="stFileUploadDropzone"] {
    border: 1.5px dashed #000 !important;
    border-radius: 0 !important;
    background: #fafafa !important;
    font-family: 'IBM Plex Mono', monospace !important;
    color: #555 !important;
}
[data-testid="stDialog"] [data-baseweb="select"] > div {
    border: 1.5px solid #000 !important;
    border-radius: 0 !important;
    background: #fff !important;
    font-family: 'IBM Plex Mono', monospace !important;
    box-shadow: none !important;
}
[data-testid="stDialog"] .stButton > button {
    background:    #000 !important;
    color:         #fff !important;
    border:        1.5px solid #000 !important;
    border-radius: 0 !important;
    font-family:   'IBM Plex Mono', monospace !important;
    font-size:     .62rem !important; font-weight: 700 !important;
    letter-spacing: 3px !important; text-transform: uppercase !important;
    width:  100% !important; padding: 12px !important;
    min-height: unset !important;
}
[data-testid="stDialog"] .stButton > button:hover {
    background: #fff !important; color: #000 !important;
}

/* primary button (purge only) — scoped red */
button[kind="primary"],
.stButton > button[kind="primary"] {
    background:    #ffffff !important;
    color:         #cc0000 !important;
    border:        1.5px solid #cc0000 !important;
    border-radius: 0 !important;
}
.stButton > button[kind="primary"]:hover {
    background: #cc0000 !important;
    color:      #ffffff !important;
}

/* coming soon */
.cs-icon { font-size:2.2rem; display:block; text-align:center; margin-bottom:14px; }
.cs-body { font-family:'IBM Plex Mono',monospace; font-size:.78rem; color:#555; text-align:center; line-height:1.8; }
.fmt-row { display:flex; flex-wrap:wrap; justify-content:center; gap:8px; margin-top:16px; }
.fmt-tag { font-family:'IBM Plex Mono',monospace; font-size:.65rem; border:1px solid #ccc; color:#888; padding:3px 10px; }
.cs-soon { font-family:'IBM Plex Mono',monospace; font-size:.68rem; color:#bbb; text-align:center; margin-top:18px; }

/* status messages inside dialogs */
.dlg-status-ok  { font-family:'IBM Plex Mono',monospace; font-size:.75rem; color:#000;
                   border-left:3px solid #000; padding-left:10px; margin-top:14px; line-height:1.7; }
.dlg-status-err { font-family:'IBM Plex Mono',monospace; font-size:.75rem; color:#888;
                   border-left:3px solid #ccc; padding-left:10px; margin-top:14px; line-height:1.7; }
</style>
""", unsafe_allow_html=True)

_defaults = {
    "open_dialog":    None,
    "source_label":   None,
    "ingested_ids":   [],
    "ingest_results": [],
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def _render_ingest_table(entries: list[dict]) -> None:
    if not entries:
        return
    rows = "".join(
        f"<tr>"
        f"<td>{e['original_name']}</td>"
        f"<td><span class='type-badge'>{e['file_type']}</span></td>"
        f"<td>{e['size_kb']} KB</td>"
        f"<td>{e['id']}</td>"
        f"</tr>"
        for e in entries
    )
    st.markdown(
        f"<table class='idx-table'>"
        f"<thead><tr><th>File</th><th>Type</th><th>Size</th><th>ID</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>",
        unsafe_allow_html=True,
    )


@st.dialog("Upload Files", width="large")
def dialog_upload():
    st.markdown('<div class="dlg-eyebrow">Evidence Source</div>', unsafe_allow_html=True)
    st.markdown('<div class="dlg-title">Upload Files</div>', unsafe_allow_html=True)

    files = st.file_uploader(
        "Drop files here",
        accept_multiple_files=True,
        type=["txt", "md", "pdf", "docx", "doc"],
        label_visibility="collapsed",
    )
    st.markdown(
        '<div class="dlg-note">'
        'Accepted: .txt · .md · .pdf · .docx · .doc<br>'
        'Text is extracted and saved to evidence/uploads/ — never transmitted.'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button("Ingest Files →", key="confirm_upload"):
        if not files:
            st.warning("No files selected.")
        else:
            with st.spinner("Extracting text and saving to index..."):
                results = ingest_uploaded_files(files)
            if results:
                st.session_state["ingested_ids"]   += [r["id"] for r in results]
                st.session_state["ingest_results"]  = results
                st.session_state["source_label"]    = (
                    f"✓  {len(results)} file(s) ingested via upload"
                )
                st.rerun()
            else:
                st.markdown(
                    '<div class="dlg-status-err">All files already in index — nothing new ingested.</div>',
                    unsafe_allow_html=True,
                )


@st.dialog("Select Sample Files", width="large")
def dialog_sample():
    st.markdown('<div class="dlg-eyebrow">Evidence Source</div>', unsafe_allow_html=True)
    st.markdown('<div class="dlg-title">Select Sample Files</div>', unsafe_allow_html=True)

    sample_files = get_sample_files()

    if not sample_files:
        st.warning("No files found in evidence/samples/")
        return

    chosen = []
    for f in sample_files:
        col_chk, col_type, col_size = st.columns([6, 2, 2])
        with col_chk:
            if st.checkbox(f["name"], value=True, key=f"chk_{f['name']}"):
                chosen.append(f)
        with col_type:
            st.markdown(
                f'<div style="padding-top:6px;font-family:monospace;font-size:.65rem">'
                f'{f["file_type"].upper()}</div>',
                unsafe_allow_html=True,
            )
        with col_size:
            st.markdown(
                f'<div style="padding-top:6px;font-family:monospace;font-size:.65rem;color:#aaa">'
                f'{f["size_kb"]} KB</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="dlg-note">'
        'Files are read from evidence/samples/ on disk.<br>'
        'Add any .txt .md .pdf .docx file there and it appears here automatically.'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button("Ingest Selected →", key="confirm_sample"):
        if not chosen:
            st.warning("No files selected.")
        else:
            with st.spinner("Extracting text and saving to index..."):
                results = ingest_sample_files(chosen)
            if results:
                st.session_state["ingested_ids"]  += [r["id"] for r in results]
                st.session_state["ingest_results"] = results
                st.session_state["source_label"]   = (
                    f"✓  {len(results)} sample file(s) ingested"
                )
                st.rerun()
            else:
                st.markdown(
                    '<div class="dlg-status-err">All selected files already in index.</div>',
                    unsafe_allow_html=True,
                )


@st.dialog("Connected Device", width="large")
def dialog_device():
    st.markdown('<div class="dlg-eyebrow">Evidence Source</div>', unsafe_allow_html=True)
    st.markdown('<div class="dlg-title">Connected Device</div>', unsafe_allow_html=True)

    mounts = detectMounts()

    if not mounts:
        st.markdown("""
            <span class="cs-icon">💾</span>
            <div class="cs-body">No removable drives detected.<br>
            Connect a USB drive or SD card and reopen this dialog.</div>
            <div class="fmt-row">
                <span class="fmt-tag">USB Drive</span>
                <span class="fmt-tag">SD Card</span>
                <span class="fmt-tag">External HDD</span>
                <span class="fmt-tag">Flash Drive</span>
            </div>
        """, unsafe_allow_html=True)
        return

    options = {m["label"]: m["path"] for m in mounts}
    chosen_label = st.selectbox("Select drive to scan", list(options.keys()))

    st.markdown(
        f'<div class="dlg-note">Will recursively scan <code>{options[chosen_label]}</code>'
        f' for .txt .md .pdf .docx .doc files.</div>',
        unsafe_allow_html=True,
    )

    if st.button("Scan & Ingest →", key="confirm_device"):
        with st.spinner(f"Scanning {chosen_label}..."):
            results = get_usb_files(options[chosen_label])
        if results:
            st.session_state["ingested_ids"]  += [r["id"] for r in results]
            st.session_state["ingest_results"] = results
            st.session_state["source_label"]   = (
                f"✓  {len(results)} file(s) ingested from {chosen_label}"
            )
            _render_ingest_table(results)
            st.rerun()
        else:
            st.markdown(
                '<div class="dlg-status-err">No new supported files found on device.</div>',
                unsafe_allow_html=True,
            )

#@st.dialog("Disk Image", width="large")
#def dialog_disk():
#    st.markdown('<div class="dlg-eyebrow">Evidence Source</div>', unsafe_allow_html=True)
#    st.markdown('<div class="dlg-title">Disk Image</div>', unsafe_allow_html=True)
#    st.markdown("""
#        <span class="cs-icon">🖴</span>
#        <div class="cs-body">Load and parse forensic disk images<br>for full file-system keyword analysis.</div>
#        <div class="fmt-row">
#           <span class="fmt-tag">.dd</span>
#           <span class="fmt-tag">.E01</span>
#           <span class="fmt-tag">.img</span>
#           <span class="fmt-tag">.raw</span>
#           <span class="fmt-tag">.iso</span>
#       </div>
#       <div class="cs-soon">— Available in the next release —</div>
#   """, unsafe_allow_html=True)




@st.dialog("Empty Uploads Directory", width="small")
def dialog_confirm_purge():
    st.markdown('<div class="dlg-eyebrow">Destructive Action</div>', unsafe_allow_html=True)
    st.markdown('<div class="dlg-title">Empty Uploads Directory</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="dlg-note" style="border-left-color:#000;color:#000;">'        'This will permanently delete all extracted .txt files and index.json'        ' from <code>evidence/uploads/</code>.<br><br>'        'Original source files (in evidence/samples/ or on your device) are NOT affected.'        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("Yes, delete all", key="purge_yes", use_container_width=True):
            count = EmptyUploads()
            st.session_state["ingested_ids"]   = []
            st.session_state["ingest_results"] = []
            st.session_state["source_label"]   = f"Uploads directory emptied — {count} file(s) removed"
            st.rerun()
    with col_no:
        if st.button("Cancel", key="purge_no", use_container_width=True):
            st.rerun()


st.markdown("""
<div class="page-title">
    <div class="eyebrow">Digital Forensics — AI Keyword Search</div>
    <h1>Semantic<br>Evidence Discovery.</h1>
</div>
""", unsafe_allow_html=True)

st.text_input(
    "Search Query",
    placeholder="e.g.  money laundering  /  destroy evidence  /  offshore account",
    key="search_query",
    on_change=lambda: st.session_state.update({"trigger_search": True}),
)

if st.session_state.get("trigger_search") and st.session_state.get("search_query", "").strip():
    st.session_state["trigger_search"] = False
    query = st.session_state["search_query"]

    with st.spinner("Preparing evidence and tokenizing..."):
        result = run_search(query)

    st.session_state["search_result"] = result

if st.session_state.get("search_result"):
    r     = st.session_state["search_result"]
    query = st.session_state.get("search_query", "")

    if r["error"]:
        st.markdown(
            f'<div class="dlg-status-err">⚠ {r["error"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        if r["match_count"] == 0:
            st.markdown(
                '<div class="dlg-status-err">No matches found for this query.</div>',
                unsafe_allow_html=True,
            )
        else:
            # ── Results table (unchanged from original) ───────────────────
            rows = "".join(
                f"<tr>"
                f"<td>{m['original_name']}</td>"
                f"<td><span class='type-badge'>{m['file_type']}</span></td>"
                f"<td>{', '.join(m['matched_tokens'].keys())}</td>"
                f"<td>{m['match_count']}</td>"
                f"<td>{m['score']:.4f}</td>"
                f"</tr>"
                for m in r["evidence"]
            )

            st.markdown(
                f"<table class='idx-table'>"
                f"<thead><tr>"
                f"<th>File</th>"
                f"<th>Type</th>"
                f"<th>Keywords Found</th>"
                f"<th>Hits</th>"
                f"<th>Score</th>"
                f"</tr></thead>"
                f"<tbody>{rows}</tbody></table>",
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<span class="section-label">Export Report</span>',
                unsafe_allow_html=True,
            )

            txt_data = generate_txt_report(query, r)
            csv_data = generate_csv_report(query, r)

            dl_col1, dl_col2 = st.columns(2)

            with dl_col1:
                st.download_button(
                    label="⬇  Download .txt Report",
                    data=txt_data,
                    file_name=report_filename(query, "txt"),
                    mime="text/plain",
                    use_container_width=True,
                    key="dl_txt",
                    type="tertiary"
                )

            with dl_col2:
                st.download_button(
                    label="⬇  Download .csv Report",
                    data=csv_data,
                    file_name=report_filename(query, "csv"),
                    mime="text/csv",
                    use_container_width=True,
                    key="dl_csv",
                    type="tertiary"
                )


st.markdown('<hr class="rule">', unsafe_allow_html=True)
st.markdown('<span class="section-label">Evidence Source</span>', unsafe_allow_html=True)

st.markdown('<div class="grid-wrap tight-grid">', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="small")  

with col1:
    st.markdown('<div class="cell-tl">', unsafe_allow_html=True)
    if st.button(
        "📂  **Upload Files**\n\n.txt  ·  .md  ·  .pdf  ·  .doc",
        key="btn_upload", use_container_width=True,
    ):
        st.session_state["open_dialog"] = "upload"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="cell-tr">', unsafe_allow_html=True)
    if st.button(
        "🗂  **Select Sample**\n\nFrom evidence/samples/ on disk.",
        key="btn_sample", use_container_width=True,
    ):
        st.session_state["open_dialog"] = "sample"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    '<div style="display: flex; justify-content: center; margin-top: 8px;">', 
    unsafe_allow_html=True
)

st.markdown('<div style="width: 48%;">', unsafe_allow_html=True)   
if st.button(
    "💾  **Connected Device**\n\nScan a USB drive or external storage.",
    key="btn_device", use_container_width=True,
):
    st.session_state["open_dialog"] = "device"
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)   

st.markdown('</div>', unsafe_allow_html=True)  

# st.markdown('<hr class="rule">', unsafe_allow_html=True)
# st.markdown('<span class="section-label">Evidence Source</span>', unsafe_allow_html=True)

# st.markdown('<div class="grid-wrap">', unsafe_allow_html=True)
# col_l, col_r = st.columns(2)

# with col_l:
#     st.markdown('<div class="cell-tl">', unsafe_allow_html=True)
#     if st.button(
#         "📂  **Upload Files**\n\n.txt  ·  .md  ·  .pdf  ·  .doc",
#         key="btn_upload", use_container_width=True,
#     ):
#         st.session_state["open_dialog"] = "upload"
#         st.rerun()
#     st.markdown('</div>', unsafe_allow_html=True)

#     st.markdown('<div class="cell-bl">', unsafe_allow_html=True)
#     if st.button(
#         "💾  **Connected Device**\n\nScan a USB drive or external storage.",
#         key="btn_device", use_container_width=True,
#     ):
#         st.session_state["open_dialog"] = "device"
#         st.rerun()
#     st.markdown('</div>', unsafe_allow_html=True)

# with col_r:
#     st.markdown('<div class="cell-tr">', unsafe_allow_html=True)
#     if st.button(
#         "🗂  **Select Sample**\n\nFrom evidence/samples/ on disk.",
#         key="btn_sample", use_container_width=True,
#     ):
#         st.session_state["open_dialog"] = "sample"
#         st.rerun()
#     st.markdown('</div>', unsafe_allow_html=True)
# # '''
# #     st.markdown('<div class="cell-br">', unsafe_allow_html=True)
# #     if st.button(
# #         "🖴  **Disk Image**\n\n.dd  ·  .E01  ·  .img  ·  .raw",
# #         key="btn_disk", use_container_width=True,
# #     ):
# #         st.session_state["open_dialog"] = "disk"
# #         st.rerun()
# #     st.markdown('</div>', unsafe_allow_html=True)
# # '''

# st.markdown('</div>', unsafe_allow_html=True)  # close grid-wrap

if st.session_state["source_label"]:
    st.markdown(
        f'<div class="source-indicator">{st.session_state["source_label"]}</div>',
        unsafe_allow_html=True,
    )

if st.session_state["ingest_results"]:
    _render_ingest_table(st.session_state["ingest_results"])

full_index = load_tracking_index()
if full_index:
    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    st.markdown('<span class="section-label">Ingested Evidence Index</span>', unsafe_allow_html=True)

    total    = len(full_index)
    sources  = {}
    for e in full_index:
        sources[e["source"]] = sources.get(e["source"], 0) + 1

    summary = "  ·  ".join(f"{v} via {k}" for k, v in sources.items())
    st.markdown(
        f'<div class="source-indicator">{total} file(s) in index &nbsp;—&nbsp; {summary}</div>',
        unsafe_allow_html=True,
    )

    with st.expander("View full index"):
        _render_ingest_table(full_index)

    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        if st.button("Clear active selection", key="btn_clear", use_container_width=True):
            st.session_state["ingested_ids"]   = []
            st.session_state["ingest_results"] = []
            st.session_state["source_label"]   = None
            st.rerun()

    with btn_col2:
        if st.button("🗑  Empty uploads directory", key="btn_purge", use_container_width=True, type="primary"):
            st.session_state["open_dialog"] = "confirm_purge"
            st.rerun()

_d = st.session_state.get("open_dialog")
if _d:
    st.session_state["open_dialog"] = None
    if   _d == "upload":        dialog_upload()
    elif _d == "sample":        dialog_sample()
    elif _d == "device":        dialog_device()
    #elif _d == "disk":          dialog_disk()
    elif _d == "confirm_purge": dialog_confirm_purge()
