import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

class Config:
    def __init__(self, config_file: str = "config.yaml"):
        load_dotenv()
        self.config = self.load_config(config_file)
        self.substitute_env_variables()
        print("CONFIG++++", self.config)

    def load_config(self, config_file: str):
        config_path = Path(config_file)
        if not config_path.is_file():
            raise FileNotFoundError(f"Configuration file {config_file} not found.")
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)

    def substitute_env_variables(self):
        for key, value in self.config.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                self.config[key] = os.getenv(env_var)
            elif isinstance(value, dict):
                self._substitute_env_variables_in_dict(value)

    def _substitute_env_variables_in_dict(self, d):
        for key, value in d.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                d[key] = os.getenv(env_var)
            elif isinstance(value, dict):
                self._substitute_env_variables_in_dict(value)

    def get(self, key: str, default=None):
        return self.config.get(key, default)
