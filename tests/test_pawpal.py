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
    scheduler.complete_task("Buddy", "Morning walk")
    pending = scheduler.get_pending_tasks()
    descriptions = [task.description for _, task in pending]
    assert "Morning walk" not in descriptions


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
