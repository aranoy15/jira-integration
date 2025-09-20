"""
Jira Client - полноценный асинхронный клиент для работы с Jira API
"""

import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class JiraIssue:
    """Класс для представления задачи Jira"""

    project_key: str
    issue_type: str
    summary: str
    description: str
    assignee: Optional[str] = None
    priority: Optional[str] = None
    labels: Optional[List[str]] = None
    components: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class JiraClient:
    """Асинхронный клиент для работы с Jira API"""

    def __init__(
        self,
        base_url: str,
        username: str = None,
        api_token: str = None,
        password: str = None,
        auth_type: str = "bearer",
    ):
        """
        Инициализация клиента

        Args:
            base_url: URL Jira сервера (например: https://yourcompany.atlassian.net)
            username: Email пользователя или логин
            api_token: API токен (для Bearer auth)
            password: Пароль (для Basic auth)
            auth_type: Тип авторизации ("bearer", "basic", "session")
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.api_token = api_token
        self.password = password
        self.auth_type = auth_type
        self.session: Optional[aiohttp.ClientSession] = None

        self._lock = asyncio.Lock()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self._headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Python-Jira-Client/1.0",
        }

        self._setup_auth()

    def _setup_auth(self):
        """Настройка авторизации в зависимости от типа"""
        if self.auth_type == "bearer" and self.api_token:
            self._headers["Authorization"] = f"Bearer {self.api_token}"
        elif self.auth_type == "basic" and self.username and self.password:
            # Для basic auth будем использовать aiohttp.BasicAuth
            self._auth = aiohttp.BasicAuth(self.username, self.password)
        elif self.auth_type == "session":
            # Для session auth токен будет получен при первом запросе
            pass
        else:
            raise ValueError(
                f"Неверные параметры для авторизации типа {self.auth_type}"
            )

    async def _get_session(self) -> aiohttp.ClientSession:
        """Получает или создает асинхронную сессию"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            timeout = aiohttp.ClientTimeout(total=30)

            auth = None
            if self.auth_type == "basic" and hasattr(self, '_auth'):
                auth = self._auth

            self.session = aiohttp.ClientSession(
                headers=self._headers,
                connector=connector,
                timeout=timeout,
                auth=auth
            )
        return self.session

    async def _get_session_token(self):
        """Получение токена сессии для session auth"""
        if not self.username or not self.password:
            raise ValueError("Для session auth нужны username и password")

        session_data = {"username": self.username, "password": self.password}
        session = await self._get_session()

        try:
            async with session.post(
                f"{self.base_url}/rest/auth/1/session",
                json=session_data,
                headers={"Content-Type": "application/json"},
            ) as response:
                response.raise_for_status()
        except Exception as e:
            raise ValueError(f"Ошибка получения токена сессии: {e}")

    async def close(self):
        """Закрывает асинхронную сессию"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход"""
        await self.close()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        api_type: str = "api",
    ) -> Dict:
        """
        Выполняет асинхронный HTTP запрос к Jira API (thread-safe)

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: API endpoint (без базового URL)
            data: Данные для отправки
            api_type: Тип API ("api" для стандартного API, "agile" для Agile API)

        Returns:
            Ответ от API в виде словаря

        Raises:
            aiohttp.ClientError: При ошибке HTTP запроса
        """
        async with self._lock:
            if api_type == "agile":
                url = f"{self.base_url}/rest/agile/latest/{endpoint}"
            else:
                url = f"{self.base_url}/rest/api/2/{endpoint}"

            session = await self._get_session()

            # Для session auth получаем токен при первом запросе
            if self.auth_type == "session":
                await self._get_session_token()

            try:
                if method.upper() == "GET":
                    async with session.get(url, params=data) as response:
                        await self._handle_response(response, method, url, data)
                        return await self._parse_response(response)
                elif method.upper() == "POST":
                    async with session.post(url, json=data) as response:
                        await self._handle_response(response, method, url, data)
                        return await self._parse_response(response)
                elif method.upper() == "PUT":
                    async with session.put(url, json=data) as response:
                        await self._handle_response(response, method, url, data)
                        return await self._parse_response(response)
                elif method.upper() == "DELETE":
                    async with session.delete(url) as response:
                        await self._handle_response(response, method, url, data)
                        return await self._parse_response(response)
                else:
                    raise ValueError(f"Неподдерживаемый HTTP метод: {method}")

            except aiohttp.ClientError as e:
                self.logger.error(f"Ошибка при выполнении запроса {method} {url}: {e}")
                raise
            except ValueError as e:
                self.logger.error(f"Ошибка парсинга JSON: {e}")
                self.logger.error(f"URL: {url}")
                self.logger.error(f"Метод: {method}")
                self.logger.error(f"Данные: {data}")
                raise

    async def _handle_response(self, response: aiohttp.ClientResponse, method: str, url: str, data: Optional[Dict]):
        """Обрабатывает ответ от сервера"""
        try:
            response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            self.logger.error(f"Ошибка HTTP {e.status}: {e.message}")
            self.logger.error(f"URL: {url}")
            self.logger.error(f"Метод: {method}")
            self.logger.error(f"Данные: {data}")
            try:
                error_text = await response.text()
                self.logger.error(f"Текст ответа (первые 500 символов): {error_text[:500]}")
            except:
                self.logger.error("Не удалось получить текст ответа")
            raise

    async def _parse_response(self, response: aiohttp.ClientResponse) -> Dict:
        """Парсит ответ от сервера"""
        if response.status == 204:
            return {}

        content_type = response.headers.get("content-type", "").lower()
        if "application/json" not in content_type:
            self.logger.warning(f"Сервер вернул не JSON. Content-Type: {content_type}")
            try:
                text = await response.text()
                self.logger.warning(f"Текст ответа: {text[:500]}")
            except:
                self.logger.warning("Не удалось получить текст ответа")
            raise ValueError(
                f"Сервер вернул не JSON ответ. Content-Type: {content_type}"
            )

        try:
            return await response.json()
        except Exception as e:
            self.logger.error(f"Ошибка парсинга JSON: {e}")
            raise


    async def get_myself(self) -> Dict:
        """
        Получает информацию о текущем пользователе

        Returns:
            Информация о текущем пользователе
        """
        try:
            return await self._make_request("GET", "myself")
        except Exception as e:
            self.logger.error(f"Ошибка при получении информации о пользователе: {e}")
            raise

    async def test_connection(self) -> bool:
        """
        Проверяет соединение с Jira через myself API

        Returns:
            True если соединение успешно, False иначе
        """
        try:
            await self.get_myself()
            self.logger.info("Соединение с Jira установлено успешно")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка соединения с Jira: {e}")
            return False


    async def get_projects(self) -> List[Dict]:
        """
        Получает список проектов

        Returns:
            Список проектов
        """
        try:
            projects = await self._make_request("GET", "project")
            self.logger.info(f"Найдено проектов: {len(projects)}")
            return projects
        except Exception as e:
            self.logger.error(f"Ошибка при получении проектов: {e}")
            return []

    async def get_project(self, project_key_or_id: str) -> Dict:
        """
        Получает информацию о проекте

        Args:
            project_key_or_id: Ключ или ID проекта

        Returns:
            Информация о проекте
        """
        try:
            return await self._make_request("GET", f"project/{project_key_or_id}")
        except Exception as e:
            self.logger.error(f"Ошибка при получении проекта {project_key_or_id}: {e}")
            raise

    async def search_issues(
        self,
        jql: str,
        start_at: int = 0,
        max_results: int = 50,
        fields: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Dict:
        """
        Выполняет поиск задач по JQL

        Args:
            jql: JQL запрос
            start_at: Начальная позиция для пагинации
            max_results: Максимальное количество результатов
            fields: Поля для возврата
            expand: Поля для расширения

        Returns:
            Результаты поиска
        """
        search_data = {"jql": jql, "startAt": start_at, "maxResults": max_results}

        if fields:
            search_data["fields"] = fields
        if expand:
            search_data["expand"] = expand

        try:
            result = await self._make_request("POST", "search", search_data)
            self.logger.info(f"Найдено задач: {result.get('total', 0)}")
            return result
        except Exception as e:
            self.logger.error(f"Ошибка при поиске задач: {e}")
            raise

    async def get_issue(
        self,
        issue_key_or_id: str,
        fields: Optional[List[str]] = None,
        expand: Optional[List[str]] = None,
    ) -> Dict:
        """
        Получает информацию о задаче

        Args:
            issue_key_or_id: Ключ или ID задачи
            fields: Поля для возврата
            expand: Поля для расширения

        Returns:
            Информация о задаче
        """
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        if expand:
            params["expand"] = ",".join(expand)

        try:
            return await self._make_request("GET", f"issue/{issue_key_or_id}", params)
        except Exception as e:
            self.logger.error(f"Ошибка при получении задачи {issue_key_or_id}: {e}")
            raise

    async def create_issue(self, issue: JiraIssue) -> str:
        """
        Создает новую задачу

        Args:
            issue: Объект задачи

        Returns:
            Ключ созданной задачи (например: PROJ-123)
        """
        issue_data = {
            "fields": {
                "project": {"key": issue.project_key},
                "issuetype": {"name": issue.issue_type},
                "summary": issue.summary,
                "description": issue.description,
            }
        }

        if issue.assignee:
            issue_data["fields"]["assignee"] = {"name": issue.assignee}

        if issue.priority:
            issue_data["fields"]["priority"] = {"name": issue.priority}

        if issue.labels:
            issue_data["fields"]["labels"] = issue.labels

        if issue.components:
            issue_data["fields"]["components"] = [
                {"name": comp} for comp in issue.components
            ]

        if issue.custom_fields:
            issue_data["fields"].update(issue.custom_fields)

        try:
            result = await self._make_request("POST", "issue", issue_data)
            issue_key = result.get("key")
            self.logger.info(f"Задача создана: {issue_key}")
            return issue_key
        except Exception as e:
            self.logger.error(f"Ошибка при создании задачи: {e}")
            raise

    async def update_issue(self, issue_key_or_id: str, fields: Dict[str, Any]) -> None:
        """
        Обновляет задачу

        Args:
            issue_key_or_id: Ключ или ID задачи
            fields: Поля для обновления
        """
        try:
            update_data = {"fields": fields}
            await self._make_request("PUT", f"issue/{issue_key_or_id}", update_data)
            self.logger.info(f"Задача {issue_key_or_id} обновлена")
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении задачи {issue_key_or_id}: {e}")
            raise

    async def add_comment(self, issue_key_or_id: str, comment_body: str) -> None:
        """
        Добавляет комментарий к задаче

        Args:
            issue_key_or_id: Ключ или ID задачи
            comment_body: Текст комментария
        """
        comment_data = {"body": comment_body}

        try:
            await self._make_request("POST", f"issue/{issue_key_or_id}/comment", comment_data)
            self.logger.info(f"Комментарий добавлен к задаче {issue_key_or_id}")
        except Exception as e:
            self.logger.error(
                f"Ошибка при добавлении комментария к задаче {issue_key_or_id}: {e}"
            )
            raise

    def get_issue_url(self, issue_key: str) -> str:
        """
        Возвращает URL задачи в веб-интерфейсе

        Args:
            issue_key: Ключ задачи

        Returns:
            URL задачи
        """
        return f"{self.base_url}/browse/{issue_key}"


    async def get_boards(
        self,
        start_at: int = 0,
        max_results: int = 50,
        board_type: Optional[str] = None,
        name: Optional[str] = None,
        project_key_or_id: Optional[str] = None,
    ) -> List[Dict]:
        """
        Получает список досок (boards) согласно Agile API

        Args:
            start_at: Начальная позиция для пагинации
            max_results: Максимальное количество результатов
            board_type: Тип доски (например: "scrum", "kanban")
            name: Фильтр по имени доски
            project_key_or_id: Фильтр по проекту

        Returns:
            Список досок
        """
        params = {"startAt": start_at, "maxResults": max_results}

        if board_type:
            params["type"] = board_type
        if name:
            params["name"] = name
        if project_key_or_id:
            params["projectKeyOrId"] = project_key_or_id

        try:
            result = await self._make_request("GET", "board", params, api_type="agile")
            boards = result.get("values", [])
            self.logger.info(f"Найдено досок: {len(boards)}")
            return boards
        except Exception as e:
            self.logger.error(f"Ошибка при получении досок: {e}")
            return []

    async def get_board(self, board_id: int) -> Dict:
        """
        Получает информацию о конкретной доске

        Args:
            board_id: ID доски

        Returns:
            Информация о доске
        """
        try:
            return await self._make_request("GET", f"board/{board_id}", api_type="agile")
        except Exception as e:
            self.logger.error(f"Ошибка при получении доски {board_id}: {e}")
            raise

    async def get_board_issues(
        self,
        board_id: int,
        start_at: int = 0,
        max_results: int = 50,
        jql: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> List[Dict]:
        """
        Получает задачи для доски

        Args:
            board_id: ID доски
            start_at: Начальная позиция для пагинации
            max_results: Максимальное количество результатов
            jql: JQL запрос для фильтрации
            fields: Поля для возврата

        Returns:
            Список задач доски
        """
        params = {"startAt": start_at, "maxResults": max_results}

        if jql:
            params["jql"] = jql
        if fields:
            params["fields"] = fields

        try:
            result = await self._make_request(
                "GET", f"board/{board_id}/issue", params, api_type="agile"
            )
            issues = result.get("issues", [])
            self.logger.info(f"Найдено задач на доске: {len(issues)}")
            return issues
        except Exception as e:
            self.logger.error(f"Ошибка при получении задач доски {board_id}: {e}")
            return []

    async def get_board_backlog(
        self,
        board_id: int,
        start_at: int = 0,
        max_results: int = 50,
        jql: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> List[Dict]:
        """
        Получает задачи из бэклога доски

        Args:
            board_id: ID доски
            start_at: Начальная позиция для пагинации
            max_results: Максимальное количество результатов
            jql: JQL запрос для фильтрации
            fields: Поля для возврата

        Returns:
            Список задач бэклога
        """
        params = {"startAt": start_at, "maxResults": max_results}

        if jql:
            params["jql"] = jql
        if fields:
            params["fields"] = fields

        try:
            result = await self._make_request(
                "GET", f"board/{board_id}/backlog", params, api_type="agile"
            )
            issues = result.get("issues", [])
            self.logger.info(f"Найдено задач в бэклоге: {len(issues)}")
            return issues
        except Exception as e:
            self.logger.error(f"Ошибка при получении бэклога доски {board_id}: {e}")
            return []

    async def create_sprint(
        self,
        name: str,
        origin_board_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        goal: Optional[str] = None,
    ) -> Dict:
        """
        Создает новый спринт

        Args:
            name: Название спринта
            origin_board_id: ID доски
            start_date: Дата начала (ISO 8601)
            end_date: Дата окончания (ISO 8601)
            goal: Цель спринта

        Returns:
            Информация о созданном спринте
        """
        sprint_data = {
            "name": name,
            "originBoardId": origin_board_id,
            "autoStartStop": True,
            "synced": False,
        }

        if start_date:
            sprint_data["startDate"] = start_date
        if end_date:
            sprint_data["endDate"] = end_date
        if goal:
            sprint_data["goal"] = goal

        try:
            result = await self._make_request("POST", "sprint", sprint_data, api_type="agile")
            self.logger.info(f"Создан спринт: {name}")
            return result
        except Exception as e:
            self.logger.error(f"Ошибка при создании спринта: {e}")
            raise

    async def get_sprint_issues(
        self,
        sprint_id: int,
        start_at: int = 0,
        max_results: int = 50,
        jql: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> List[Dict]:
        """
        Получает задачи спринта

        Args:
            sprint_id: ID спринта
            start_at: Начальная позиция для пагинации
            max_results: Максимальное количество результатов
            jql: JQL запрос для фильтрации
            fields: Поля для возврата

        Returns:
            Список задач спринта
        """
        params = {"startAt": start_at, "maxResults": max_results}

        if jql:
            params["jql"] = jql
        if fields:
            params["fields"] = fields

        try:
            result = await self._make_request(
                "GET", f"sprint/{sprint_id}/issue", params, api_type="agile"
            )
            issues = result.get("issues", [])
            self.logger.info(f"Найдено задач в спринте: {len(issues)}")
            return issues
        except Exception as e:
            self.logger.error(f"Ошибка при получении задач спринта {sprint_id}: {e}")
            return []

    async def move_issues_to_sprint(self, sprint_id: int, issue_keys: List[str]) -> None:
        """
        Перемещает задачи в спринт

        Args:
            sprint_id: ID спринта
            issue_keys: Список ключей задач
        """
        move_data = {"issues": issue_keys}

        try:
            await self._make_request(
                "POST", f"sprint/{sprint_id}/issue", move_data, api_type="agile"
            )
            self.logger.info(f"Перемещено {len(issue_keys)} задач в спринт {sprint_id}")
        except Exception as e:
            self.logger.error(f"Ошибка при перемещении задач в спринт: {e}")
            raise

    async def move_issues_to_backlog(self, issue_keys: List[str]) -> None:
        """
        Перемещает задачи в бэклог

        Args:
            issue_keys: Список ключей задач
        """
        move_data = {"issues": issue_keys}

        try:
            await self._make_request("POST", "backlog/issue", move_data, api_type="agile")
            self.logger.info(f"Перемещено {len(issue_keys)} задач в бэклог")
        except Exception as e:
            self.logger.error(f"Ошибка при перемещении задач в бэклог: {e}")
            raise
