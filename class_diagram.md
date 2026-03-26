# PawPal+ Class Diagram

## Classes

### Owner
- **name** (str): The owner's name.
- **pets** (list): A collection of Pet objects.
- `add_pet(pet_obj)`: Registers a new pet to the owner's profile.
- `get_all_tasks()`: Aggregates tasks from all pets for a master schedule view.

### Pet
- **name** (str): The pet's name.
- **species** (str): Breed or species (e.g., Dog, Cat).
- **age** (int): The pet's age.
- **health_notes** (list): A log of medical history or physical observations.
- `add_health_note(note)`: Appends a timestamped string to the health log.
- `get_summary()`: Returns a quick-glance string of the pet's vital info.

### Task
- **description** (str): The name of the activity (e.g., "Morning Feeding").
- **category** (str): Type of task (Feeding, Medication, Exercise, Appointment).
- **due_time** (str): The scheduled time for the task.
- **is_completed** (bool): Tracks whether the task has been performed.
- `mark_complete()`: Toggles the completion status to True.

### Schedule
- **date** (date): The calendar day this schedule represents.
- **tasks** (list): A list of Task objects.
- `get_pending()`: Returns a list of tasks that are not yet completed.

---

## Mermaid Class Diagram

```mermaid
classDiagram
    class Owner {
        +String name
        +List pets
        +add_pet(pet_obj)
        +get_all_tasks()
    }

    class Pet {
        +String name
        +String species
        +int age
        +List health_notes
        +add_health_note(note)
        +get_summary()
    }

    class Task {
        +String description
        +String category
        +String due_time
        +bool is_completed
        +mark_complete()
    }

    class Schedule {
        +Date date
        +List tasks
        +get_pending()
    }

    Owner "1" --> "0..*" Pet : owns
    Pet "1" --> "1" Schedule : has
    Schedule "1" --> "0..*" Task : contains
    Owner ..> Task : aggregates via get_all_tasks()
```
