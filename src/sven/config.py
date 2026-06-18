import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Options:
    """
    Encapsulates nested options (currently only temperature).
    """
    temperature: float = 0.0

    # ---------- JSON helpers ----------
    def to_dict(self) -> Dict[str, Any]:
        return {"temperature": self.temperature}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Options":
        return cls(temperature=data.get("temperature", 0.0))

    # ---------- Convenience for env override ----------
    @staticmethod
    def _override_from_env(opt: "Options") -> "Options":
        """
        Return a new Options instance overriding values that come from the
        corresponding environment variables.
        """
        temperature = opt.temperature
        if (env_val := os.getenv("SVEN_TEMPERATURE")) is not None:
            try:
                temperature = float(env_val)
            except ValueError:
                raise ValueError(
                    f"Invalid SVEN_TEMPERATURE value: {env_val!r}"
                )
        return Options(temperature=temperature)


@dataclass
class Config:
    """
    Main configuration container.  The class is intentionally mutable so
    that the getters/setters feel natural while still providing a clear API.
    """
    model: str = "gemma4:12b"
    system_prompt: str = "You are a Senior software developer called Sven."
    options: Options = field(default_factory=Options)
    keep_recent_count: int = 5
    max_messages: int= 20

    # ---------- Getters / Setters ----------
    @property
    def model(self) -> str:
        return self._model

    @model.setter
    def model(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("model must be a string")
        self._model = value

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("system_prompt must be a string")
        self._system_prompt = value

    @property
    def keep_recent_count(self) -> str:
        return self._keep_recent_count

    @keep_recent_count.setter
    def keep_recent_count(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("keep_recent_count must be a int")
        self._keep_recent_count = value

    @property
    def max_messages(self) -> str:
        return self._max_messages

    @max_messages.setter
    def max_messages(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("max_messages must be a int")
        self._max_messages = value

    # options is an Options instance – no custom property needed

    # ---------- JSON helpers ----------
    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "system_prompt": self.system_prompt,
            "options": self.options.to_dict(),
            "keep_recent_count": self.keep_recent_count,
            "max_messages": self.max_messages,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """
        Create a Config instance from a plain dictionary (e.g. the one returned by json.load()).
        """
        options_data = data.get("options", {})
        options_obj = Options.from_dict(options_data)

        return cls(
            model=data.get("model", "gemma4:12b"),
            system_prompt=data.get(
                "system_prompt",
                "You are a Senior software developer called Sven.",
            ),
            options=options_obj,
            keep_recent_count=data.get("keep_recent_count", 5),
            max_messages=data.get("max_messages", 20)
        )

    @classmethod
    def from_json(cls, path: Path) -> "Config":
        """
        Load configuration from a JSON file.
        If the file does not exist, a default instance is created and written to disk.
        """
        if not path.exists():
            cfg = cls()
            cfg.write_to_file(path)
            return cfg

        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)

        # Handle profile‑specific overrides if present
        profiles = data.get("profiles", {})
        profile_name = os.getenv("SVEN_PROFILE", "dev")
        if profile_name in profiles:
            data.update(profiles[profile_name])

        cfg = cls.from_dict(data)
        return cfg

    def write_to_file(self, path: Path) -> None:
        """Persist the configuration to disk."""
        with path.open("w", encoding="utf-8") as fp:
            json.dump(self.to_dict(), fp, indent=4)

    # ---------- Environment overrides ----------
    @staticmethod
    def _env_override(cfg: "Config") -> "Config":
        """
        Return a new Config instance where any recognised environment variable
        has overridden the corresponding field.
        """
        model = cfg.model
        if (v := os.getenv("SVEN_MODEL")):
            model = v

        system_prompt = cfg.system_prompt
        if (v := os.getenv("SVEN_SYSTEM_PROMPT")):
            system_prompt = v

        options = Options._override_from_env(cfg.options)

        return Config(
            model=model,
            system_prompt=system_prompt,
            options=options,
            keep_recent_count=5,
            max_messages=20
        )

    # ---------- Convenience API ----------
    @classmethod
    def load(cls, config_path: str | Path = "config.json") -> "Config":
        """
        Full load pipeline:
          1. Load defaults from file (or create a new one).
          2. Merge profile overrides.
          3. Apply environment variable overrides.
        """
        cfg = cls.from_json(Path(config_path))
        return cls._env_override(cfg)

    def to_json(self, path: Optional[Path] = None) -> str:
        """Return the JSON representation; optionally write it to a file."""
        json_str = json.dumps(self.to_dict(), indent=4)
        if path is not None:
            with path.open("w", encoding="utf-8") as fp:
                fp.write(json_str)
        return json_str
