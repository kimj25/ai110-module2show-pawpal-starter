from dataclasses import dataclass, field
from datetime import datetime, time
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

    def __post_init__(self):
        """Normalize category to lowercase and parse due_time from string if needed."""
        self.category = self.category.lower()
        if isinstance(self.due_time, str):
            hour, minute = map(int, self.due_time.split(":"))
            self.due_time = time(hour=hour, minute=minute)

    def mark_complete(self):
        """Mark this task as completed."""
        self.is_completed = True


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

    def get_pending_tasks(self) -> list[tuple[str, Task]]:
        """All incomplete tasks, sorted by due_time."""
        pending = [
            (pet_name, task)
            for pet_name, task in self.owner.get_all_tasks()
            if not task.is_completed
        ]
        return sorted(pending, key=lambda pair: pair[1].due_time)

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
        """Mark a task complete by pet name and description. Returns True if found."""
        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                task = pet.task_index.get(description.lower())
                if task:
                    task.mark_complete()
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
                for task in sorted(pending, key=lambda t: t.due_time):
                    lines.append(f"  [{task.due_time.strftime('%H:%M')}] {task.description} ({task.category}, {task.frequency})")
            else:
                lines.append("  All tasks complete!")
        return "\n".join(lines)
