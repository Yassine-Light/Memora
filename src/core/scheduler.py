"""Background scheduler for due patient tasks."""

from collections.abc import Callable
import time

from .models import Task


class TaskScheduler:
    def __init__(
        self,
        get_tasks: Callable[[], list[Task]],
        on_due_task: Callable[[Task], None],
        interval_seconds: int = 30,
    ) -> None:
        self.get_tasks = get_tasks
        self.on_due_task = on_due_task
        self.interval_seconds = interval_seconds

    def run_once(self) -> None:
        now = __import__("datetime").datetime.utcnow()
        for task in self.get_tasks():
            if not task.completed and task.due_at <= now:
                self.on_due_task(task)

    def run_forever(self) -> None:
        while True:
            self.run_once()
            time.sleep(self.interval_seconds)

