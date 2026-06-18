#!/usr/bin/env python3
"""
token_counter.py – A tiny token‑usage tracker that persists its state.
"""

import json
from pathlib import Path
from typing import Dict, Optional


class TokenCounter:
    """
    Tracks the number of tokens used.  The counter can be serialised to a JSON file
    and reloaded later.

    Attributes
    ----------
    total : int
        Total number of tokens consumed.
    per_user : dict[str, int]
        Optional mapping from user identifiers to token counts.
    """

    def __init__(self, initial_total: int = 0,
                 per_user: Optional[Dict[str, int]] = None) -> None:
        self.total = int(initial_total)
        self.per_user = dict(per_user or {})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(self, count: int = 1, user_id: Optional[str] = None) -> None:
        """
        Increment the counter.

        Parameters
        ----------
        count : int
            Number of tokens to add (default 1).
        user_id : str | None
            If supplied, also increment that user's individual counter.
        """
        if count < 0:
            raise ValueError("Token count must be non‑negative")
        self.total += count
        if user_id is not None:
            self.per_user[user_id] = self.per_user.get(user_id, 0) + count

    def get_total(self) -> int:
        """Return the total number of tokens consumed."""
        return self.total

    def get_user_total(self, user_id: str) -> int:
        """Return the token count for a specific user (or 0 if unknown)."""
        return self.per_user.get(user_id, 0)

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict:
        """Convert the counter state into a plain dictionary."""
        return {"total": self.total, "per_user": self.per_user}

    @classmethod
    def from_dict(cls, data: Dict) -> "TokenCounter":
        """Create a TokenCounter instance from a dictionary."""
        return cls(initial_total=data.get("total", 0),
                   per_user=data.get("per_user"))

    def save(self, filepath: str | Path) -> None:
        """
        Persist the counter to disk as JSON.

        Parameters
        ----------
        filepath : str or pathlib.Path
            Destination file.  The directory will be created if it does not exist.
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str | Path) -> "TokenCounter":
        """
        Load a counter from disk.

        Parameters
        ----------
        filepath : str or pathlib.Path
            Source file.  If the file does not exist, an empty counter is returned.
        """
        path = Path(filepath)
        if not path.is_file():
            # Return an empty counter instead of raising – this makes it safe to call
            # load() before any data has been written.
            return cls()
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


# ----------------------------------------------------------------------
# Example usage (uncomment to run)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    counter_file = "token_counter.json"

    # Load existing state or start fresh
    counter = TokenCounter.load(counter_file)

    # Simulate some token consumption
    counter.add(120)          # 120 tokens for the system
    counter.add(30, user_id="alice")
    counter.add(45, user_id="bob")

    print(f"Total tokens: {counter.get_total()}")
    print(f"Alice's tokens: {counter.get_user_total('alice')}")
    print(f"Bob's tokens: {counter.get_user_total('bob')}")

    # Persist the updated state
    counter.save(counter_file)
