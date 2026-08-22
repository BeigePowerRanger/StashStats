#!/usr/bin/env python3
"""
Live Ravelry API Print Test Script.

Exercises all 7 Ravelry API modules in stashies using live credentials from .env.
Prints structured section headers, HTTP status, execution latency, and pretty-printed
JSON payloads to stdout.

Usage:
    PYTHONPATH=. python scripts/test_ravelry_api.py
"""
import os
import sys
import json
import time
from typing import Any, Callable, Tuple

from dotenv import load_dotenv
from stashies.ravelry_client import RavelryClient


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

LINE = "=" * 60
DASH = "-" * 60


def header(section_num: int, total: int, title: str) -> None:
    print(f"\n{LINE}")
    print(f"  [{section_num}/{total}] {title}")
    print(LINE)


def subheader(title: str) -> None:
    print(f"\n  {DASH}")
    print(f"  {title}")
    print(f"  {DASH}")


def dump_payload(obj: Any, max_items: int = 3) -> None:
    """Pretty-print a payload, truncating long lists to max_items."""
    if isinstance(obj, list):
        total = len(obj)
        truncated = obj[:max_items]
        print(json.dumps(truncated, indent=2))
        if total > max_items:
            print(f"  ... ({total - max_items} more items not shown)")
    elif isinstance(obj, dict):
        print(json.dumps(obj, indent=2))
    else:
        print(repr(obj))


def run_call(label: str, func: Callable, *args, **kwargs) -> Tuple[bool, Any, int]:
    """
    Execute an API call, print status, return (passed, result, duration_ms).

    Args:
        label: Human-readable method name for display.
        func: The callable to invoke.
        *args: Positional arguments for func.
        **kwargs: Keyword arguments for func.

    Returns:
        Tuple of (passed: bool, result: Any, duration_ms: int).
    """
    start = time.time()
    try:
        result = func(*args, **kwargs)
        duration_ms = int((time.time() - start) * 1000)
        print(f"\n  [PASS] {label} ({duration_ms}ms)")
        if result is not None:
            dump_payload(result)
        else:
            print("  (no payload / empty response)")
        return True, result, duration_ms
    except Exception as exc:
        duration_ms = int((time.time() - start) * 1000)
        print(f"\n  [FAIL] {label} ({duration_ms}ms)")
        print(f"         ERROR: {exc}")
        return False, None, duration_ms


# ---------------------------------------------------------------------------
# Main test runner
# ---------------------------------------------------------------------------

def main() -> None:
    """Run live API tests across all 7 Ravelry client modules."""
    load_dotenv()

    api_username = os.getenv("API_USERNAME")
    api_key = os.getenv("API_KEY")
    ravelry_username = os.getenv("RAVELRY_USERNAME") or os.getenv("USERNAME", "")

    if not api_username or not api_key:
        print(LINE)
        print("ERROR: API_USERNAME or API_KEY missing from .env")
        print(LINE)
        sys.exit(1)

    client = RavelryClient(api_username=api_username, api_key=api_key)

    print(f"\n{LINE}")
    print(f"  LIVE RAVELRY API TEST SCRIPT")
    print(f"  Auth user : {api_username}")
    print(f"  Ravelry   : {ravelry_username}")
    print(LINE)

    results = []  # list of (label, passed, duration_ms)
    total_sections = 7
    section = 0

    # ------------------------------------------------------------------
    # 1. Color Families
    # ------------------------------------------------------------------
    section += 1
    header(section, total_sections, "COLOR FAMILIES API")

    passed, color_data, ms = run_call(
        "get_color_families()",
        client.get_color_families
    )
    results.append(("get_color_families()", passed, ms))

    # ------------------------------------------------------------------
    # 2. Yarn Weights
    # ------------------------------------------------------------------
    section += 1
    header(section, total_sections, "YARN WEIGHTS API")

    passed, weights_data, ms = run_call(
        "get_yarn_weights()",
        client.get_yarn_weights
    )
    results.append(("get_yarn_weights()", passed, ms))

    # ------------------------------------------------------------------
    # 3. Yarn Search + Get
    # ------------------------------------------------------------------
    section += 1
    header(section, total_sections, "YARN API")

    yarn_query = "Cascade 220"
    passed, yarn_list, ms = run_call(
        f"search_yarn(query={yarn_query!r})",
        client.search_yarn,
        yarn_query
    )
    results.append((f"search_yarn({yarn_query!r})", passed, ms))

    if yarn_list:
        yarn_id = yarn_list[0].get("id")
        if yarn_id:
            passed, yarn_detail, ms = run_call(
                f"get_yarn(yarn_id={yarn_id})",
                client.get_yarn,
                yarn_id
            )
            results.append((f"get_yarn(id={yarn_id})", passed, ms))
        else:
            print("  [SKIP] get_yarn() — no yarn ID found in search results")
    else:
        print("  [SKIP] get_yarn() — search returned no results")

    # ------------------------------------------------------------------
    # 4. Pattern Search + Get
    # ------------------------------------------------------------------
    section += 1
    header(section, total_sections, "PATTERN API")

    pattern_query = "simple beanie"
    passed, pattern_list, ms = run_call(
        f"search_patterns(query={pattern_query!r})",
        client.search_patterns,
        pattern_query
    )
    results.append((f"search_patterns({pattern_query!r})", passed, ms))

    if pattern_list:
        pattern_id = pattern_list[0].get("id")
        if pattern_id:
            passed, pattern_detail, ms = run_call(
                f"get_pattern(pattern_id={pattern_id})",
                client.get_pattern,
                pattern_id
            )
            results.append((f"get_pattern(id={pattern_id})", passed, ms))
        else:
            print("  [SKIP] get_pattern() — no pattern ID in search results")
    else:
        print("  [SKIP] get_pattern() — search returned no results")

    # ------------------------------------------------------------------
    # 5. Stash CRUD
    # ------------------------------------------------------------------
    section += 1
    header(section, total_sections, "STASH API")

    subheader("List stash")
    passed, stash_list, ms = run_call(
        f"get_stash_list(username={ravelry_username!r})",
        client.get_stash_list,
        ravelry_username
    )
    results.append((f"get_stash_list({ravelry_username!r})", passed, ms))
    if stash_list:
        print(f"  Total stash items returned: {len(stash_list)}")

    subheader("Create stash item (test entry)")
    test_stash_data = {
        "stash_yarn_name": "API Test Yarn",
        "color_name": "Test Blue",
        "colorway_name": "Test Blue",
        "skein_count": 1,
        "notes": "Created by test_ravelry_api.py — safe to delete"
    }
    passed, created_stash, ms = run_call(
        "create_stash()",
        client.create_stash,
        ravelry_username,
        test_stash_data
    )
    results.append(("create_stash()", passed, ms))

    stash_id = None
    if created_stash:
        stash_id = (
            created_stash.get("id")
            or (created_stash.get("stash") or {}).get("id")
        )

    if stash_id:
        subheader(f"Update stash item (id={stash_id})")
        update_data = {
            "stash_yarn_name": "API Test Yarn (Updated)",
            "skein_count": 2,
            "notes": "Updated by test_ravelry_api.py"
        }
        passed, updated_stash, ms = run_call(
            f"update_stash(stash_id={stash_id})",
            client.update_stash,
            ravelry_username,
            stash_id,
            update_data
        )
        results.append((f"update_stash(id={stash_id})", passed, ms))

        subheader(f"Delete stash item (id={stash_id})")
        passed, del_result, ms = run_call(
            f"delete_stash(stash_id={stash_id})",
            client.delete_stash,
            ravelry_username,
            stash_id
        )
        results.append((f"delete_stash(id={stash_id})", passed, ms))
        print(f"  Delete returned: {del_result}")
    else:
        print("  [SKIP] update_stash / delete_stash — create did not return a stash ID")

    # ------------------------------------------------------------------
    # 6. Favorites
    # ------------------------------------------------------------------
    section += 1
    header(section, total_sections, "FAVORITES API")

    subheader("List favorites")
    passed, fav_list, ms = run_call(
        "get_favorites()",
        client.get_favorites
    )
    results.append(("get_favorites()", passed, ms))
    if fav_list:
        print(f"  Total favorites: {len(fav_list)}")

    subheader("Add favorite (test pattern)")
    # Use a known stable Ravelry pattern ID: 26 = Log Cabin Blanket
    fav_data = {"favorited_id": 26, "favorited_type": "Pattern"}
    passed, added_fav, ms = run_call(
        "add_favorite(pattern_id=26)",
        client.add_favorite,
        fav_data
    )
    results.append(("add_favorite(pattern_id=26)", passed, ms))

    fav_id = None
    if added_fav and isinstance(added_fav, dict):
        fav_id = added_fav.get("id")

    if fav_id:
        subheader(f"Remove favorite (id={fav_id})")
        passed, rem_result, ms = run_call(
            f"remove_favorite(fav_id={fav_id})",
            client.remove_favorite,
            fav_id
        )
        results.append((f"remove_favorite(id={fav_id})", passed, ms))
        print(f"  Remove returned: {rem_result}")
    else:
        print("  [SKIP] remove_favorite — no favorite ID returned from add")

    # ------------------------------------------------------------------
    # 7. Queue
    # ------------------------------------------------------------------
    section += 1
    header(section, total_sections, "QUEUE API")

    subheader("List queue")
    passed, queue_list, ms = run_call(
        "get_queue()",
        client.get_queue
    )
    results.append(("get_queue()", passed, ms))
    if queue_list:
        print(f"  Total queue items: {len(queue_list)}")

    subheader("Add to queue (test pattern)")
    queue_data = {"pattern_id": 26}
    passed, added_queue, ms = run_call(
        "add_to_queue(pattern_id=26)",
        client.add_to_queue,
        queue_data
    )
    results.append(("add_to_queue(pattern_id=26)", passed, ms))

    queue_item_id = None
    if added_queue and isinstance(added_queue, dict):
        queue_item_id = added_queue.get("id")

    if queue_item_id:
        subheader(f"Remove from queue (id={queue_item_id})")
        passed, rem_q, ms = run_call(
            f"remove_from_queue(queue_id={queue_item_id})",
            client.remove_from_queue,
            queue_item_id
        )
        results.append((f"remove_from_queue(id={queue_item_id})", passed, ms))
        print(f"  Remove returned: {rem_q}")
    else:
        print("  [SKIP] remove_from_queue — no queue item ID returned from add")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    total_calls = len(results)
    total_passed = sum(1 for _, p, _ in results if p)
    total_failed = total_calls - total_passed
    total_time_ms = sum(ms for _, _, ms in results)

    print(f"\n\n{LINE}")
    print(f"  LIVE API TEST SUMMARY")
    print(DASH)
    print(f"  {'Endpoint':<40} {'Status':<8} {'Time':>6}")
    print(f"  {DASH}")
    for label, passed, ms in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {label:<40} {status:<8} {ms:>4}ms")
    print(f"  {DASH}")
    print(f"  Total calls : {total_calls}")
    print(f"  Passed      : {total_passed}")
    print(f"  Failed      : {total_failed}")
    print(f"  Total time  : {total_time_ms / 1000:.2f}s")
    print(LINE)

    sys.exit(0 if total_failed == 0 else 1)


if __name__ == "__main__":
    main()
