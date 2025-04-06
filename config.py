import yaml
import os
from typing import Dict, Any


def get_config() -> Dict[str, Any]:  # Dict[str, Any]: Словарь с конфигурационными параметрами
    config_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'config.yml'
    )

    try:
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)
            return config or {}

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Config file not found at: {config_path}. "
            "Please create config.yml in root directory."
        )

    except yaml.YAMLError as e:
        raise yaml.YAMLError(
            f"Error parsing YAML file: {e}"
        )
