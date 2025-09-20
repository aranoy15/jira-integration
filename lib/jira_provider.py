import json
import os
from typing import Protocol, List, Dict, Any
from .jira_client import JiraIssue

class JiraProviderBase(Protocol):
    """Базовый интерфейс для поставщиков данных Jira"""

    def get_issues(self) -> List[Dict[str, Any]]:
        """Получить задачи"""
        pass

class JiraJsonProvider(JiraProviderBase):
    """Поставщик данных из JSON файла"""

    def __init__(self, json_file_path: str):
        """
        Инициализация поставщика JSON

        Args:
            json_file_path: Путь к JSON файлу с данными Jira
        """
        self.json_file_path = json_file_path
        self._validate_file()

    def _validate_file(self) -> None:
        """Проверка существования файла"""
        if not os.path.exists(self.json_file_path):
            raise FileNotFoundError(f"JSON файл не найден: {self.json_file_path}")

        if not self.json_file_path.endswith('.json'):
            raise ValueError(f"Файл должен иметь расширение .json: {self.json_file_path}")

    def get_issues(self) -> List[Dict[str, Any]]:
        """Получить задачи из JSON файла"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if isinstance(data, list):
                return data

            if isinstance(data, dict) and 'issues' in data:
                return data['issues']

            if isinstance(data, dict) and 'results' in data:
                return data['results']

            if isinstance(data, dict):
                return [data]

            raise ValueError(f"Неожиданный формат данных в JSON файле: {type(data)}")

        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга JSON файла: {e}")
        except Exception as e:
            raise RuntimeError(f"Ошибка чтения файла {self.json_file_path}: {e}")
