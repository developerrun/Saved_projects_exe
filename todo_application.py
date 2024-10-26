
import json
import os
from tabulate import tabulate

class Application:
    """ A simple to-do app for adding, deleting, viewing, and completing tasks """

    def __init__(self, filename="filename.json"):
        """Initializing the filename and self.tasks"""
        self.filename = filename
        self.tasks = self.load_tasks()

    def add_task(self, task_description):
        """ Function for adding tasks. """
        
        if not task_description.strip():  # Check for empty messages
            print("Task description cannot be empty.")
            return
        
        task = {"Description": task_description, "completed": False}
        self.tasks.append(task)
        self.save_tasks()  # Saving tasks after adding
        print(f"Task added: {task}")

    def view_task(self):
        """ Function for viewing tasks. """
        
        if not isinstance(self.tasks, list):
            print("Error while loading tasks.")
            return

        if not self.tasks:
            print("No tasks found.")
            return

        table = []
        for i, task in enumerate(self.tasks):
            tsk_num = i + 1
            status = "✔" if task["completed"] else "✖"
            table.append([tsk_num, task["Description"], status])

        print(tabulate(table, headers=["Task Number", "Task", "Status"], tablefmt="pretty"))

    def delete_task(self, task):
        """ Function for the deletion of a task. """
        
        if not isinstance(task, int):
            print("Task number must be an integer.")
            return
        
        if 1 <= task <= len(self.tasks):
            remove_task = self.tasks.pop(task - 1)
            self.save_tasks()  # Saving tasks after deletion
            print(f"Task deleted: {remove_task['Description']}")
        else:
            print("Invalid task number.")

    def save_tasks(self):
        """ Function for saving tasks """
        try:
            with open(self.filename, "w") as file:
                json.dump(self.tasks, file)  # Adds tasks into the file, using dump function.
        except IOError:
            print("Failed to save tasks to file.")

    def mark_complete(self, task_number):
        if 1 <= task_number <= len(self.tasks):
            
            if not self.tasks[task_number - 1]["completed"]:
                self.tasks[task_number - 1]["completed"] = True
                self.save_tasks()
                print(f"Task marked as completed: {self.tasks[task_number - 1]['Description']}")
            else:
                print(f"Task already completed: {self.tasks[task_number - 1]['Description']}")
        else:
            print("Invalid task number.")

    def load_tasks(self):
        """Load tasks from a JSON file and return them as a list."""
        
        if os.path.exists(self.filename):  # Check if filepath exists
            
            try:  # Try except, used for handling errors during the deserialization process.
                with open(self.filename, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print("Error during the deserialization process")
                return []  # Returns an empty list, in case errors occur in deserialization process

        return []


# Clear the contents of filename.json by writing an empty list to it
with open("filename.json", "w") as file:
    json.dump([], file)

app = Application() 

def main():
    while True:
        print("\nTo-Do List Application")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Delete Task")
        print("4. Mark Task as Completed")
        print("5. Exit")
        user_choice = input("Enter your choice: ")

        match user_choice:
            case "1":
                task_description = input("Enter task description: ")
                app.add_task(task_description)

            case "2":
                app.view_task()

            case "3":
                try:
                    task_number = int(input("Enter task number to delete: "))
                    app.delete_task(task_number)
                except ValueError:
                    print("Invalid input. Enter a numerical input")

            case "4":
                try:
                    task_num = int(input("Enter the task to mark as complete: "))
                    app.mark_complete(task_num)
                except ValueError:
                    print("Invalid input. Enter a numerical input")

            case "5":
                print("Exiting the application.")
                break

            case _:
                print("Invalid option. Try again.")

if __name__ == "__main__":
    main()
