import queue

class StatusLogger:
    def __init__(self):
        self.history = []
        self.max_history = 10
        self.queue = queue.Queue()

    def log(self, message):
        print(f"[STATUS] {message}")
        self.history.append(message)
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_recent(self):
        return self.history

# Global instance
logger = StatusLogger()
