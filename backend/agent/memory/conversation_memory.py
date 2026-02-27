"""
Conversation Memory — persists chat history per session.
Supports in-memory (for testing) and JSON file backend.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class ConversationMemory:
    def __init__(self, session_id: str, backend: str = "file", memory_dir: str = "./data/memory"):
        self.session_id = session_id
        self.backend = backend
        self.memory_dir = Path(memory_dir)
        self._messages: List[Dict[str, Any]] = []

        if self.backend == "file":
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            self._load()

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def add_user(self, content: str) -> None:
        self._append("user", content)

    def add_assistant(self, content: str) -> None:
        self._append("assistant", content)

    def add_system(self, content: str) -> None:
        self._append("system", content)

    def get_messages(self) -> List[Dict[str, str]]:
        """Return messages in OpenAI API format (role + content only)."""
        return [{"role": m["role"], "content": m["content"]} for m in self._messages]

    def get_messages_with_metadata(self) -> List[Dict[str, Any]]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages = []
        if self.backend == "file":
            path = self._file_path()
            if path.exists():
                path.unlink()

    def count(self) -> int:
        return len(self._messages)

    # ------------------------------------------------------------------ #
    #  Internals                                                           #
    # ------------------------------------------------------------------ #

    def _append(self, role: str, content: str) -> None:
        self._messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })
        if self.backend == "file":
            self._save()

    def _file_path(self) -> Path:
        return self.memory_dir / f"{self.session_id}.json"

    def _save(self) -> None:
        with open(self._file_path(), "w", encoding="utf-8") as f:
            json.dump(self._messages, f, ensure_ascii=False, indent=2)

    def _load(self) -> None:
        path = self._file_path()
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                self._messages = json.load(f)


class MemoryManager:
    """Singleton registry — holds all active ConversationMemory instances."""

    _instances: Dict[str, ConversationMemory] = {}

    @classmethod
    def get(cls, session_id: str, backend: Optional[str] = None, memory_dir: Optional[str] = None) -> ConversationMemory:
        if session_id not in cls._instances:
            cls._instances[session_id] = ConversationMemory(
                session_id=session_id,
                backend=backend or os.getenv("MEMORY_BACKEND", "file"),
                memory_dir=memory_dir or os.getenv("MEMORY_DIR", "./data/memory"),
            )
        return cls._instances[session_id]

    @classmethod
    def delete(cls, session_id: str) -> bool:
        if session_id in cls._instances:
            cls._instances[session_id].clear()
            del cls._instances[session_id]
            return True
        return False
