import json
import logging

import boto3
import codeocean.folder
import requests
import aind_session

import models

logger = logging.getLogger(__name__)

S3_DEST_BUCKET = "aind-scratch-data"
S3_DEST_PREFIX = "dynamic-routing/ibl-gui-output"


def validate_locations(locations_input: str) -> dict[str, models.ChannelLocationCCF]:
    locations_dict = json.loads(locations_input)
    if not all(k.startswith("channel_") for k in locations_dict.keys()):
        raise ValueError("Invalid locations input: keys must start with 'channel_'")
    return {k: models.ChannelLocationCCF(**v) for k, v in locations_dict.items()}


def validate_sorted_asset_name(sorted_asset_name_input: str) -> str:
    # ecephys_816308_2025-08-20_15-24-06_sorted_2025-09-20_07-10-14
    if not sorted_asset_name_input.startswith("ecephys_"):
        raise ValueError("Invalid sorted asset name: must start with 'ecephys_'")
    if "_sorted_" not in sorted_asset_name_input:
        raise ValueError("Invalid sorted asset name: must contain '_sorted_'")
    return sorted_asset_name_input


def _get_all_subfiles(
    client,
    computation_id: str,
    folder: codeocean.folder.Folder,
    filename_filter: str | None = "ccf_channel_locations.json",
) -> list[codeocean.folder.FolderItem]:
    """Recursively fetch all bottom-level files matching filename_filter."""
    items = []
    for item in folder.items:
        if item.type == "folder":
            subfolder = client.computations.list_computation_results(
                computation_id=computation_id, path=item.path
            )
            items.extend(_get_all_subfiles(client, computation_id, subfolder, filename_filter))
        elif filename_filter is None or item.name == filename_filter:
            items.append(item)
    return items


def get_computation_subject_id(computation_id: str) -> str:
    """Get the subject ID from the top-level numeric folder of a computation result."""
    logger.info("Getting subject ID for computation %s", computation_id)
    client = aind_session.get_codeocean_client()
    root_folder = client.computations.list_computation_results(computation_id=computation_id)
    result = next((r for r in root_folder.items if str(r.name).isdigit()), None)
    if result is None:
        raise FileNotFoundError("No folder with a numeric name found in computation results.")
    logger.info("Found subject ID: %s", result.name)
    return result.name


def get_computation_file_paths(computation_id: str) -> list[str]:
    """Return paths of all ccf_channel_locations.json files in a computation result."""
    logger.info("Getting file paths for computation %s", computation_id)
    client = aind_session.get_codeocean_client()
    root_folder = client.computations.list_computation_results(computation_id=computation_id)
    files = _get_all_subfiles(client, computation_id, root_folder)
    paths = [f.path for f in files]
    logger.info("Found %d files", len(paths))
    return paths


def get_existing_s3_files(subject_id: str) -> list[str]:
    """List existing S3 keys under the subject's output directory."""
    logger.info("Checking S3 for subject %s", subject_id)
    s3 = boto3.client("s3")
    prefix = f"{S3_DEST_PREFIX}/{subject_id}/"
    try:
        response = s3.list_objects_v2(Bucket=S3_DEST_BUCKET, Prefix=prefix)
        keys = [obj["Key"] for obj in response.get("Contents", [])]
        logger.info("Found %d existing S3 files", len(keys))
        return keys
    except Exception:
        logger.warning("Failed to list S3 objects for prefix %s", prefix, exc_info=True)
        return []


def copy_files_to_s3(computation_id: str, file_paths: list[str]) -> list[str]:
    """Download files from CodeOcean and upload to S3, preserving path structure."""
    logger.info("Copying %d files to S3 for computation %s", len(file_paths), computation_id)
    client = aind_session.get_codeocean_client()
    s3 = boto3.client("s3")
    uploaded = []
    for path in file_paths:
        logger.info("Copying %s", path)
        url = client.computations.get_result_file_urls(
            computation_id=computation_id, path=path
        ).download_url
        content = requests.get(url).text
        s3_key = f"{S3_DEST_PREFIX}/{path}"
        s3.put_object(
            Bucket=S3_DEST_BUCKET,
            Key=s3_key,
            Body=content.encode(),
            ContentType="application/json",
        )
        uploaded.append(s3_key)
        logger.info("Uploaded s3://%s/%s", S3_DEST_BUCKET, s3_key)
    return uploaded
