import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# --- Task ---

def test_task_defaults_to_incomplete():
    task = Task(description="Walk", due_time="08:00", category="exercise", frequency="daily")
    assert task.is_completed is False


def test_task_mark_complete():
    task = Task(description="Walk", due_time="08:00", category="exercise", frequency="daily")
    task.mark_complete()
    assert task.is_completed is True


# --- Pet ---

def test_pet_add_task():
    pet = Pet(name="Buddy", species="Dog", age=3)
    task = Task(description="Breakfast", due_time="08:00", category="feeding", frequency="daily")
    pet.add_task(task)
    assert len(pet.tasks) == 1
    assert pet.tasks[0].description == "Breakfast"


def test_pet_add_health_note_timestamped():
    pet = Pet(name="Luna", species="Cat", age=2)
    pet.add_health_note("Sneezing observed")
    assert len(pet.health_notes) == 1
    assert "Sneezing observed" in pet.health_notes[0]
    assert pet.health_notes[0].startswith("[")


def test_pet_get_summary_counts_pending():
    pet = Pet(name="Mochi", species="Dog", age=1)
    pet.add_task(Task(description="Walk", due_time="07:00", category="exercise", frequency="daily"))
    pet.add_task(Task(description="Feeding", due_time="08:00", category="feeding", frequency="daily"))
    pet.tasks[0].mark_complete()
    summary = pet.get_summary()
    assert "Pending tasks: 1" in summary
    assert "Mochi" in summary


# --- Owner ---

def test_owner_add_pet():
    owner = Owner(name="Alex")
    pet = Pet(name="Buddy", species="Dog", age=3)
    owner.add_pet(pet)
    assert len(owner.pets) == 1


def test_owner_get_all_tasks():
    owner = Owner(name="Alex")
    dog = Pet(name="Buddy", species="Dog", age=3)
    cat = Pet(name="Luna", species="Cat", age=5)
    dog.add_task(Task(description="Walk", due_time="07:00", category="exercise", frequency="daily"))
    cat.add_task(Task(description="Medication", due_time="09:30", category="health", frequency="daily"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    all_tasks = owner.get_all_tasks()
    assert len(all_tasks) == 2
    pet_names = [name for name, _ in all_tasks]
    assert "Buddy" in pet_names
    assert "Luna" in pet_names


# --- Scheduler ---

@pytest.fixture
def scheduler():
    owner = Owner(name="Jordan")
    dog = Pet(name="Buddy", species="Dog", age=3)
    cat = Pet(name="Luna", species="Cat", age=5)
    dog.add_task(Task(description="Morning walk", due_time="07:00", category="exercise", frequency="daily"))
    dog.add_task(Task(description="Breakfast", due_time="08:00", category="feeding", frequency="daily"))
    cat.add_task(Task(description="Medication", due_time="09:30", category="health", frequency="daily"))
    cat.add_task(Task(description="Evening feeding", due_time="18:00", category="feeding", frequency="daily"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    return Scheduler(owner)


def test_get_pending_tasks_sorted_by_time(scheduler):
    pending = scheduler.get_pending_tasks()
    times = [task.due_time for _, task in pending]
    assert times == sorted(times)


def test_get_pending_tasks_excludes_completed(scheduler):
    # DAILY task: completing it schedules a new occurrence with the same description.
    # The completed instance should not appear in pending; the new occurrence will.
    scheduler.complete_task("Buddy", "Morning walk")
    buddy = scheduler.owner.pets[0]
    completed = [t for t in buddy.tasks if t.is_completed and t.description == "Morning walk"]
    pending_completed = [t for t in buddy.tasks if not t.is_completed and t.description == "Morning walk"]
    assert len(completed) == 1       # original is marked done
    assert len(pending_completed) == 1  # next occurrence is scheduled


def test_get_tasks_by_category(scheduler):
    feeding_tasks = scheduler.get_tasks_by_category("feeding")
    assert len(feeding_tasks) == 2
    assert all(task.category.lower() == "feeding" for _, task in feeding_tasks)


def test_get_tasks_by_category_case_insensitive(scheduler):
    result = scheduler.get_tasks_by_category("FEEDING")
    assert len(result) == 2


def test_add_task_to_pet_found(scheduler):
    new_task = Task(description="Grooming", due_time="11:00", category="hygiene", frequency="weekly")
    result = scheduler.add_task_to_pet("Buddy", new_task)
    assert result is True
    descriptions = [t.description for t in scheduler.owner.pets[0].tasks]
    assert "Grooming" in descriptions


def test_add_task_to_pet_not_found(scheduler):
    new_task = Task(description="Grooming", due_time="11:00", category="hygiene", frequency="weekly")
    result = scheduler.add_task_to_pet("Unknown", new_task)
    assert result is False


def test_complete_task_found(scheduler):
    result = scheduler.complete_task("Buddy", "Morning walk")
    assert result is True
    task = scheduler.owner.pets[0].tasks[0]
    assert task.is_completed is True


def test_complete_task_not_found(scheduler):
    result = scheduler.complete_task("Buddy", "Nonexistent task")
    assert result is False


def test_complete_task_case_insensitive(scheduler):
    result = scheduler.complete_task("buddy", "morning walk")
    assert result is True


def test_daily_summary_contains_owner_name(scheduler):
    summary = scheduler.daily_summary()
    assert "Jordan" in summary


def test_daily_summary_shows_all_tasks_complete(scheduler):
    for pet in scheduler.owner.pets:
        for task in pet.tasks:
            task.mark_complete()
    summary = scheduler.daily_summary()
    assert "All tasks complete!" in summary


# --- Edge Cases: Sorting ---

def test_sort_by_time_ties_returns_both(scheduler):
    """Tasks with identical due_time should both appear, order is unspecified."""
    from datetime import time
    pet = Pet(name="Rex", species="Dog", age=2)
    t1 = Task(description="Feed AM", due_time="08:00", category="feeding", frequency="daily")
    t2 = Task(description="Meds AM", due_time="08:00", category="health", frequency="daily")
    pet.add_task(t1)
    pet.add_task(t2)
    result = scheduler.sort_by_time(pet.tasks)
    assert len(result) == 2
    assert result[0].due_time == result[1].due_time == time(8, 0)


def test_sort_by_time_midnight_sorts_first():
    """Midnight (00:00) should sort before all other times."""
    from datetime import time
    t_midnight = Task(description="Midnight med", due_time="00:00", category="health", frequency="daily")
    t_morning = Task(description="Morning walk", due_time="08:00", category="exercise", frequency="daily")
    t_night = Task(description="Night walk", due_time="23:00", category="exercise", frequency="daily")
    owner = Owner(name="Sam")
    scheduler_local = Scheduler(owner)
    result = scheduler_local.sort_by_time([t_morning, t_night, t_midnight])
    assert result[0].due_time == time(0, 0)
    assert result[-1].due_time == time(23, 0)


def test_sort_by_time_empty_list():
    owner = Owner(name="Sam")
    scheduler_local = Scheduler(owner)
    assert scheduler_local.sort_by_time([]) == []


# --- Edge Cases: Recurring Tasks ---

def test_next_occurrence_daily_advances_one_day():
    from datetime import date
    task = Task(description="Walk", due_time="08:00", category="exercise", frequency="daily",
                due_date="2026-03-25")
    nxt = task.next_occurrence()
    assert nxt is not None
    assert nxt.due_date == date(2026, 3, 26)
    assert nxt.is_completed is False


def test_next_occurrence_weekly_advances_seven_days():
    from datetime import date
    task = Task(description="Bath", due_time="10:00", category="hygiene", frequency="weekly",
                due_date="2026-01-28")
    nxt = task.next_occurrence()
    assert nxt is not None
    assert nxt.due_date == date(2026, 2, 4)


def test_next_occurrence_weekly_across_year_boundary():
    from datetime import date
    task = Task(description="Checkup", due_time="09:00", category="health", frequency="weekly",
                due_date="2025-12-30")
    nxt = task.next_occurrence()
    assert nxt.due_date == date(2026, 1, 6)


def test_next_occurrence_once_returns_none():
    task = Task(description="Vet visit", due_time="14:00", category="health", frequency="once")
    assert task.next_occurrence() is None


def test_complete_daily_task_schedules_next_occurrence(scheduler):
    """Completing a DAILY task should add a new pending task for the next day."""
    scheduler.complete_task("Buddy", "Morning walk")
    pending_descriptions = [t.description for _, t in scheduler.get_pending_tasks()]
    assert "Morning walk" in pending_descriptions


def test_complete_daily_task_twice_schedules_two_occurrences(scheduler):
    """Completing a recurring task twice should produce two future occurrences."""
    scheduler.complete_task("Buddy", "Morning walk")
    scheduler.complete_task("Buddy", "Morning walk")
    completed = [t for t in scheduler.owner.pets[0].tasks if t.is_completed and t.description == "Morning walk"]
    assert len(completed) == 2


def test_complete_once_task_does_not_recur():
    owner = Owner(name="Pat")
    pet = Pet(name="Pip", species="Cat", age=1)
    task = Task(description="Vet visit", due_time="14:00", category="health", frequency="once")
    pet.add_task(task)
    owner.add_pet(pet)
    s = Scheduler(owner)
    s.complete_task("Pip", "Vet visit")
    pending = [t for _, t in s.get_pending_tasks()]
    assert not any(t.description == "Vet visit" for t in pending)


# --- Edge Cases: Duplicate Detection ---

def test_add_duplicate_task_raises():
    pet = Pet(name="Rex", species="Dog", age=2)
    pet.add_task(Task(description="Walk", due_time="08:00", category="exercise", frequency="daily"))
    with pytest.raises(ValueError):
        pet.add_task(Task(description="Walk", due_time="09:00", category="exercise", frequency="once"))


def test_add_duplicate_task_case_insensitive_raises():
    pet = Pet(name="Rex", species="Dog", age=2)
    pet.add_task(Task(description="Morning Walk", due_time="08:00", category="exercise", frequency="daily"))
    with pytest.raises(ValueError):
        pet.add_task(Task(description="morning walk", due_time="09:00", category="exercise", frequency="once"))


# --- Edge Cases: Conflict Detection ---

def test_get_conflicts_same_pet_same_time():
    owner = Owner(name="Jo")
    pet = Pet(name="Rex", species="Dog", age=2)
    pet.add_task(Task(description="Walk", due_time="08:00", category="exercise", frequency="daily", due_date="2026-03-25"))
    pet.add_task(Task(description="Meds", due_time="08:00", category="health", frequency="daily", due_date="2026-03-25"))
    owner.add_pet(pet)
    conflicts = Scheduler(owner).get_conflicts()
    assert any("CONFLICT" in c and "Rex" in c for c in conflicts)


def test_get_conflicts_different_pets_same_time():
    owner = Owner(name="Jo")
    dog = Pet(name="Rex", species="Dog", age=2)
    cat = Pet(name="Miso", species="Cat", age=3)
    dog.add_task(Task(description="Walk", due_time="08:00", category="exercise", frequency="daily", due_date="2026-03-25"))
    cat.add_task(Task(description="Meds", due_time="08:00", category="health", frequency="daily", due_date="2026-03-25"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    conflicts = Scheduler(owner).get_conflicts()
    assert any("WARNING" in c for c in conflicts)


def test_get_conflicts_same_time_different_date_no_conflict():
    owner = Owner(name="Jo")
    pet = Pet(name="Rex", species="Dog", age=2)
    pet.add_task(Task(description="Walk", due_time="08:00", category="exercise", frequency="daily", due_date="2026-03-25"))
    pet.add_task(Task(description="Meds", due_time="08:00", category="health", frequency="daily", due_date="2026-03-26"))
    owner.add_pet(pet)
    conflicts = Scheduler(owner).get_conflicts()
    assert conflicts == []


def test_get_conflicts_completed_task_excluded():
    owner = Owner(name="Jo")
    pet = Pet(name="Rex", species="Dog", age=2)
    t1 = Task(description="Walk", due_time="08:00", category="exercise", frequency="daily", due_date="2026-03-25")
    t2 = Task(description="Meds", due_time="08:00", category="health", frequency="daily", due_date="2026-03-25")
    t1.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)
    owner.add_pet(pet)
    conflicts = Scheduler(owner).get_conflicts()
    assert conflicts == []


def test_get_conflicts_both_conflict_and_warning():
    """Slot with same-pet conflict AND cross-pet warning should produce both messages."""
    owner = Owner(name="Jo")
    dog = Pet(name="Rex", species="Dog", age=2)
    cat = Pet(name="Miso", species="Cat", age=3)
    dog.add_task(Task(description="Walk", due_time="08:00", category="exercise", frequency="daily", due_date="2026-03-25"))
    dog.add_task(Task(description="Meds", due_time="08:00", category="health", frequency="daily", due_date="2026-03-25"))
    cat.add_task(Task(description="Feeding", due_time="08:00", category="feeding", frequency="daily", due_date="2026-03-25"))
    owner.add_pet(dog)
    owner.add_pet(cat)
    conflicts = Scheduler(owner).get_conflicts()
    assert any("CONFLICT" in c for c in conflicts)
    assert any("WARNING" in c for c in conflicts)


def test_get_conflicts_no_conflicts_returns_empty(scheduler):
    assert scheduler.get_conflicts() == []


# --- Edge Cases: Cache Invalidation ---

def test_cache_reflects_task_added_via_scheduler(scheduler):
    """add_task_to_pet should be visible in get_all_tasks (cache must not be stale)."""
    _ = scheduler.owner.get_all_tasks()  # populate cache
    new_task = Task(description="Grooming", due_time="11:00", category="hygiene", frequency="weekly")
    scheduler.add_task_to_pet("Buddy", new_task)
    all_tasks = scheduler.owner.get_all_tasks()
    descriptions = [t.description for _, t in all_tasks]
    assert "Grooming" in descriptions


def test_cache_reflects_once_task_completed():
    """After completing a ONCE task, get_all_tasks cache should return updated state."""
    owner = Owner(name="Pat")
    pet = Pet(name="Pip", species="Cat", age=1)
    task = Task(description="Vet visit", due_time="14:00", category="health", frequency="once")
    pet.add_task(task)
    owner.add_pet(pet)
    s = Scheduler(owner)
    _ = owner.get_all_tasks()  # populate cache
    s.complete_task("Pip", "Vet visit")
    pending = [t for _, t in s.get_pending_tasks()]
    assert not any(t.description == "Vet visit" for t in pending)


# --- Edge Cases: Empty / No-op Scenarios ---

def test_get_pending_tasks_empty_owner():
    owner = Owner(name="Nobody")
    s = Scheduler(owner)
    assert s.get_pending_tasks() == []


def test_daily_summary_no_pets():
    owner = Owner(name="Nobody")
    summary = Scheduler(owner).daily_summary()
    assert "Nobody" in summary


def test_filter_tasks_nonexistent_pet(scheduler):
    assert scheduler.filter_tasks(pet_name="Ghost") == []


def test_filter_tasks_none_params_returns_all(scheduler):
    all_tasks = scheduler.filter_tasks()
    assert len(all_tasks) == len(scheduler.owner.get_all_tasks())
