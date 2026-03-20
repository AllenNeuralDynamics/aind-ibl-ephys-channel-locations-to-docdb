"""
- get existing json paths, or allow user to paste json
- display json in a json viewer
- allow user to select from available smartspim assets, then sorted data assets (with probe names
  and sorter version)
- display partial df
- button linked to writing assets and launching the pipeline
"""

import logging

import streamlit as st
import streamlit.logger
import utils

logging.basicConfig(level=logging.INFO)
logger = streamlit.logger.get_logger(__name__)

st.set_page_config(layout="wide")

logger.warning("DocDB is not hooked up yet! Running in dev mode, only applicable for Dynamic Routing!")


st.title("Enter required information")

locations_input = st.text_input(
    "Channel locations from IBL alignment capsule:",
    key="locations_input",
    placeholder="Paste contents of channel locations json (a dict of dicts) and hit Enter...",
)

locations = utils.validate_locations(locations_input)
st.write(f"Validated locations for {len(locations)} channels")

sorted_asset_name_input = st.text_input(
    'Sorted asset used for alignment (hint: check the manifest in the "ibl-converted" data asset):',
    key="sorted_asset_name_input",
    placeholder="e.g. ecephys_816308_2025-08-20_15-24-06_sorted_2025-09-20_07-10-14",
)
sorted_asset_name = utils.validate_sorted_asset_name(sorted_asset_name_input)
logger.info(f"Validated sorted asset name: {sorted_asset_name}")

#TODO need to submit which probe this is (get probe names from sorted asset or manifest?)
# TODO do we need the 'previous_alignments' which are in the capsule submission

st.write("Writing ")
