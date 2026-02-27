"""
Kimi Agent — orchestrates the LLM, memory, web search, and file tools.
Uses Kimi's OpenAI-compatible API endpoint.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI

from agent.memory.conversation_memory import MemoryManager
from agent.tools.web_search import web_search, format_search_results
from agent.tools.file_reader import extract_text, summarize_prompt


SYSTEM_PROMPT = """You are Kimi, a smart and helpful AI assistant.
You have access to:
- Web search: When users ask about current events or need up-to-date information, you will receive search results to base your answer on.
- File analysis: You can read and analyze uploaded documents (PDF, DOCX, TXT).
- Conversation memory: You remember previous messages in this session.

Always be concise, accurate, and helpful. When using search results, cite the source URLs when relevant.
"""


class KimiAgent:
    def __init__(self):
        api_key = os.getenv("KIMI_API_KEY")
        base_url = os.getenv("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
        self.model = os.getenv("KIMI_MODEL", "moonshot-v1-8k")

        if not api_key:
            raise ValueError("KIMI_API_KEY is not set in environment variables.")

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    # ------------------------------------------------------------------ #
    #  Chat                                                                #
    # ------------------------------------------------------------------ #

    def chat(
        self,
        session_id: str,
        user_message: str,
        use_search: bool = True,
    ) -> Tuple[str, List[str]]:
        """
        Send a message and get a reply.

        Returns:
            (reply_text, list_of_source_urls)
        """
        memory = MemoryManager.get(session_id)
        sources: List[str] = []

        # Initialise system prompt on first message
        if memory.count() == 0:
            memory.add_system(SYSTEM_PROMPT)

        # Optionally inject web search context
        augmented_message = user_message
        if use_search and self._should_search(user_message):
            results = web_search(user_message)
            sources = [r["url"] for r in results if r["url"]]
            context = format_search_results(results)
            augmented_message = (
                f"{user_message}\n\n"
                f"[Web search results for your reference:]\n{context}"
            )

        memory.add_user(augmented_message)

        # Call Kimi API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=memory.get_messages(),
            temperature=0.7,
        )

        reply = response.choices[0].message.content or ""
        memory.add_assistant(reply)

        return reply, sources

    # ------------------------------------------------------------------ #
    #  File upload & analysis                                              #
    # ------------------------------------------------------------------ #

    def analyze_file(
        self,
        session_id: str,
        file_path: str,
        file_name: str,
    ) -> Tuple[str, str]:
        """
        Extract text from a file and ask the agent to summarise it.

        Returns:
            (summary, file_type)
        """
        text, file_type = extract_text(file_path)
        prompt = summarize_prompt(text, file_name)

        memory = MemoryManager.get(session_id)
        if memory.count() == 0:
            memory.add_system(SYSTEM_PROMPT)

        memory.add_user(prompt)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=memory.get_messages(),
            temperature=0.3,
        )

        summary = response.choices[0].message.content or ""
        memory.add_assistant(summary)
        return summary, file_type

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _should_search(self, message: str) -> bool:
        """Simple heuristic — search for questions about current events."""
        search_triggers = [
            "what is", "who is", "latest", "recent", "news",
            "current", "today", "price", "weather", "?",
        ]
        lower = message.lower()
        return any(trigger in lower for trigger in search_triggers)
