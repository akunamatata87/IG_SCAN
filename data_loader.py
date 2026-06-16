"""Data loading module for InstaAnalytics Pro.

Reads Instagram export JSON files and extracts profile (username) data.
This module contains pure data logic — no Streamlit dependency.
"""

import json
import logging
import os
import re

__all__ = ["get_json_data", "extract_profiles", "load_dataset"]

logger = logging.getLogger(__name__)

# Pattern that matches Instagram's numbered follower files:
# followers_1.json, followers_2.json, …, followers_99.json, etc.
_FOLLOWERS_NUMBERED_RE = re.compile(r"^followers_\d+\.json$")


def get_json_data(filepath: str) -> object | None:
    """Read and parse a JSON file, returning the decoded Python object.

    Parameters
    ----------
    filepath : str
        Absolute or relative path to the JSON file.

    Returns
    -------
    object | None
        The parsed JSON content (``list``, ``dict``, etc.), or ``None`` if
        the file does not exist or cannot be decoded.
    """
    if not os.path.exists(filepath):
        logger.warning("File not found: %s", filepath)
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        logger.error("Failed to decode %s: %s", filepath, exc)
        return None


def extract_profiles(json_data: object) -> set[str]:
    """Extract Instagram usernames from a parsed JSON structure.

    The function handles several JSON layouts used by Instagram data
    exports across different versions:

    * A top-level ``list`` of entry dicts.
    * A ``dict`` with known keys (``relationships_following``,
      ``relationships_followers``) whose values are lists.
    * A ``dict`` where the first value that is a ``list`` is used as
      a fallback.

    Within each entry dict the username is resolved by trying, in order:

    1. ``entry["string_list_data"][*]["value"]``
    2. ``entry["title"]``
    3. ``entry["value"]``

    Parameters
    ----------
    json_data : object
        Parsed JSON data (typically a ``list`` or ``dict``).

    Returns
    -------
    set[str]
        A set of unique Instagram usernames found in *json_data*.
    """
    profiles: set[str] = set()

    if not json_data:
        return profiles

    # -- 1. Normalise to a flat list of entry dicts --------------------
    data_list: list = []

    if isinstance(json_data, list):
        data_list = json_data
    elif isinstance(json_data, dict):
        # Try well-known top-level keys first.
        known_keys = ("relationships_following", "relationships_followers")
        for key in known_keys:
            if key in json_data:
                data_list = json_data[key]
                break

        # Fallback: use the first list-valued entry in the dict.
        if not data_list:
            for _key, val in json_data.items():
                if isinstance(val, list):
                    data_list = val
                    break

    # -- 2. Extract a username from each entry -------------------------
    for entry in data_list:
        if not isinstance(entry, dict):
            continue

        username: str | None = None

        # Strategy A – string_list_data → value (e.g. followers_1.json)
        if "string_list_data" in entry:
            for item in entry["string_list_data"]:
                if "value" in item:
                    username = item["value"]
                    break

        # Strategy B – title field (e.g. following.json)
        if not username and "title" in entry:
            username = entry["title"]

        # Strategy C – direct value field (legacy formats)
        if not username and "value" in entry:
            username = entry["value"]

        if username:
            profiles.add(username)

    return profiles


def load_dataset(folder_path: str) -> dict[str, set[str]]:
    """Load followers and following sets from an Instagram export folder.

    The function walks *folder_path* recursively to locate the relevant
    JSON files.  For **followers** it collects *all* numbered files that
    match the ``followers_N.json`` pattern (Instagram splits large
    follower lists across multiple files) as well as the plain
    ``followers.json`` variant.  For **following** it looks for
    ``following.json``.

    Parameters
    ----------
    folder_path : str
        Path to the root of a single Instagram data-export snapshot
        (the folder that contains ``followers/`` and ``following/``
        sub-directories, or the JSON files directly).

    Returns
    -------
    dict[str, set[str]]
        A dictionary with two keys:

        * ``"followers"`` — set of follower usernames.
        * ``"following"`` — set of following usernames.

        Either set may be empty if the corresponding files were not
        found or could not be parsed.
    """
    data: dict[str, set[str]] = {"followers": set(), "following": set()}

    follower_paths: list[str] = []
    following_path: str | None = None

    for root, _dirs, files in os.walk(folder_path):
        for filename in files:
            # Collect every followers_N.json *and* the plain followers.json
            if _FOLLOWERS_NUMBERED_RE.match(filename) or filename == "followers.json":
                follower_paths.append(os.path.join(root, filename))

            # following.json — take only the first occurrence
            if following_path is None and filename == "following.json":
                following_path = os.path.join(root, filename)

    # -- Followers (merge all matched files) ---------------------------
    for path in follower_paths:
        json_raw = get_json_data(path)
        extracted = extract_profiles(json_raw)
        if extracted:
            logger.debug("Loaded %d followers from %s", len(extracted), path)
            data["followers"] |= extracted

    # -- Following -----------------------------------------------------
    if following_path is not None:
        json_raw = get_json_data(following_path)
        extracted = extract_profiles(json_raw)
        if extracted:
            logger.debug("Loaded %d following from %s", len(extracted), following_path)
            data["following"] = extracted

    if not data["followers"]:
        logger.warning("No follower profiles found in %s", folder_path)
    if not data["following"]:
        logger.warning("No following profiles found in %s", folder_path)

    return data
