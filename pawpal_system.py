from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum


class Frequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    ONCE = "once"

@dataclass
class Task:
    description: str
    due_time: datetime.time  # e.g. datetime.time(8, 0)
    category: str
    frequency: Frequency   # e.g. Frequency.DAILY, Frequency.WEEKLY, Frequency.ONCE
    is_completed: bool = False
    due_date: date = field(default_factory=date.today)

    def __post_init__(self):
        """Normalize category/frequency and parse due_time and due_date from strings if needed."""
        self.category = self.category.lower()
        if isinstance(self.due_time, str):
            hour, minute = map(int, self.due_time.split(":"))
            self.due_time = time(hour=hour, minute=minute)
        if isinstance(self.frequency, str):
            self.frequency = Frequency(self.frequency.lower())
        if isinstance(self.due_date, str):
            self.due_date = date.fromisoformat(self.due_date)

    def mark_complete(self):
        """Mark this task as completed."""
        self.is_completed = True

    def next_occurrence(self) -> "Task | None":
        """
        Return a new Task scheduled for the next occurrence based on frequency.

        - DAILY:  due_date advances by 1 day  (timedelta(days=1))
        - WEEKLY: due_date advances by 7 days (timedelta(weeks=1))
        - ONCE:   returns None — task does not recur

        The new Task is identical in every other way (description, time, category).
        """
        if self.frequency == Frequency.DAILY:
            next_date = self.due_date + timedelta(days=1)
        elif self.frequency == Frequency.WEEKLY:
            next_date = self.due_date + timedelta(weeks=1)
        else:
            return None
        return Task(
            description=self.description,
            due_time=self.due_time,
            category=self.category,
            frequency=self.frequency,
            due_date=next_date,
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int

    def __post_init__(self):
        """Initialize empty tasks list, task index, and health notes."""
        self.tasks = []
        self.task_index = {}
        self.health_notes = []

    def add_task(self, task: Task):
        """Add a task to this pet, raising ValueError if a duplicate description exists."""
        if task.description.lower() in self.task_index:
            raise ValueError(f"Task with description '{task.description}' already exists.")
        self.tasks.append(task)
        self.task_index[task.description.lower()] = task

    def add_health_note(self, note: str):
        """Append a timestamped health note to this pet's health_notes list."""
        timestamped = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {note}"
        self.health_notes.append(timestamped)

    def get_summary(self) -> str:
        """Return a formatted string with the pet's name, species, age, and pending/note counts."""
        pending = [t for t in self.tasks if not t.is_completed]
        lines = [
            f"Name: {self.name}",
            f"Species: {self.species}",
            f"Age: {self.age}",
            f"Pending tasks: {len(pending)}",
            f"Health notes: {len(self.health_notes)}",
        ]
        return "\n".join(lines)

@dataclass
class Owner:
    name: str
    pets: list[Pet] = field(default_factory=list)
    _task_cache: list[tuple[str, Task]] = field(default_factory=list, init=False)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner and invalidate the task cache."""
        self.pets.append(pet)
        self._invalidate_cache()

    def _invalidate_cache(self):
        """Invalidate the cached tasks."""
        self._task_cache = []

    def get_all_tasks(self) -> list[tuple[str, Task]]:
        """Returns (pet_name, task) pairs across all pets, with caching."""
        if not self._task_cache:
            self._task_cache = [(pet.name, task) for pet in self.pets for task in pet.tasks]
        return self._task_cache


class Scheduler:
    """Retrieves, organizes, and manages tasks across all pets for an owner."""

    def __init__(self, owner: Owner):
        """Initialize the scheduler with an owner and build a lowercase pet name lookup."""
        self.owner = owner
        self.pet_lookup = {pet.name.lower(): pet for pet in owner.pets}

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted ascending by due_time."""
        return sorted(tasks, key=lambda t: t.due_time)

    def get_pending_tasks(self) -> list[tuple[str, Task]]:
        """All incomplete tasks, sorted by due_time."""
        pending = [
            (pet_name, task)
            for pet_name, task in self.owner.get_all_tasks()
            if not task.is_completed
        ]
        return sorted(pending, key=lambda pair: pair[1].due_time)  # tuples keep pet_name, sort by task time

    def filter_tasks(
        self,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[tuple[str, Task]]:
        """
        Filter tasks by completion status and/or pet name.

        Args:
            completed: If True, return only completed tasks. If False, return only
                       incomplete tasks. If None, return all tasks regardless of status.
            pet_name:  If provided, return only tasks belonging to that pet (case-insensitive).
                       If None, return tasks across all pets.
        """
        results = self.owner.get_all_tasks()
        if pet_name is not None:
            results = [(pn, t) for pn, t in results if pn.lower() == pet_name.lower()]
        if completed is not None:
            results = [(pn, t) for pn, t in results if t.is_completed == completed]
        return results

    def get_conflicts(self) -> list[str]:
        """
        Scan all pending tasks and return warning strings for scheduling conflicts.

        Two levels are checked per (due_date, due_time) slot:
          - CONFLICT: same pet has 2+ tasks at the same time — owner can't do both.
          - WARNING:  different pets have tasks at the same time — owner is double-booked.

        Returns an empty list when no conflicts exist. Never raises.
        """
        from collections import defaultdict

        # Group pending tasks: {(due_date, due_time): [(pet_name, task), ...]}
        slots: dict[tuple, list[tuple[str, Task]]] = defaultdict(list)
        for pet_name, task in self.owner.get_all_tasks():
            if not task.is_completed:
                slots[(task.due_date, task.due_time)].append((pet_name, task))

        warnings = []
        for (due_date, due_time), entries in sorted(slots.items()):
            if len(entries) < 2:
                continue

            time_str = due_time.strftime("%H:%M")
            date_str = due_date.isoformat()

            # Check for same-pet conflicts
            pet_tasks: dict[str, list[str]] = defaultdict(list)
            for pet_name, task in entries:
                pet_tasks[pet_name].append(task.description)

            for pet_name, descriptions in pet_tasks.items():
                if len(descriptions) > 1:
                    joined = " & ".join(f'"{d}"' for d in descriptions)
                    warnings.append(
                        f"CONFLICT [{date_str} {time_str}] {pet_name} has overlapping tasks: {joined}"
                    )

            # Check for cross-pet double-booking
            pets_in_slot = list(pet_tasks.keys())
            if len(pets_in_slot) > 1:
                pet_list = " & ".join(pets_in_slot)
                warnings.append(
                    f"WARNING  [{date_str} {time_str}] Owner double-booked: tasks for {pet_list} at the same time"
                )

        return warnings

    def get_tasks_by_category(self, category: str) -> list[tuple[str, Task]]:
        """Filter all tasks by category (case-insensitive)."""
        return [
            (pet_name, task)
            for pet_name, task in self.owner.get_all_tasks()
            if task.category.lower() == category.lower()
        ]

    def add_task_to_pet(self, pet_name: str, task: Task) -> bool:
        """Add a task to a pet by name. Returns True if pet was found."""
        pet = self.pet_lookup.get(pet_name.lower())
        if pet:
            pet.add_task(task)
            return True
        return False

    def complete_task(self, pet_name: str, description: str) -> bool:
        """Mark a task complete by pet name and description. Returns True if found.

        For DAILY and WEEKLY tasks, the next occurrence is automatically scheduled
        so the task reappears in pending views without any manual re-entry.
        ONCE tasks are marked done permanently. Returns False if pet or task not found.
        """
        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                task = pet.task_index.get(description.lower())
                if task:
                    task.mark_complete()
                    next_task = task.next_occurrence()
                    if next_task:
                        # Remove old index entry so the new instance can claim the key.
                        # The completed task remains in pet.tasks for historical reference.
                        del pet.task_index[description.lower()]
                        pet.tasks.append(next_task)
                        pet.task_index[next_task.description.lower()] = next_task
                        self.owner._invalidate_cache()
                    return True
        return False

    def daily_summary(self) -> str:
        """
        Print a summary of all pending tasks grouped by pet.

        Example output:
        === Daily Summary for John Doe ===

        Bella (Dog) — 2 pending task(s):
          [08:00] Morning Walk (exercise, daily)
          [18:00] Evening Walk (exercise, daily)

        Max (Cat) — 1 pending task(s):
          [12:00] Vet Appointment (health, once)
        """
        lines = [f"=== Daily Summary for {self.owner.name} ==="]
        for pet in self.owner.pets:
            pending = [t for t in pet.tasks if not t.is_completed]
            lines.append(f"\n{pet.name} ({pet.species}) — {len(pending)} pending task(s):")
            if pending:
                for task in self.sort_by_time(pending):
                    lines.append(f"  [{task.due_time.strftime('%H:%M')}] {task.description} ({task.category}, {task.frequency.value})")
            else:
                lines.append("  All tasks complete!")
        return "\n".join(lines)
