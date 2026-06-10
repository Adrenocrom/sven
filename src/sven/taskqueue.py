# Simple serial TaskQueue implementation

class TaskQueue:
    """
    A very simple serial task queue. Tasks are stored in a list and executed one by one.
    The queue is intentionally *not* thread‑safe; it is meant for single‑thread usage only.
    """

    def __init__(self):
        self._tasks = []  # List of (func, args, kwargs)

    def add(self, func, *args, **kwargs):
        """Add a callable to the queue.

        Parameters:
            func: Callable – The function to execute.
            *args, **kwargs: Arguments that will be passed to the function when executed.
        """
        self._tasks.append((func, args, kwargs))

    def run(self):
        """Execute all queued tasks in the order they were added.

        Each task is popped from the front of the queue. Any exception raised by a
        task will be caught and printed; the queue will then continue with the next
        task.
        """
        while self._tasks:
            func, args, kwargs = self._tasks.pop(0)
            try:
                func(*args, **kwargs)
            except Exception as exc:
                print(f"Task {func.__name__} raised an exception: {exc}")

# Example usage
if __name__ == "__main__":
    import time

    def greet(name):
        print(f"Hello, {name}!")
        time.sleep(0.5)

    def fail_task():
        raise ValueError("Intentional failure")

    queue = TaskQueue()
    queue.add(greet, "Alice")
    queue.add(greet, "Bob")
    queue.add(fail_task)
    queue.add(greet, "Charlie")
    queue.run()

