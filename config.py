import json
from pathlib import Path


class Config:
    def __init__(self, cache_dir):
        self.cache_dir = Path(cache_dir)
        self.settings = self._load_settings()

    def _load_settings(self) -> dict:
        settings_file = self.cache_dir / "settings.json"

        if not settings_file.exists():
            settings_file.parent.mkdir(exist_ok=True)
            default = {"stamp_size": 42, "sign_size": 20}
            settings_file.write_text(json.dumps(default, indent=4), encoding="utf-8")
            return default

        return json.loads(settings_file.read_text(encoding="utf-8"))

    def save_settings(self) -> None:  # Обновляем текущие настройки
        self._save_raw(self.settings)

    def _save_raw(self, data: dict) -> None:
        settings_file = self.cache_dir / "settings.json"
        settings_file.write_text(json.dumps(data, indent=4), encoding="utf-8")