# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The design follows a hierarchical composition model, separating pet identity from daily logistics to keep the system modular and testable.

Has four classes: Owner, Pet, Schedule, Task.
Owner 
- Global Management, Root container for all data.
- Holds Pets list, can aggregate all tasks
Pets  
- identifies pet, and stores pets data
- Holds pet's condition, links Schedule
Schedule 
- organizes task by date
- contain tasks, and holds pending task 
Task
- lists activities that can be completed
- tracks due_time, category, and is_completed status


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

- Was missing relationship: pet and schedule. Diagram had pet "1" --> "1" Schedule, meaning every Pet must have a Schedule. 

- Logic Bottlenecks: Owner.get_all_tasks() has no path to tasks. The method needed to traverse Owner → pets → schedule → tasks. But if any pet's schedule is None, this will throw an AttributeError.  Changed to check if the pet has a schedule, guarding against None.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
- Frequency, Time, Completion are the constraints currently considered
- Time is the constraint that matters most. Since every method is organized around due_time and due_date. Tasks are organized based on the time.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

- Scheduler maintains two separate ways to access same data, a task: a List (pet.tasks) and a Dictionary/Map (pet.task_index)
- every add_task and every complete_task both must be in sync. 
- It is reasonable since each way can be accessed differently since each preserves different sort description (insertion order vs lookup by description)


---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

- I used Claude code for design brainstorming, debugging, refractoring, making tests, fixing bugs, and for UI implementation
- Asking for suggestions to improve the app was helpful. I also liked asking to cover edge cases for tests. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

- I tried to see if we can make the algorithm "simpler" for the scheduler section. However, the readability was poor so I kept as is. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?



**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

- I was surprised and satisfied with the UI portion. Looks clean, and easy to use. Also I liked how it shows entire schedule.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

- I want to add choosing dates on the calendar feature.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

- That it is important to design and build step by step for better organization and minimize redundancy. This way, AI also understands clearly what I am trying to build. 
