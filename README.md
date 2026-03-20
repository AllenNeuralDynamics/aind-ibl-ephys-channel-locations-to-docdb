# aind-ibl-ephys-channel-locations-to-docdb

## Requirements
- AIND power user assumable role, for writing to the AIND metadata DocDB
- the name of the sorted asset used for alignment OR the name of the "converted" data asset (e.g. `SmartSPIM_816308_2025-09-17_19-05-14_ibl-converted_2025-10-15_15-59-46`), which we can use to find the sorted data asset
- a dict matching the following format (which will be validated with Pydantic):
    ```json
    {
        "channel_0": {
            "x": -0.002517582795765973,
            "y": -0.0031254016699778088,
            "z": -0.002868241522548693,
            "axial": 0.0,
            "lateral": 16.0,
            "brain_region_id": 10703,
            "brain_region": "DG-mo"
        },
        "channel_1": {
            "x": -0.002517582795765973,
            "y": -0.0031254016699778088,
            ...
        },
        ...
    }
    ```
