"""
Асинхронный сервис для работы с Jira API
Использует существующий клиент из jira_client.py
"""

import asyncio
import os
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor
from .jira_client import JiraClient, JiraIssue


class AsyncJiraService:
    """Асинхронный сервис для работы с Jira"""

    def __init__(self, base_url: str, username: str, api_token: str,
                 password: str = None, auth_type: str = "bearer"):
        """Инициализация сервиса"""
        self.client = JiraClient(
            base_url=base_url,
            username=username,
            api_token=api_token,
            password=password,
            auth_type=auth_type
        )
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход"""
        self.executor.shutdown(wait=True)

    # Делегируем все методы клиенту через ThreadPoolExecutor
    async def get_myself(self) -> Dict:
        """Получает информацию о текущем пользователе"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.client.get_myself)

    async def get_projects(self) -> List[Dict]:
        """Получает список проектов"""
        return await asyncio.to_thread(self.client.get_projects)

    async def get_project(self, project_key_or_id: str) -> Dict:
        """Получает информацию о проекте"""
        return await asyncio.to_thread(self.client.get_project, project_key_or_id)

    async def search_issues(self, jql: str, start_at: int = 0, max_results: int = 50,
                           fields: Optional[List[str]] = None,
                           expand: Optional[List[str]] = None) -> Dict:
        """Выполняет поиск задач по JQL"""
        return await asyncio.to_thread(
            self.client.search_issues, jql, start_at, max_results, fields, expand
        )

    async def get_issue(self, issue_key_or_id: str, fields: Optional[List[str]] = None,
                       expand: Optional[List[str]] = None) -> Dict:
        """Получает информацию о задаче"""
        return await asyncio.to_thread(
            self.client.get_issue, issue_key_or_id, fields, expand
        )

    async def create_issue(self, issue: JiraIssue) -> str:
        """Создает новую задачу"""
        return await asyncio.to_thread(self.client.create_issue, issue)

    async def update_issue(self, issue_key_or_id: str, fields: Dict[str, Any]) -> None:
        """Обновляет задачу"""
        return await asyncio.to_thread(self.client.update_issue, issue_key_or_id, fields)

    async def add_comment(self, issue_key_or_id: str, comment_body: str) -> None:
        """Добавляет комментарий к задаче"""
        return await asyncio.to_thread(self.client.add_comment, issue_key_or_id, comment_body)

    def get_issue_url(self, issue_key: str) -> str:
        """Получает URL задачи"""
        return self.client.get_issue_url(issue_key)

    # Agile API методы
    async def get_boards(self, start_at: int = 0, max_results: int = 50,
                        board_type: Optional[str] = None, name: Optional[str] = None,
                        project_key_or_id: Optional[str] = None) -> List[Dict]:
        """Получает список досок"""
        return await asyncio.to_thread(
            self.client.get_boards, start_at, max_results, board_type, name, project_key_or_id
        )

    async def get_board(self, board_id: int) -> Dict:
        """Получает информацию о доске"""
        return await asyncio.to_thread(self.client.get_board, board_id)

    async def get_board_issues(self, board_id: int, start_at: int = 0, max_results: int = 50,
                              jql: Optional[str] = None, fields: Optional[str] = None) -> List[Dict]:
        """Получает задачи для доски"""
        return await asyncio.to_thread(
            self.client.get_board_issues, board_id, start_at, max_results, jql, fields
        )

    async def get_board_backlog(self, board_id: int, start_at: int = 0, max_results: int = 50,
                               jql: Optional[str] = None, fields: Optional[str] = None) -> List[Dict]:
        """Получает задачи из бэклога доски"""
        return await asyncio.to_thread(
            self.client.get_board_backlog, board_id, start_at, max_results, jql, fields
        )

    async def create_sprint(self, name: str, origin_board_id: int, start_date: Optional[str] = None,
                           end_date: Optional[str] = None, goal: Optional[str] = None) -> Dict:
        """Создает новый спринт"""
        return await asyncio.to_thread(
            self.client.create_sprint, name, origin_board_id, start_date, end_date, goal
        )

    async def get_sprint_issues(self, sprint_id: int, start_at: int = 0, max_results: int = 50,
                               jql: Optional[str] = None, fields: Optional[str] = None) -> List[Dict]:
        """Получает задачи спринта"""
        return await asyncio.to_thread(
            self.client.get_sprint_issues, sprint_id, start_at, max_results, jql, fields
        )

    async def move_issues_to_sprint(self, sprint_id: int, issue_keys: List[str]) -> None:
        """Перемещает задачи в спринт"""
        return await asyncio.to_thread(self.client.move_issues_to_sprint, sprint_id, issue_keys)

    async def move_issues_to_backlog(self, issue_keys: List[str]) -> None:
        """Перемещает задачи в бэклог"""
        return await asyncio.to_thread(self.client.move_issues_to_backlog, issue_keys)
