"""
State Manager for InstaAnalytics Pro.

Manages a persistent world_state.json file that stores:
- A baseline snapshot (full follower/following sets from the first import)
- Incremental events (diffs) for each subsequent snapshot
- The current follower/following sets for quick access
- Snapshot metadata (counts, timestamps, labels)

This replaces the legacy approach of maintaining 84+ date-named folders.
"""

import json
import os
import shutil
import logging
from datetime import datetime
from typing import Optional

from data_loader import load_dataset

logger = logging.getLogger(__name__)

__all__ = [
    'load_state', 'save_state', 'import_snapshot',
    'migrate_from_folders', 'get_state_at', 'get_snapshot_labels',
    'get_events_between', 'get_trend_data', 'get_comparison_data',
    'STATE_VERSION',
]

STATE_VERSION = 1
DEFAULT_STATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "world_state.json")


def _now_iso() -> str:
    """Return current local time as ISO 8601 string."""
    return datetime.now().isoformat(timespec='seconds')


def get_latest_state_path(directory: str) -> Optional[str]:
    """Find the latest world_state_*.json file in the given directory."""
    import glob
    files = glob.glob(os.path.join(directory, "world_state_*.json"))
    
    # Filter out backups
    files = [f for f in files if "backup" not in f.lower()]
    
    if not files:
        # Fallback to legacy world_state.json
        legacy_path = os.path.join(directory, "world_state.json")
        if os.path.exists(legacy_path):
            return legacy_path
        return None
        
    # Sort files by name (which contains YYYY-MM-DD_HH-MM-SS)
    files.sort(reverse=True)
    return files[0]

def load_state(path: Optional[str] = None) -> Optional[dict]:
    """
    Load the world state from a JSON file.

    Args:
        path: Path to the state file. Defaults to latest world_state_*.json next to this script.

    Returns:
        The state dict, or None if the file doesn't exist or is invalid.
    """
    if not path:
        path = get_latest_state_path(os.path.dirname(os.path.abspath(__file__)))
        
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        if state.get('version') != STATE_VERSION:
            logger.warning("State file version mismatch: expected %d, got %s",
                           STATE_VERSION, state.get('version'))
        return state
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Failed to load state file %s: %s", path, e)
        return None


def save_state(state: dict, path: Optional[str] = None) -> bool:
    """
    Save the world state to a JSON file.
    Always creates a new file with the current timestamp and keeps only the latest 2 files.

    Args:
        state: The state dict to save.
        path: Optional specific path to save to. If None, generates a timestamped name.

    Returns:
        True if saved successfully, False otherwise.
    """
    directory = os.path.dirname(os.path.abspath(__file__))
    
    if not path:
        now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(directory, f"world_state_{now_str}.json")

    try:
        state['last_updated'] = _now_iso()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
        # Clean up old files: keep only the newest 2
        import glob
        files = glob.glob(os.path.join(directory, "world_state_*.json"))
        files = [f for f in files if "backup" not in f.lower()]
        files.sort(reverse=True)
        
        for old_file in files[2:]:
            try:
                os.remove(old_file)
            except OSError:
                pass
                
        # Also clean up legacy world_state.json if it exists and we have newer ones
        legacy_path = os.path.join(directory, "world_state.json")
        if os.path.exists(legacy_path) and len(files) >= 1:
            try:
                os.remove(legacy_path)
            except OSError:
                pass
                
        return True
    except OSError as e:
        logger.error("Failed to save state file %s: %s", path, e)
        return False


def _create_empty_state() -> dict:
    """Create a new empty state structure."""
    return {
        "version": STATE_VERSION,
        "last_updated": _now_iso(),
        "current": {
            "followers": [],
            "following": []
        },
        "baseline": None,  # Set on first import
        "snapshots": []
    }


def import_snapshot(
    state: Optional[dict],
    new_data: dict,
    label: Optional[str] = None
) -> tuple[dict, dict]:
    """
    Import a new data snapshot, compute diffs, and update the state.

    Args:
        state: The current state dict, or None for first import.
        new_data: Dict with 'followers' and 'following' keys, each a set of usernames.
        label: Optional label for this snapshot (e.g. a date string).

    Returns:
        Tuple of (updated_state, events_summary).
        events_summary has keys: new_followers, lost_followers, new_following, lost_following
        (each a list of usernames).
    """
    if label is None:
        label = datetime.now().strftime("%Y-%m-%d")

    new_followers = set(new_data.get('followers', set()))
    new_following = set(new_data.get('following', set()))

    if state is None:
        # First import — create baseline
        state = _create_empty_state()
        state['baseline'] = {
            "label": label,
            "followers": sorted(new_followers),
            "following": sorted(new_following)
        }
        state['current'] = {
            "followers": sorted(new_followers),
            "following": sorted(new_following)
        }
        state['snapshots'] = [{
            "label": label,
            "timestamp": _now_iso(),
            "follower_count": len(new_followers),
            "following_count": len(new_following),
            "events": None  # Baseline — no events
        }]

        events_summary = {
            "new_followers": [],
            "lost_followers": [],
            "new_following": [],
            "lost_following": [],
            "is_baseline": True
        }
        return state, events_summary

    # Subsequent import — compute diffs against current state
    current_followers = set(state['current']['followers'])
    current_following = set(state['current']['following'])

    gained_followers = sorted(new_followers - current_followers)
    lost_followers_list = sorted(current_followers - new_followers)
    gained_following = sorted(new_following - current_following)
    lost_following_list = sorted(current_following - new_following)

    events_summary = {
        "new_followers": gained_followers,
        "lost_followers": lost_followers_list,
        "new_following": gained_following,
        "lost_following": lost_following_list,
        "is_baseline": False
    }

    # Check if there are any changes
    has_changes = any([gained_followers, lost_followers_list,
                       gained_following, lost_following_list])

    # Always record the snapshot (even if no changes, for trend tracking)
    snapshot = {
        "label": label,
        "timestamp": _now_iso(),
        "follower_count": len(new_followers),
        "following_count": len(new_following),
        "events": {
            "new_followers": gained_followers,
            "lost_followers": lost_followers_list,
            "new_following": gained_following,
            "lost_following": lost_following_list
        } if has_changes else {
            "new_followers": [],
            "lost_followers": [],
            "new_following": [],
            "lost_following": []
        }
    }
    state['snapshots'].append(snapshot)

    # Update current state
    state['current'] = {
        "followers": sorted(new_followers),
        "following": sorted(new_following)
    }

    return state, events_summary


def migrate_from_folders(
    root_path: str,
    state_path: Optional[str] = None
) -> tuple[Optional[dict], int]:
    """
    Migrate all legacy date-named folders into a single world_state.json.

    Reads folders in sorted order, builds the baseline from the first folder,
    then computes incremental diffs for each subsequent folder.

    Args:
        root_path: Path to the root directory containing date-named subfolders.
        state_path: Path to save the state file.

    Returns:
        Tuple of (state, snapshot_count). state is None if migration failed.
    """
    if not os.path.isdir(root_path):
        logger.error("Migration root path not found: %s", root_path)
        return None, 0

    subfolders = sorted([
        f.path for f in os.scandir(root_path)
        if f.is_dir() and not f.name.startswith('.')
    ])

    if not subfolders:
        logger.warning("No subfolders found in %s", root_path)
        return None, 0

    state = None
    count = 0

    for folder_path in subfolders:
        folder_name = os.path.basename(folder_path)
        data = load_dataset(folder_path)

        # Skip folders that yielded no data
        if not data['followers'] and not data['following']:
            logger.info("Skipping empty folder: %s", folder_name)
            continue

        state, _ = import_snapshot(state, data, label=folder_name)
        count += 1

    if state is not None:
        save_state(state, state_path)

    return state, count


def get_snapshot_labels(state: dict) -> list[str]:
    """
    Get all snapshot labels in chronological order.

    Args:
        state: The state dict.

    Returns:
        List of label strings.
    """
    return [s['label'] for s in state.get('snapshots', [])]


def get_state_at(state: dict, target_label: str) -> dict:
    """
    Reconstruct the follower/following sets at a given snapshot label.

    Starts from the baseline and replays events forward until the target.

    Args:
        state: The state dict.
        target_label: The snapshot label to reconstruct.

    Returns:
        Dict with 'followers' (set) and 'following' (set).
    """
    baseline = state.get('baseline')
    if baseline is None:
        return {'followers': set(), 'following': set()}

    followers = set(baseline['followers'])
    following = set(baseline['following'])

    for snapshot in state.get('snapshots', [])[1:]:  # Skip baseline (index 0)
        events = snapshot.get('events')
        if events:
            followers.update(events.get('new_followers', []))
            followers.difference_update(events.get('lost_followers', []))
            following.update(events.get('new_following', []))
            following.difference_update(events.get('lost_following', []))

        if snapshot['label'] == target_label:
            break

    return {'followers': followers, 'following': following}


def get_events_between(
    state: dict,
    label_start: str,
    label_end: str
) -> list[dict]:
    """
    Get all events between two snapshot labels (exclusive start, inclusive end).

    Args:
        state: The state dict.
        label_start: Start label (exclusive).
        label_end: End label (inclusive).

    Returns:
        List of event dicts with keys: date, username, type.
    """
    events = []
    in_range = False

    for snapshot in state.get('snapshots', []):
        if snapshot['label'] == label_start:
            in_range = True
            continue

        if in_range:
            snap_events = snapshot.get('events')
            if snap_events:
                date = snapshot['label']
                for u in snap_events.get('new_followers', []):
                    events.append({"date": date, "username": u, "type": "new_follower"})
                for u in snap_events.get('lost_followers', []):
                    events.append({"date": date, "username": u, "type": "unfollower"})
                for u in snap_events.get('new_following', []):
                    events.append({"date": date, "username": u, "type": "new_following"})
                for u in snap_events.get('lost_following', []):
                    events.append({"date": date, "username": u, "type": "unfollowed"})

            if snapshot['label'] == label_end:
                break

    return events


def get_comparison_data(
    state: dict,
    label_start: str,
    label_end: str
) -> dict:
    """
    Compute comparison data between two snapshots using set reconstruction.

    This is the most accurate method — it reconstructs the full sets at both
    points and performs set operations, correctly handling users who leave
    and rejoin between the two dates.

    Args:
        state: The state dict.
        label_start: The T0 label.
        label_end: The T1 label.

    Returns:
        Dict with keys:
        - f1, f2: follower sets at T0 and T1
        - ing1, ing2: following sets at T0 and T1
        - gained: f2 - f1
        - lost: f1 - f2
        - nfb: ing2 - f2 (not following back)
        - fans: f2 - ing2
        - friends: f2 & ing2
    """
    state_t0 = get_state_at(state, label_start)
    state_t1 = get_state_at(state, label_end)

    f1 = state_t0['followers']
    f2 = state_t1['followers']
    ing1 = state_t0['following']
    ing2 = state_t1['following']

    return {
        'f1': f1, 'f2': f2,
        'ing1': ing1, 'ing2': ing2,
        'gained': f2 - f1,
        'lost': f1 - f2,
        'nfb': ing2 - f2,
        'fans': f2 - ing2,
        'friends': f2 & ing2,
    }


def get_trend_data(state: dict) -> list[dict]:
    """
    Get follower/following counts over time for trend charts.

    Args:
        state: The state dict.

    Returns:
        List of dicts with keys: label, follower_count, following_count, ratio.
    """
    trend = []
    for snapshot in state.get('snapshots', []):
        fc = snapshot['follower_count']
        igc = snapshot['following_count']
        ratio = round(fc / igc, 2) if igc > 0 else 0
        trend.append({
            "label": snapshot['label'],
            "follower_count": fc,
            "following_count": igc,
            "ratio": ratio
        })
    return trend


def get_all_events(state: dict) -> list[dict]:
    """
    Get all events across all snapshots for the full timeline view.

    Args:
        state: The state dict.

    Returns:
        List of event dicts with keys: date, username, type, link.
    """
    events = []
    for snapshot in state.get('snapshots', []):
        snap_events = snapshot.get('events')
        if not snap_events:
            continue

        date = snapshot['label']
        for u in snap_events.get('new_followers', []):
            events.append({
                "date": date, "username": u,
                "type": "new_follower",
                "link": f"https://instagram.com/{u}"
            })
        for u in snap_events.get('lost_followers', []):
            events.append({
                "date": date, "username": u,
                "type": "unfollower",
                "link": f"https://instagram.com/{u}"
            })
        for u in snap_events.get('new_following', []):
            events.append({
                "date": date, "username": u,
                "type": "new_following",
                "link": f"https://instagram.com/{u}"
            })
        for u in snap_events.get('lost_following', []):
            events.append({
                "date": date, "username": u,
                "type": "unfollowed",
                "link": f"https://instagram.com/{u}"
            })

    return events
