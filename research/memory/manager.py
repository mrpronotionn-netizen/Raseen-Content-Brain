try:
    from .store import (
        remember,
        recall,
        search_memory,
        memory_exists
    )
except ImportError:
    from store import (
        remember,
        recall,
        search_memory,
        memory_exists
    )


class MemoryManager:

    def __init__(self):
        pass

    def add_memory(
        self,
        memory_type,
        title,
        content,
        source_url=None,
        status="new",
        decision=None,
        decision_reason=None
    ):
        """
        Add a new memory if the title does not already exist.
        """

        if memory_exists(title):
            return {
                "success": False,
                "reason": "duplicate",
                "message": "Memory already exists."
            }

        remember(
            memory_type=memory_type,
            title=title,
            content=content,
            source_url=source_url,
            status=status,
            decision=decision,
            decision_reason=decision_reason
        )

        return {
            "success": True,
            "reason": "created",
            "message": "Memory saved successfully."
        }

    def search(self, query, limit=10):
        """
        Search memories by title or content.
        """

        return search_memory(
            query=query,
            limit=limit
        )

    def recent(self, limit=10):
        """
        Return the most recent memories.
        """

        return recall(
            limit=limit
        )

    def exists(self, title):
        """
        Check whether a memory already exists.
        """

        return memory_exists(title)