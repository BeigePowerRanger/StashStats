"""Unit tests for Project and Queue data models."""

import pytest
from pydantic import ValidationError
from stashstats.models import (
    Project,
    ProjectListResult,
    ProjectListResponse,
    ProjectDetailResponse,
    QueuedProject,
    QueueListResponse,
    Paginator,
)

def test_project_list_result_validation():
    data = {
        "id": 36759869,
        "name": "Anniversary Scarf",
        "status_name": "In progress",
        "progress": 45,
        "craft_name": "Knitting",
        "started": "2025/05/24",
        "completed": None,
        "tag_names": ["gift", "alpaca"],
    }
    p = ProjectListResult.model_validate(data)
    assert p.id == 36759869
    assert p.name == "Anniversary Scarf"
    assert p.progress == 45
    assert p.status_name == "In progress"
    assert "gift" in p.tag_names

def test_project_list_response():
    data = {
        "projects": [
            {"id": 1, "name": "Project 1", "progress": 10},
            {"id": 2, "name": "Project 2", "progress": None},
        ],
        "paginator": {"page": 1, "page_size": 25, "page_count": 1, "results": 2},
    }
    resp = ProjectListResponse.model_validate(data)
    assert len(resp.projects) == 2
    assert resp.projects[1].progress == 0  # None coerced to 0

def test_project_detail_response():
    data = {
        "project": {
            "id": 100,
            "name": "Detailed Sweater",
            "packs": [
                {"id": 55, "skeins": 4.0, "colorway": "Ochre", "total_yards": 880.0}
            ],
            "notes": "Used size US 7 needles.",
        },
        "comments": [{"id": 1, "comment": "Beautiful work!"}],
    }
    detail = ProjectDetailResponse.model_validate(data)
    assert detail.project.id == 100
    assert len(detail.project.packs) == 1
    assert detail.project.packs[0].colorway == "Ochre"
    assert len(detail.comments) == 1

def test_queue_list_response():
    data = {
        "queued_projects": [
            {"id": 10, "name": "Sophie Scarf", "sort_order": 1, "pattern_name": "Sophie Scarf"}
        ],
        "paginator": {"page": 1, "page_size": 10, "page_count": 1, "results": 1},
    }
    q = QueueListResponse.model_validate(data)
    assert len(q.queued_projects) == 1
    assert q.queued_projects[0].name == "Sophie Scarf"
