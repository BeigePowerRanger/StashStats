"""Stash and project yarn consumption analytics and correlation calculator."""

from typing import Any

from stashstats.models.analytics import ProjectConsumptionSummary, ProjectUsageRecord
from stashstats.models.project import Project
from stashstats.models.stash import StashItem


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
        stash_by_id: dict[int, StashItem] = {item.id: item for item in stash_items if item.id}
        stash_by_yarn: dict[int, list[StashItem]] = {}
        for item in stash_items:
            yarn_id = getattr(item, "yarn_id", None) or (item.yarn.id if item.yarn else None)
            if yarn_id:
                stash_by_yarn.setdefault(yarn_id, []).append(item)

        results: list[ProjectUsageRecord] = []
        seen_keys: set[tuple[int | None, int | None, str | None]] = set()

        # 1. Correlate from external Project records
        for proj in (projects or []):
            for pack in getattr(proj, "packs", []):
                matched_stash: StashItem | None = None
                if pack.stash_id and pack.stash_id in stash_by_id:
                    matched_stash = stash_by_id[pack.stash_id]
                elif pack.yarn_id and pack.yarn_id in stash_by_yarn:
                    candidates = stash_by_yarn[pack.yarn_id]
                    matched_stash = next(
                        (c for c in candidates if c.colorway_name == pack.colorway),
                        candidates[0] if candidates else None,
                    )

                if matched_stash or pack.stash_id or pack.yarn_id:
                    stash_id = matched_stash.id if matched_stash else pack.stash_id
                    yarn_name = (
                        matched_stash.name
                        if matched_stash
                        else (matched_stash.yarn.name if matched_stash and matched_stash.yarn else pack.colorway or "Project Yarn")
                    )

                    skeins = pack.skeins or 0.0
                    yards = pack.total_yards or 0.0
                    if yards == 0.0 and pack.yards_per_skein and skeins:
                        yards = pack.yards_per_skein * skeins
                    meters = pack.total_meters or (yards * 0.9144 if yards else 0.0)
                    grams = pack.total_grams or 0.0
                    if grams == 0.0 and pack.grams_per_skein and skeins:
                        grams = pack.grams_per_skein * skeins

                    rec_key = (proj.id, stash_id, pack.colorway)
                    seen_keys.add(rec_key)

                    results.append(
                        ProjectUsageRecord(
                            project_id=proj.id,
                            project_name=proj.name or f"Project #{proj.id}",
                            pattern_name=proj.pattern_name,
                            status_name=proj.status_name,
                            craft_name=proj.craft_name,
                            completed_date=proj.completed,
                            stash_id=stash_id,
                            yarn_name=yarn_name,
                            colorway=pack.colorway,
                            skeins_used=round(skeins, 2),
                            yards_used=round(yards, 2),
                            meters_used=round(meters, 2),
                            grams_used=round(grams, 2),
                        )
                    )

        # 2. Correlate from StashItem packs
        for item in stash_items:
            for pack in getattr(item, "packs", []):
                if not pack:
                    continue
                proj_id = getattr(pack, "project_id", None)
                if proj_id and (proj_id, item.id, pack.colorway) not in seen_keys:
                    skeins = pack.skeins or 0.0
                    yards = pack.total_yards or 0.0
                    if yards == 0.0 and getattr(pack, "yards_per_skein", None) and skeins:
                        yards = pack.yards_per_skein * skeins
                    meters = pack.total_meters or (yards * 0.9144 if yards else 0.0)
                    grams = pack.total_grams or 0.0
                    if grams == 0.0 and getattr(pack, "grams_per_skein", None) and skeins:
                        grams = pack.grams_per_skein * skeins

                    seen_keys.add((proj_id, item.id, pack.colorway))
                    results.append(
                        ProjectUsageRecord(
                            project_id=proj_id,
                            project_name=f"Project #{proj_id}",
                            pattern_name=None,
                            status_name="In progress",
                            craft_name=None,
                            completed_date=None,
                            stash_id=item.id,
                            yarn_name=item.name or (item.yarn.name if item.yarn else "Stash Yarn"),
                            colorway=pack.colorway or item.colorway_name,
                            skeins_used=round(skeins, 2),
                            yards_used=round(yards, 2),
                            meters_used=round(meters, 2),
                            grams_used=round(grams, 2),
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
                for entry in entries:
                    p_name = entry.get("project_name") if isinstance(entry, dict) else getattr(entry, "project_name", None)
                    p_id = entry.get("project_id") if isinstance(entry, dict) else getattr(entry, "project_id", None)
                    pat_name = entry.get("pattern_name") if isinstance(entry, dict) else getattr(entry, "pattern_name", None)

                    if p_name or p_id:
                        skeins = abs(entry.get("skeins", 0.0) if isinstance(entry, dict) else (getattr(entry, "skeins", 0.0) or 0.0))
                        yards = abs(entry.get("yards", 0.0) or 0.0 if isinstance(entry, dict) else (getattr(entry, "yards", 0.0) or 0.0))
                        grams = abs(entry.get("grams", 0.0) or 0.0 if isinstance(entry, dict) else (getattr(entry, "grams", 0.0) or 0.0))
                        date_str = entry.get("date") if isinstance(entry, dict) else getattr(entry, "date", None)
                        if not date_str and hasattr(entry, "timestamp"):
                            date_str = entry.timestamp

                        proj_display_name = p_name or f"Project #{p_id}"
                        effective_stash_id = sid or (matched_stash.id if matched_stash else None)
                        yarn_display_name = (
                            matched_stash.name
                            if matched_stash
                            else (matched_stash.yarn.name if matched_stash and matched_stash.yarn else "Stash Yarn")
                        )

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
                                colorway=matched_stash.colorway_name if matched_stash else None,
                                skeins_used=round(skeins, 2),
                                yards_used=round(yards, 2),
                                meters_used=round(yards * 0.9144, 2) if yards else 0.0,
                                grams_used=round(grams, 2),
                            )
                        )

        return results

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
