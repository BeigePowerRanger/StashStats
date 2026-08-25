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
        projects: list[Project],
    ) -> list[ProjectUsageRecord]:
        """Match project yarn allocations to stash items and extract usage records.

        Args:
            stash_items: List of user's StashItem records.
            projects: List of user's Project records with packs.

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

        for proj in projects:
            for pack in getattr(proj, "packs", []):
                matched_stash: StashItem | None = None
                if pack.stash_id and pack.stash_id in stash_by_id:
                    matched_stash = stash_by_id[pack.stash_id]
                elif pack.yarn_id and pack.yarn_id in stash_by_yarn:
                    # Match by colorway or pick first
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
