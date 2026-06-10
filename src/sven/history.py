# src/history.py
"""
A very small, self‑contained history manager for chat prompts.

Features
--------
* Keeps the most recent *N* prompts (default 100).
* Stores them in a JSON file located next to this module (`prompt_history.json`)
  so that the data survives across runs.
* Provides a tiny API: `add_prompt`, `get_history`, and `clear`.

Usage Example
-------------
>>> from src.history import PromptHistory
>>> hist = PromptHistory()          # defaults to 100 items, JSON file in ./src/
>>> hist.add_prompt("Hello world!")
>>> print(hist.get_history())       # most recent prompt is last element
['Hello world!']
"""

import json
from pathlib import Path

__all__ = ["PromptHistory"]


class PromptHistory:
    """
    Persistently store the last *max_size* prompts.

    Parameters
    ----------
    filename : str | None, optional
        Where to store the history.  If ``None`` (default), a file named
        ``prompt_history.json`` will be created next to this module.
    max_size : int, optional
        Keep only the last *max_size* prompts.  Defaults to 100.

    Notes
    -----
    The JSON file contains a plain list of strings:

    .. code-block:: json

        [
            "First prompt",
            "Second prompt",
            ...
        ]

    The list is ordered from oldest to newest – i.e. the last element is the
    most recent prompt.
    """

    def __init__(self, filename: str | None = None, max_size: int = 100):
        self.max_size = max_size

        # Resolve file location --------------------------------------------------
        if filename is None:
            base_dir = Path(__file__).parent.resolve()
            self.filename = base_dir / "prompt_history.json"
        else:
            self.filename = Path(filename).expanduser().resolve()

        # Ensure the JSON file exists (create an empty list if missing)
        if not self.filename.exists():
            self._write([])

        # Load current history into memory --------------------------------------
        self.history: list[str] = self._read()

    # ---------------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------------

    def _read(self) -> list[str]:
        """Load the JSON file and return its contents as a Python list."""
        try:
            with self.filename.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    # Make sure every entry is string‑like
                    return [str(item) for item in data]
                raise ValueError("JSON file does not contain a list")
        except (json.JSONDecodeError, FileNotFoundError, ValueError):
            # Corrupted or missing – start from scratch
            return []

    def _write(self, data: list[str]) -> None:
        """Persist *data* to disk as pretty‑printed JSON."""
        # Create parent dir if needed
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        with self.filename.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ---------------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------------

    def add_prompt(self, prompt: str) -> None:
        """
        Add a new prompt to the history.

        Parameters
        ----------
        prompt : str
            The user’s input. Empty or whitespace‑only strings are ignored.
        """
        cleaned = prompt.strip()
        if not cleaned:
            return

        # Append and trim to max_size
        self.history.append(cleaned)
        if len(self.history) > self.max_size:
            # keep only the last `max_size` items
            self.history = self.history[-self.max_size:]

        # Persist immediately – no need for a separate flush step
        self._write(self.history)

    def get_history(self, limit: int | None = None) -> list[str]:
        """
        Retrieve the current history.

        Parameters
        ----------
        limit : int | None
            If provided, return only the last *limit* prompts.
            Default is all stored items (most recent last).

        Returns
        -------
        List[str]
            The requested portion of the history, oldest → newest.
        """
        if limit is not None:
            return self.history[-limit:]
        return list(self.history)

    def clear(self) -> None:
        """Erase every stored prompt."""
        self.history.clear()
        self._write([])

    # ---------------------------------------------------------------------------

    # Convenience for interactive use
    # -----------------------------------------------
    if __name__ == "__main__":
        import argparse, sys

        parser = argparse.ArgumentParser(
            description="Simple demo of PromptHistory"
        )
        sub = parser.add_subparsers(dest="cmd", required=True)

        addp = sub.add_parser("add")
        addp.add_argument("prompt", help="Prompt to store")

        getp = sub.add_parser("get")
        getp.add_argument("-n", "--last", type=int, default=None,
                          help="Show only the last N prompts (default: all)")

        clearp = sub.add_parser("clear")

        args = parser.parse_args()

        hist = PromptHistory()

        if args.cmd == "add":
            hist.add_prompt(args.prompt)
            print(f"Added prompt. Total stored: {len(hist.get_history())}")
        elif args.cmd == "get":
            for i, p in enumerate(hist.get_history(limit=args.last), 1):
                print(f"{i}. {p}")
        else:  # clear
            hist.clear()
            print("All history cleared.")

