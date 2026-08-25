"""Stash and project yarn consumption analytics and correlation calculator."""

from typing import Any

from stashstats.models.analytics import ProjectConsumptionSummary, ProjectUsageRecord
from stashstats.models.project import Project
from stashstats.models.stash import StashItem


def _safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """Safely get an attribute or dictionary key value."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class StashProjectUsageCalculator:
    """Correlates project yarn pack allocations with user stash inventory."""

    @classmethod
    def correlate_projects_and_stash(
        cls,
        stash_items: list[StashItem],
        projects: list[Project] | None = None,
        histories: dict[int, Any] | list[Any] | None = None,
    ) -> list[ProjectUsageRecord]:
        """Match project yarn allocations, packs, and usage ledger entries to stash items.

        Args:
            stash_items: List of user's StashItem records.
            projects: Optional list of user's Project records with packs.
            histories: Optional mapping of stash_id to history ledger records or list of entries.

        Returns:
            List of ProjectUsageRecord correlation objects.
        """
        stash_by_id: dict[int, Any] = {}
        stash_by_yarn: dict[int, list[Any]] = {}
        for item in stash_items:
            s_id = _safe_get(item, "id")
            if s_id:
                stash_by_id[s_id] = item
            yarn_info = _safe_get(item, "yarn")
            yarn_id = _safe_get(item, "yarn_id") or (_safe_get(yarn_info, "id") if yarn_info else None)
            if yarn_id:
                stash_by_yarn.setdefault(yarn_id, []).append(item)

        results: list[ProjectUsageRecord] = []
        seen_keys: set[tuple[Any, Any, Any]] = set()

        # 1. Correlate from external Project records
        for proj in (projects or []):
            proj_id = _safe_get(proj, "id")
            proj_name = _safe_get(proj, "name") or f"Project #{proj_id}"
            pattern_name = _safe_get(proj, "pattern_name")
            status_name = _safe_get(proj, "status_name") or "Finished"
            craft_name = _safe_get(proj, "craft_name")
            completed_date = _safe_get(proj, "completed")
            packs = _safe_get(proj, "packs") or []

            for pack in packs:
                pack_stash_id = _safe_get(pack, "stash_id")
                pack_yarn_id = _safe_get(pack, "yarn_id")
                pack_colorway = _safe_get(pack, "colorway")
                skeins = _safe_get(pack, "skeins") or 0.0
                yards = _safe_get(pack, "total_yards") or 0.0
                meters = _safe_get(pack, "total_meters") or (yards * 0.9144 if yards else 0.0)
                grams = _safe_get(pack, "total_grams") or 0.0
                yards_per_skein = _safe_get(pack, "yards_per_skein")
                grams_per_skein = _safe_get(pack, "grams_per_skein")

                if yards == 0.0 and yards_per_skein and skeins:
                    yards = float(yards_per_skein) * float(skeins)
                    meters = yards * 0.9144
                if grams == 0.0 and grams_per_skein and skeins:
                    grams = float(grams_per_skein) * float(skeins)

                matched_stash = None
                if pack_stash_id and pack_stash_id in stash_by_id:
                    matched_stash = stash_by_id[pack_stash_id]
                elif pack_yarn_id and pack_yarn_id in stash_by_yarn:
                    candidates = stash_by_yarn[pack_yarn_id]
                    matched_stash = next(
                        (c for c in candidates if _safe_get(c, "colorway_name") == pack_colorway),
                        candidates[0] if candidates else None,
                    )

                if matched_stash or pack_stash_id or pack_yarn_id:
                    stash_id = _safe_get(matched_stash, "id") if matched_stash else pack_stash_id
                    matched_yarn = _safe_get(matched_stash, "yarn") if matched_stash else None
                    yarn_name = (
                        _safe_get(matched_stash, "name")
                        if matched_stash
                        else (_safe_get(matched_yarn, "name") if matched_yarn else pack_colorway or "Project Yarn")
                    )

                    rec_key = (proj_id, stash_id, pack_colorway)
                    seen_keys.add(rec_key)

                    results.append(
                        ProjectUsageRecord(
                            project_id=proj_id or 0,
                            project_name=proj_name,
                            pattern_name=pattern_name,
                            status_name=status_name,
                            craft_name=craft_name,
                            completed_date=completed_date,
                            stash_id=stash_id,
                            yarn_name=yarn_name,
                            colorway=pack_colorway,
                            skeins_used=round(float(skeins or 0.0), 2),
                            yards_used=round(float(yards or 0.0), 2),
                            meters_used=round(float(meters or 0.0), 2),
                            grams_used=round(float(grams or 0.0), 2),
                        )
                    )

        # 2. Correlate from StashItem packs
        for item in stash_items:
            item_id = _safe_get(item, "id")
            item_yarn = _safe_get(item, "yarn")
            item_name = _safe_get(item, "name") or (_safe_get(item_yarn, "name") if item_yarn else "Stash Yarn")
            item_colorway = _safe_get(item, "colorway_name")
            packs = _safe_get(item, "packs") or []

            for pack in packs:
                if not pack:
                    continue
                proj_id = _safe_get(pack, "project_id")
                proj_name = _safe_get(pack, "project_name") or (f"Project #{proj_id}" if proj_id else None)
                pack_colorway = _safe_get(pack, "colorway") or item_colorway

                if proj_id or proj_name:
                    skeins = _safe_get(pack, "skeins") or 0.0
                    yards = _safe_get(pack, "total_yards") or 0.0
                    yards_per_skein = _safe_get(pack, "yards_per_skein")
                    if yards == 0.0 and yards_per_skein and skeins:
                        yards = float(yards_per_skein) * float(skeins)
                    meters = _safe_get(pack, "total_meters") or (yards * 0.9144 if yards else 0.0)
                    grams = _safe_get(pack, "total_grams") or 0.0
                    grams_per_skein = _safe_get(pack, "grams_per_skein")
                    if grams == 0.0 and grams_per_skein and skeins:
                        grams = float(grams_per_skein) * float(skeins)

                    rec_key = (proj_id, item_id, pack_colorway)
                    if rec_key not in seen_keys:
                        seen_keys.add(rec_key)
                        results.append(
                            ProjectUsageRecord(
                                project_id=proj_id or 0,
                                project_name=proj_name or f"Project #{proj_id or 0}",
                                pattern_name=None,
                                status_name="In progress",
                                craft_name=None,
                                completed_date=None,
                                stash_id=item_id,
                                yarn_name=item_name,
                                colorway=pack_colorway,
                                skeins_used=round(float(skeins or 0.0), 2),
                                yards_used=round(float(yards or 0.0), 2),
                                meters_used=round(float(meters or 0.0), 2),
                                grams_used=round(float(grams or 0.0), 2),
                            )
                        )

        # 3. Correlate from histories dictionary or list
        if histories:
            hist_items: list[tuple[int | None, list[Any]]] = []
            if isinstance(histories, dict):
                for sid, hlist in histories.items():
                    if hasattr(hlist, "entries"):
                        hist_items.append((sid, getattr(hlist, "entries", [])))
                    elif isinstance(hlist, list):
                        hist_items.append((sid, hlist))
            elif isinstance(histories, list):
                hist_items.append((None, histories))

            for sid, entries in hist_items:
                matched_stash = stash_by_id.get(sid) if sid else None
                matched_yarn = _safe_get(matched_stash, "yarn") if matched_stash else None
                yarn_display_name = (
                    _safe_get(matched_stash, "name")
                    if matched_stash
                    else (_safe_get(matched_yarn, "name") if matched_yarn else "Stash Yarn")
                )

                for entry in entries:
                    skeins = abs(float(_safe_get(entry, "skeins") or 0.0))
                    delta_skeins = abs(float(_safe_get(entry, "delta_skeins") or 0.0))
                    effective_skeins = skeins or delta_skeins

                    # Skip non-consumption entries (0 skeins used and 0 yards/grams)
                    raw_yds = abs(float(_safe_get(entry, "yards") or _safe_get(entry, "delta_yards") or 0.0))
                    raw_g = abs(float(_safe_get(entry, "grams") or _safe_get(entry, "delta_grams") or 0.0))
                    if effective_skeins <= 0 and raw_yds <= 0 and raw_g <= 0:
                        continue

                    p_name = _safe_get(entry, "project_name")
                    p_id = _safe_get(entry, "project_id")
                    pat_name = _safe_get(entry, "pattern_name")
                    notes = _safe_get(entry, "notes")

                    proj_display_name = p_name or (f"Project #{p_id}" if p_id else (notes.strip() if notes and notes.strip() else f"{yarn_display_name} Project"))
                    effective_stash_id = sid or (_safe_get(matched_stash, "id") if matched_stash else None)

                    yards = raw_yds
                    grams = raw_g

                    if yards == 0.0 and effective_skeins > 0:
                        if matched_stash and _safe_get(matched_stash, "total_yards") and _safe_get(matched_stash, "skeins"):
                            stash_yards = float(_safe_get(matched_stash, "total_yards") or 0.0)
                            stash_skeins = float(_safe_get(matched_stash, "skeins") or 1.0)
                            yards = (stash_yards / stash_skeins) * effective_skeins
                        else:
                            yards = effective_skeins * 200.0

                    if grams == 0.0 and effective_skeins > 0:
                        if matched_stash and _safe_get(matched_stash, "total_grams") and _safe_get(matched_stash, "skeins"):
                            stash_grams = float(_safe_get(matched_stash, "total_grams") or 0.0)
                            stash_skeins = float(_safe_get(matched_stash, "skeins") or 1.0)
                            grams = (stash_grams / stash_skeins) * effective_skeins
                        else:
                            grams = effective_skeins * 100.0

                    meters = yards * 0.9144 if yards else 0.0
                    date_str = _safe_get(entry, "date") or _safe_get(entry, "timestamp")

                    results.append(
                        ProjectUsageRecord(
                            project_id=p_id or 0,
                            project_name=proj_display_name,
                            pattern_name=pat_name,
                            status_name="Finished",
                            craft_name="Knitting",
                            completed_date=date_str,
                            stash_id=effective_stash_id,
                            yarn_name=yarn_display_name,
                            colorway=_safe_get(matched_stash, "colorway_name") if matched_stash else None,
                            skeins_used=round(effective_skeins, 2),
                            yards_used=round(yards, 2),
                            meters_used=round(meters, 2),
                            grams_used=round(grams, 2),
                        )
                    )

        # Strictly return records where yarn was actually used
        return [
            r
            for r in results
            if (
                float(r.skeins_used or 0.0) > 0
                or float(r.yards_used or 0.0) > 0
                or float(r.grams_used or 0.0) > 0
                or float(r.meters_used or 0.0) > 0
            )
        ]

    @classmethod
    def aggregate_summary(
        cls,
        records: list[ProjectUsageRecord],
    ) -> ProjectConsumptionSummary:
        """Aggregate total project-level consumption metrics across usage records.

        Args:
            records: List of ProjectUsageRecord correlation objects.

        Returns:
            ProjectConsumptionSummary containing totals and project counts.
        """
        if not records:
            return ProjectConsumptionSummary()

        total_yards = sum(r.yards_used for r in records)
        total_meters = sum(r.meters_used for r in records)
        total_grams = sum(r.grams_used for r in records)
        total_skeins = sum(r.skeins_used for r in records)
        unique_project_ids = {r.project_id for r in records}

        return ProjectConsumptionSummary(
            project_usages=records,
            total_yards_consumed=round(total_yards, 2),
            total_meters_consumed=round(total_meters, 2),
            total_grams_consumed=round(total_grams, 2),
            total_skeins_consumed=round(total_skeins, 2),
            project_count=len(unique_project_ids),
        )

    @classmethod
    def get_projects_for_stash_item(
        cls,
        stash_id: int,
        records: list[ProjectUsageRecord],
    ) -> list[ProjectUsageRecord]:
        """Filter usage records down to a specific stash item.

        Args:
            stash_id: Unique stash item database ID.
            records: List of ProjectUsageRecord objects.

        Returns:
            List of ProjectUsageRecord entries linked to the given stash item.
        """
        return [r for r in records if r.stash_id == stash_id]
