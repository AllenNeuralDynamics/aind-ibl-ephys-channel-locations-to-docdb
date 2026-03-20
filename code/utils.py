import json

import models


def validate_locations(locations_input: str) -> dict[str, models.ChannelLocationCCF]:
    locations_dict = json.loads(locations_input)
    if not all(k.startswith("channel_") for k in locations_dict.keys()):
        raise ValueError("Invalid locations input: keys must start with 'channel_'")
    return {k: models.ChannelLocationCCF(**v) for k, v in locations_dict.items()}

def validate_sorted_asset_name(sorted_asset_name_input: str) -> str:
    # ecephys_816308_2025-08-20_15-24-06_sorted_2025-09-20_07-10-14
    if not sorted_asset_name_input.startswith("ecephys_"):
        raise ValueError("Invalid sorted asset name: must start with 'ecephys_'")
    if not "_sorted_" in sorted_asset_name_input:
        raise ValueError("Invalid sorted asset name: must contain '_sorted_'")
    return sorted_asset_name_input