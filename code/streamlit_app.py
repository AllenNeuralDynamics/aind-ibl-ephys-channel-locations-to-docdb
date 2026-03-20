"""
- get computation ID
- check computation is accessible in codeocean API
 - if not: alert user to share capsule with ben
- get file tree for files in computation
- extract subject ID (top level folder name, 6-7digit number) and check s3 dir for existing data
 - if any found, display as read-only table
- display table with all files in file tree with toggles for each day/probe (default selected)
- for files selected, copy with original file tree structure to s3://aind-scratch-data/dynamic-routing/ibl-gui-output/
-
"""

import logging
import re

import aind_session
import pandas as pd
import streamlit as st
import streamlit.logger
import utils

logging.basicConfig(level=logging.INFO)
logger = streamlit.logger.get_logger(__name__)

st.set_page_config(layout="wide")

st.warning("DocDB is not hooked up yet! Running in S3 scratch data mode: only applicable for Dynamic Routing!")

# subject/session/probe/json_files
COMPUTATION_FILE_GLOB = "*/*/*/ccf_channel_locations.json"
S3_CACHE_FILE_GLOB = "{subject_id}/*/*/ccf_channel_locations.json"


@st.cache_data
def _cached_get_computation_subject_id(computation_id: str) -> str:
    return utils.get_computation_subject_id(computation_id)


@st.cache_data
def _cached_get_computation_file_paths(computation_id: str) -> list[str]:
    return utils.get_computation_file_paths(computation_id)


@st.cache_data
def _cached_get_existing_s3_files(subject_id: str) -> list[str]:
    return utils.get_existing_s3_files(subject_id)


st.title("IBL Ephys Channel Locations to DocDB")

computation_id = st.text_input(
    "Computation ID from IBL GUI capsule:",
    key="computation_id_input",
    placeholder="Computation ID from the IBL GUI capsule (36 characters, menu on right of 'Run 2342342')...",
)

if not computation_id:
    st.stop()

try:
    computation = aind_session.get_codeocean_model(computation_id, is_computation=True)
except Exception as exc:
    st.error(
        f"Failed to retrieve computation: {exc!r}\n\n"
        "Please ensure the IBL GUI capsule results are shared with the service account."
    )
    st.stop()

st.success(f"Validated computation: `{computation.id}`")

try:
    subject_id = _cached_get_computation_subject_id(computation.id)
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

st.write(f"Subject ID: **{subject_id}**")

existing_files = _cached_get_existing_s3_files(subject_id)
if existing_files:
    st.subheader("Existing data in S3")
    existing_rows = []
    for key in existing_files:
        parts = key.split("/")
        # key structure: {prefix}/{subject_id}/{session}/{probe}/ccf_channel_locations.json
        session = parts[-3] if len(parts) >= 4 else ""
        probe = parts[-2] if len(parts) >= 3 else ""
        date = m.group() if (m := re.search(r"\d{4}-\d{2}-\d{2}", session)) else ""
        existing_rows.append({"date": date, "probe": probe, "path": f"s3://{utils.S3_DEST_BUCKET}/{key}"})
    st.dataframe(
        pd.DataFrame(existing_rows),
        width="stretch",
        hide_index=True,
    )

st.subheader("Select files to copy")

with st.spinner("Fetching file list from computation..."):
    file_paths = _cached_get_computation_file_paths(computation.id)

if not file_paths:
    st.warning("No `ccf_channel_locations.json` files found in computation.")
    st.stop()

rows = []
for path in file_paths:
    parts = path.split("/")
    # path structure: {subject_id}/{session}/{probe}/ccf_channel_locations.json
    session = parts[1] if len(parts) > 1 else ""
    probe = parts[2] if len(parts) > 2 else ""
    date = m.group() if (m := re.search(r"\d{4}-\d{2}-\d{2}", session)) else ""
    rows.append({"selected": True, "date": date, "probe": probe, "session": session, "path": path})

edited_df = st.data_editor(
    pd.DataFrame(rows),
    column_config={
        "selected": st.column_config.CheckboxColumn("Copy?", default=True, width=50),
        "date": st.column_config.TextColumn("date", disabled=True, width="small"),
        "probe": st.column_config.TextColumn("probe", disabled=True, width="small"),
        "session": st.column_config.TextColumn("session", disabled=True, width="medium"),
        "path": st.column_config.TextColumn("path", disabled=True, width="large"),
    },
    width="stretch",
    hide_index=True,
)

selected_paths = edited_df[edited_df["selected"]]["path"].tolist()

if st.button(
    f"Copy {len(selected_paths)} file(s) to S3",
    type="primary",
    disabled=len(selected_paths) == 0,
):
    with st.spinner(f"Copying {len(selected_paths)} files to S3..."):
        try:
            uploaded = utils.copy_files_to_s3(computation.id, selected_paths)
            st.success(f"Successfully copied {len(uploaded)} file(s).")
            for key in uploaded:
                st.write(f"- `s3://{utils.S3_DEST_BUCKET}/{key}`")
            _cached_get_existing_s3_files.clear()
        except Exception as exc:
            st.error(f"Failed to copy files: {exc!r}")
