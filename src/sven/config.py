import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dataclasses import dataclass, field

@dataclass(frozen=True)
class Options:
    temperature: float = 0.0
    num_ctx: int = 2048
    repeat_penalty: float = 1.1

    # ---------- JSON helpers ----------
    def to_dict(self) -> Dict[str, Any]:
        return {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx,
                "repeat_penalty": self.repeat_penalty, 
                }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Options":
        return cls(
                temperature=data.get("temperature", 0.0), 
                num_ctx=data.get("num_ctx", 2048),
                repeat_penalty=data.get("repeat_penalty", 1.1),
                )

    # ---------- Convenience for env override ----------
    @staticmethod
    def _override_from_env(opt: "Options") -> "Options":
        if (v := os.getenv("SVEN_TEMPERATURE")) is not None:
            try:
                temperature = float(v)
            except ValueError as exc:
                raise ValueError(f"Invalid SVEN_TEMPERATURE value: {v!r}") from exc
            return Options(temperature=temperature)

        return opt

@dataclass
class Config:
    """
    Mutable configuration container.
    The public attributes are protected by property setters that enforce
    basic type checks, while the dataclass keeps the nice syntax for defaults.
    """

    _data_dir: str = field(init=False, default="C:/Users/henrik/AppData/Roaming/Sven/.local/share")
    _config_dir: str = field(init=False, default="C:/Users/henrik/AppData/Roaming/Sven/.config")
    _token_stats_file: str = field(init=False, default="tokens.json")
    _model: str = field(init=False, default="gemma4:12b")
    _host: str = field(init=False, default="localhost")
    _keep_alive: str = field(init=False, default="10m")
    _system_prompt: str = field(
        init=False,
        default="You are a Senior software developer called Sven.",
    )
    options: Options = field(default_factory=Options)
    keep_recent_count: int = 5
    max_messages: int = 20

    @property
    def data_dir(self) -> str:
        return os.path.expanduser(self._data_dir)

    @data_dir.setter
    def data_dir(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("data_dir must be a string")
        self._data_dir = value

    @property
    def config_dir(self) -> str:
        return os.path.expanduser(self._config_dir)

    @config_dir.setter
    def config_dir(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("config_dir must be a string")
        self._config_dir = value

    @property
    def token_stats_file(self) -> str:
        return self._token_stats_file

    @token_stats_file.setter
    def token_stats_file(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("token_stats_file must be a string")
        self._token_stats_file = value

    @property
    def model(self) -> str:
        return self._model

    @model.setter
    def model(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("model must be a string")
        self._model = value

    @property
    def host(self) -> str:
        return self._host

    @host.setter
    def host(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("host must be a string")
        self._host = value

    @property
    def keep_alive(self) -> str:
        return self._keep_alive

    @keep_alive.setter
    def keep_alive(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("keep_alive must be a string")
        self._keep_alive = value

    # ---- Property for *system_prompt* -----------------------------------------
    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("system_prompt must be a string")
        self._system_prompt = value

    # ---- No properties needed for keep_recent_count / max_messages; type checks --
    # (the dataclass already enforces the annotations; you can add __post_init__ for stricter validation)

    # --------------------------------------------------------------------------- #
    # JSON helpers
    # --------------------------------------------------------------------------- #

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_dir": self.data_dir,
            "config_dir": self.config_dir,
            "token_stats_file": self.token_stats_file,
            "model": self.model,
            "host": self.host,
            "keep_alive": self.keep_alive,
            "system_prompt": self.system_prompt,
            "options": self.options.to_dict(),
            "keep_recent_count": self.keep_recent_count,
            "max_messages": self.max_messages,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        options_data = data.get("options", {})
        opts = Options.from_dict(options_data)

        # The constructor expects the *private* names because we used init=False above.
        cfg = cls(
            keep_recent_count=data.get("keep_recent_count", 5),
            max_messages=data.get("max_messages", 20),
            options=opts,
        )
        cfg.data_dir = data.get("data_dir", "C:/Users/henrik/AppData/Roaming/Sven/.local/share")
        cfg.config_dir = data.get("config_dir", "C:/Users/henrik/AppData/Roaming/Sven/.config")
        cfg.token_stats_file = data.get("token_stats_file", "tokens.json")
        cfg.model = data.get("model", "gemma4:12b")
        cfg.host = data.get("host", "localhost")
        cfg.keep_alive = data.get("keep_alive", "30m")
        cfg.system_prompt = data.get("system_prompt", "")
        return cfg


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

        return cls.from_dict(data)

    def write_to_file(self, path: Path) -> None:
        """Persist the configuration to disk."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fp:
            json.dump(self.to_dict(), fp, indent=4)

    @staticmethod
    def _env_override(cfg: "Config") -> "Config":
        """
        Return a new Config instance where any recognised environment variable
        has overridden the corresponding field.
        """
        model = cfg.model
        if (v := os.getenv("SVEN_MODEL")):
            model = v

        host = cfg.host
        if (v := os.getenv("SVEN_HOST")):
            host = v

        system_prompt = cfg.system_prompt
        if (v := os.getenv("SVEN_SYSTEM_PROMPT")):
            system_prompt = v

        data_dir = cfg._data_dir
        if (v := os.getenv("SVEN_DATA_DIR")):
            data_dir = v

        options = Options._override_from_env(cfg.options)

        return Config(
            _model=model,
            _host=host,
            _keep_alive=cfg.keep_alive,
            _system_prompt=system_prompt,
            _data_dir=data_dir,
            options=options,
            keep_recent_count=cfg.keep_recent_count,
            max_messages=cfg.max_messages,
        )

    @classmethod
    def load(cls, config_path: str | Path = None) -> "Config":
        """
        Full load pipeline:
          1. Load defaults from file (or create a new one).
          2. Merge profile overrides.
          3. Apply environment variable overrides.
        """
        if config_path is None:
            config_path = Path(os.path.expanduser("C:/Users/henrik/AppData/Roaming/Sven/.config")) / "sven.json"
        cfg = cls.from_json(Path(config_path))
        return cfg

    def to_json(self, path: Optional[Path] = None) -> str:
        """Return the JSON representation; optionally write it to a file."""
        json_str = json.dumps(self.to_dict(), indent=4)
        if path is not None:
            with path.open("w", encoding="utf-8") as fp:
                fp.write(json_str)
        return json_str
