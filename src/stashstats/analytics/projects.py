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


def _normalize_stash_item(item: Any) -> StashItem:
    """Normalize input into a StashItem model instance."""
    if isinstance(item, StashItem):
        return item
    if isinstance(item, dict):
        return StashItem.model_validate(item)
    if hasattr(item, "model_dump"):
        return StashItem.model_validate(item.model_dump())
    return StashItem.model_validate(item)


def _normalize_project(project: Any) -> Project:
    """Normalize input into a Project model instance."""
    if isinstance(project, Project):
        return project
    if isinstance(project, dict):
        return Project.model_validate(project)
    if hasattr(project, "model_dump"):
        return Project.model_validate(project.model_dump())
    return Project.model_validate(project)


class StashProjectUsageCalculator:
    """Correlates project yarn pack allocations with user stash inventory."""

    @classmethod
    def correlate_projects_and_stash(
        cls,
        stash_items: list[StashItem] | list[Any],
        projects: list[Project] | list[Any] | None = None,
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
        normalized_stash: list[StashItem] = [
            _normalize_stash_item(item) for item in (stash_items or [])
        ]
        normalized_projects: list[Project] = [
            _normalize_project(proj) for proj in (projects or [])
        ]

        stash_by_id: dict[Any, StashItem] = {}
        stash_by_yarn: dict[Any, list[StashItem]] = {}
        for item in normalized_stash:
            s_id = item.id
            if s_id is not None:
                stash_by_id[s_id] = item
                stash_by_id[str(s_id)] = item
                try:
                    stash_by_id[int(s_id)] = item
                except (ValueError, TypeError):
                    pass
            yarn_info = item.yarn
            yarn_id = yarn_info.id if yarn_info else None
            if yarn_id is not None:
                stash_by_yarn.setdefault(yarn_id, []).append(item)
                stash_by_yarn.setdefault(str(yarn_id), []).append(item)
                try:
                    stash_by_yarn.setdefault(int(yarn_id), []).append(item)
                except (ValueError, TypeError):
                    pass

        results: list[ProjectUsageRecord] = []
        seen_keys: set[tuple[Any, Any, Any]] = set()

        # 1. Correlate from external Project records
        for proj in normalized_projects:
            proj_id = proj.id
            proj_name = proj.name or f"Project #{proj_id}"
            pattern_name = proj.pattern_name
            status_name = proj.status_name or "Finished"
            craft_name = proj.craft_name
            completed_date = proj.completed
            packs = proj.packs or []

            for pack in packs:
                pack_stash_id = pack.stash_id
                pack_yarn_id = pack.yarn_id
                pack_colorway = pack.colorway
                skeins = pack.skeins or 0.0
                yards = pack.total_yards or 0.0
                meters = pack.total_meters or (yards * 0.9144 if yards else 0.0)
                grams = pack.total_grams or 0.0
                yards_per_skein = pack.yards_per_skein
                grams_per_skein = pack.grams_per_skein

                if yards == 0.0 and yards_per_skein and skeins:
                    yards = float(yards_per_skein) * float(skeins)
                    meters = yards * 0.9144
                if grams == 0.0 and grams_per_skein and skeins:
                    grams = float(grams_per_skein) * float(skeins)

                matched_stash: StashItem | None = None
                if pack_stash_id and pack_stash_id in stash_by_id:
                    matched_stash = stash_by_id[pack_stash_id]
                elif pack_yarn_id and pack_yarn_id in stash_by_yarn:
                    candidates = stash_by_yarn[pack_yarn_id]
                    matched_stash = next(
                        (c for c in candidates if c.colorway_name == pack_colorway),
                        candidates[0] if candidates else None,
                    )

                if matched_stash or pack_stash_id or pack_yarn_id:
                    stash_id = matched_stash.id if matched_stash else pack_stash_id
                    matched_yarn = matched_stash.yarn if matched_stash else None
                    yarn_name = (
                        matched_stash.name
                        if matched_stash and matched_stash.name
                        else (matched_yarn.name if matched_yarn else pack_colorway or "Project Yarn")
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
        for item in normalized_stash:
            item_id = item.id
            item_yarn = item.yarn
            item_name = item.name or (item_yarn.name if item_yarn else "Stash Yarn")
            item_colorway = item.colorway_name
            packs = item.packs or []

            for pack in packs:
                if not pack:
                    continue
                proj_id = pack.project_id
                proj_name = pack.project_name
                if proj_id:
                    try:
                        if int(proj_id) == 0:
                            proj_id = None
                    except (ValueError, TypeError):
                        pass
                if proj_name and not str(proj_name).strip():
                    proj_name = None

                pack_colorway = pack.colorway or item_colorway

                # Only correlate if explicitly linked to a project
                if proj_id or proj_name:
                    skeins = pack.skeins or 0.0
                    yards = pack.total_yards or 0.0
                    grams = pack.total_grams or 0.0
                    yards_per_skein = pack.yards_per_skein
                    grams_per_skein = pack.grams_per_skein
                    if yards == 0.0 and yards_per_skein and skeins:
                        yards = float(yards_per_skein) * float(skeins)
                    if grams == 0.0 and grams_per_skein and skeins:
                        grams = float(grams_per_skein) * float(skeins)
                    meters = pack.total_meters or (yards * 0.9144 if yards else 0.0)

                    # Only if yarn was actually used
                    if float(skeins or 0.0) <= 0 and float(yards or 0.0) <= 0 and float(grams or 0.0) <= 0:
                        continue

                    rec_key = (proj_id or proj_name, item_id, pack_colorway)
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
                matched_yarn = matched_stash.yarn if matched_stash else None
                yarn_display_name = (
                    matched_stash.name
                    if matched_stash and matched_stash.name
                    else (matched_yarn.name if matched_yarn else "Stash Yarn")
                )

                for entry in entries:
                    event_type = _safe_get(entry, "event_type")
                    # If this is an initial purchase/acquisition entry, SKIP IT!
                    if event_type in ("initial", "acquired", "purchase", "in_stash"):
                        continue

                    p_name = (_safe_get(entry, "project_name") or "").strip() or None
                    p_id = _safe_get(entry, "project_id")
                    if p_id:
                        try:
                            if int(p_id) == 0:
                                p_id = None
                        except (ValueError, TypeError):
                            pass

                    # Require an explicit project attribution (project_name or project_id)
                    if not p_name and not p_id:
                        continue

                    raw_skeins = float(_safe_get(entry, "skeins") or 0.0)
                    raw_delta_skeins = float(_safe_get(entry, "delta_skeins") or 0.0)
                    raw_yds = float(_safe_get(entry, "yards") or _safe_get(entry, "delta_yards") or 0.0)
                    raw_g = float(_safe_get(entry, "grams") or _safe_get(entry, "delta_grams") or 0.0)
                    pat_name = (_safe_get(entry, "pattern_name") or "").strip() or None
                    notes = (_safe_get(entry, "notes") or "").strip() or None

                    # Only consumption events count as used yarn
                    is_consumption = (
                        event_type in ("consumed", "usage", "used")
                        or raw_delta_skeins < 0
                        or raw_skeins < 0
                        or raw_yds < 0
                        or raw_g < 0
                        or (p_name is not None or p_id is not None)
                    )

                    if not is_consumption:
                        continue

                    effective_skeins = (
                        abs(raw_delta_skeins)
                        if raw_delta_skeins < 0
                        else (abs(raw_skeins) if raw_skeins < 0 else (abs(raw_skeins) if (p_name or p_id) else 0.0))
                    )
                    used_yards = abs(raw_yds) if raw_yds < 0 else (abs(raw_yds) if (p_name or p_id) else 0.0)
                    used_grams = abs(raw_g) if raw_g < 0 else (abs(raw_g) if (p_name or p_id) else 0.0)

                    if effective_skeins <= 0 and used_yards <= 0 and used_grams <= 0:
                        continue

                    proj_display_name = p_name or f"Project #{p_id}"
                    effective_stash_id = sid or (matched_stash.id if matched_stash else None)

                    yards = used_yards
                    grams = used_grams

                    if yards == 0.0 and effective_skeins > 0:
                        if matched_stash and matched_stash.total_yards and matched_stash.skeins:
                            stash_yards = float(matched_stash.total_yards or 0.0)
                            stash_skeins = float(matched_stash.skeins or 1.0)
                            yards = (stash_yards / stash_skeins) * effective_skeins
                        else:
                            yards = effective_skeins * 200.0

                    if grams == 0.0 and effective_skeins > 0:
                        if matched_stash and matched_stash.total_grams and matched_stash.skeins:
                            stash_grams = float(matched_stash.total_grams or 0.0)
                            stash_skeins = float(matched_stash.skeins or 1.0)
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
                            colorway=matched_stash.colorway_name if matched_stash else None,
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
