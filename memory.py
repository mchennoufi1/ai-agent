class ConversationMemory:
    def __init__(self, max_history: int = 5):
        self.history = []
        self.max_history = max_history

    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-(self.max_history * 2):]

    def get_context(self) -> str:
        if not self.history:
            return ""
        return "\n".join(
            f"{m['role'].upper()}: {m['content']}"
            for m in self.history[-self.max_history:]
        )

    def clear(self):
        self.history = []
