"""Domain models for patients, memories, and scheduled tasks."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Patient:
    name: str
    patient_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class Memory:
    patient_id: str
    content: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    memory_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass
class Task:
    patient_id: str
    title: str
    due_at: datetime
    completed: bool = False
    task_id: str = field(default_factory=lambda: str(uuid4()))

