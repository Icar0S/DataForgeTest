"""Data models for Checklist Support QA."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ItemStatus(str, Enum):
    """Status of a checklist item."""
    DONE = "DONE"
    NOT_DONE = "NOT_DONE"


@dataclass
class ChecklistItem:
    """A single checklist item."""
    id: str
    code: str
    title: str
    manual: str
    references: List[str]
    priority_weight: int


@dataclass
class ChecklistDimension:
    """A dimension/category of checklist items."""
    id: str
    name: str
    items: List[ChecklistItem]


@dataclass
class ChecklistTemplate:
    """Template containing all dimensions and items."""
    name: str
    dimensions: List[ChecklistDimension]


@dataclass
class ChecklistMark:
    """A mark/answer for a checklist item."""
    id: str
    run_id: str
    item_id: str
    status: ItemStatus


@dataclass
class ChecklistRun:
    """A checklist run/session for a user."""
    id: str
    user_id: str
    project_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    marks: Dict[str, ItemStatus] = field(default_factory=dict)


def template_to_dict(template: ChecklistTemplate) -> Dict[str, Any]:
    """Convert ChecklistTemplate to dictionary."""
    return {
        "name": template.name,
        "dimensions": [
            {
                "id": dim.id,
                "name": dim.name,
                "items": [
                    {
                        "id": item.id,
                        "code": item.code,
                        "title": item.title,
                        "manual": item.manual,
                        "references": item.references,
                        "priority_weight": item.priority_weight
                    }
                    for item in dim.items
                ]
            }
            for dim in template.dimensions
        ]
    }


def template_from_dict(data: Dict[str, Any]) -> ChecklistTemplate:
    """Create ChecklistTemplate from dictionary."""
    dimensions = []
    for dim_data in data.get("dimensions", []):
        items = []
        for item_data in dim_data.get("items", []):
            items.append(ChecklistItem(
                id=item_data["id"],
                code=item_data["code"],
                title=item_data["title"],
                manual=item_data["manual"],
                references=item_data["references"],
                priority_weight=item_data["priority_weight"]
            ))
        dimensions.append(ChecklistDimension(
            id=dim_data["id"],
            name=dim_data["name"],
            items=items
        ))
    
    return ChecklistTemplate(
        name=data["name"],
        dimensions=dimensions
    )


def run_to_dict(run: ChecklistRun) -> Dict[str, Any]:
    """Convert ChecklistRun to dictionary."""
    return {
        "id": run.id,
        "user_id": run.user_id,
        "project_id": run.project_id,
        "created_at": run.created_at.isoformat(),
        "updated_at": run.updated_at.isoformat(),
        "marks": {k: v.value for k, v in run.marks.items()}
    }


def run_from_dict(data: Dict[str, Any]) -> ChecklistRun:
    """Create ChecklistRun from dictionary."""
    marks = {k: ItemStatus(v) for k, v in data.get("marks", {}).items()}
    
    return ChecklistRun(
        id=data["id"],
        user_id=data["user_id"],
        project_id=data.get("project_id"),
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
        marks=marks
    )
