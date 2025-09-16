"""
Jira Client - полноценный клиент для работы с Jira API
"""

import requests
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
    """Клиент для работы с Jira API"""

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
        self.session = requests.Session()

        # Настройка авторизации
        self._setup_auth()

        # Общие заголовки
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Python-Jira-Client/1.0",
            }
        )

    def _setup_auth(self):
        """Настройка авторизации в зависимости от типа"""
        if self.auth_type == "bearer" and self.api_token:
            self.session.headers["Authorization"] = f"Bearer {self.api_token}"
        elif self.auth_type == "basic" and self.username and self.password:
            self.session.auth = (self.username, self.password)
        elif self.auth_type == "session":
            # Для session auth нужно сначала получить токен
            self._get_session_token()
        else:
            raise ValueError(
                f"Неверные параметры для авторизации типа {self.auth_type}"
            )

    def _get_session_token(self):
        """Получение токена сессии для session auth"""
        if not self.username or not self.password:
            raise ValueError("Для session auth нужны username и password")

        session_data = {"username": self.username, "password": self.password}

        try:
            response = self.session.post(
                f"{self.base_url}/rest/auth/1/session",
                json=session_data,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            # Токен автоматически сохраняется в cookies
        except Exception as e:
            raise ValueError(f"Ошибка получения токена сессии: {e}")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        api_type: str = "api",
    ) -> Dict:
        """
        Выполняет HTTP запрос к Jira API

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: API endpoint (без базового URL)
            data: Данные для отправки
            api_type: Тип API ("api" для стандартного API, "agile" для Agile API)

        Returns:
            Ответ от API в виде словаря

        Raises:
            requests.RequestException: При ошибке HTTP запроса
        """
        if api_type == "agile":
            url = f"{self.base_url}/rest/agile/latest/{endpoint}"
        else:
            url = f"{self.base_url}/rest/api/2/{endpoint}"

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=data)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Неподдерживаемый HTTP метод: {method}")

            response.raise_for_status()

            # Возвращаем пустой словарь для DELETE запросов без контента
            if response.status_code == 204:
                return {}

            # Проверяем что ответ JSON
            content_type = response.headers.get("content-type", "").lower()
            if "application/json" not in content_type:
                print(f"⚠️ Сервер вернул не JSON. Content-Type: {content_type}")
                print(f"Текст ответа: {response.text[:500]}")
                raise ValueError(
                    f"Сервер вернул не JSON ответ. Content-Type: {content_type}"
                )

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выполнении запроса {method} {url}: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Статус код: {e.response.status_code}")
                print(f"Заголовки ответа: {dict(e.response.headers)}")
                print(f"Текст ответа (первые 500 символов): {e.response.text[:500]}")
                try:
                    error_data = e.response.json()
                    print(f"JSON ошибки: {error_data}")
                except:
                    print("Ответ не является валидным JSON")
            raise
        except ValueError as e:
            print(f"Ошибка парсинга JSON: {e}")
            print(f"URL: {url}")
            print(f"Метод: {method}")
            print(f"Данные: {data}")
            raise

    # === Myself API методы ===
    # Согласно документации: https://developer.atlassian.com/server/jira/platform/rest/v11000/api-group-myself/#api-group-myself

    def get_myself(self) -> Dict:
        """
        Получает информацию о текущем пользователе

        Returns:
            Информация о текущем пользователе
        """
        try:
            return self._make_request("GET", "myself")
        except Exception as e:
            print(f"Ошибка при получении информации о пользователе: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Проверяет соединение с Jira через myself API

        Returns:
            True если соединение успешно, False иначе
        """
        try:
            self.get_myself()
            print("✅ Соединение с Jira установлено успешно")
            return True
        except Exception as e:
            print(f"❌ Ошибка соединения с Jira: {e}")
            return False

    # === Issue API методы ===

    def get_projects(self) -> List[Dict]:
        """
        Получает список проектов

        Returns:
            Список проектов
        """
        try:
            projects = self._make_request("GET", "project")
            print(f"Найдено проектов: {len(projects)}")
            return projects
        except Exception as e:
            print(f"Ошибка при получении проектов: {e}")
            return []

    def get_project(self, project_key_or_id: str) -> Dict:
        """
        Получает информацию о проекте

        Args:
            project_key_or_id: Ключ или ID проекта

        Returns:
            Информация о проекте
        """
        try:
            return self._make_request("GET", f"project/{project_key_or_id}")
        except Exception as e:
            print(f"Ошибка при получении проекта {project_key_or_id}: {e}")
            raise

    def search_issues(
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
            result = self._make_request("POST", "search", search_data)
            print(f"Найдено задач: {result.get('total', 0)}")
            return result
        except Exception as e:
            print(f"Ошибка при поиске задач: {e}")
            raise

    def get_issue(
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
            return self._make_request("GET", f"issue/{issue_key_or_id}", params)
        except Exception as e:
            print(f"Ошибка при получении задачи {issue_key_or_id}: {e}")
            raise

    def create_issue(self, issue: JiraIssue) -> str:
        """
        Создает новую задачу

        Args:
            issue: Объект задачи

        Returns:
            Ключ созданной задачи (например: PROJ-123)
        """
        # Подготовка данных для создания задачи
        issue_data = {
            "fields": {
                "project": {"key": issue.project_key},
                "issuetype": {"name": issue.issue_type},
                "summary": issue.summary,
                "description": issue.description,
            }
        }

        # Добавляем опциональные поля
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

        # Добавляем кастомные поля
        if issue.custom_fields:
            issue_data["fields"].update(issue.custom_fields)

        try:
            result = self._make_request("POST", "issue", issue_data)
            issue_key = result.get("key")
            print(f"✅ Задача создана: {issue_key}")
            return issue_key
        except Exception as e:
            print(f"❌ Ошибка при создании задачи: {e}")
            raise

    def update_issue(self, issue_key_or_id: str, fields: Dict[str, Any]) -> None:
        """
        Обновляет задачу

        Args:
            issue_key_or_id: Ключ или ID задачи
            fields: Поля для обновления
        """
        try:
            update_data = {"fields": fields}
            self._make_request("PUT", f"issue/{issue_key_or_id}", update_data)
            print(f"✅ Задача {issue_key_or_id} обновлена")
        except Exception as e:
            print(f"❌ Ошибка при обновлении задачи {issue_key_or_id}: {e}")
            raise

    def add_comment(self, issue_key_or_id: str, comment_body: str) -> None:
        """
        Добавляет комментарий к задаче

        Args:
            issue_key_or_id: Ключ или ID задачи
            comment_body: Текст комментария
        """
        comment_data = {"body": comment_body}

        try:
            self._make_request("POST", f"issue/{issue_key_or_id}/comment", comment_data)
            print(f"✅ Комментарий добавлен к задаче {issue_key_or_id}")
        except Exception as e:
            print(
                f"❌ Ошибка при добавлении комментария к задаче {issue_key_or_id}: {e}"
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

    # === Agile API методы ===

    def get_boards(
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
            result = self._make_request("GET", "board", params, api_type="agile")
            boards = result.get("values", [])
            print(f"Найдено досок: {len(boards)}")
            return boards
        except Exception as e:
            print(f"Ошибка при получении досок: {e}")
            return []

    def get_board(self, board_id: int) -> Dict:
        """
        Получает информацию о конкретной доске

        Args:
            board_id: ID доски

        Returns:
            Информация о доске
        """
        try:
            return self._make_request("GET", f"board/{board_id}", api_type="agile")
        except Exception as e:
            print(f"Ошибка при получении доски {board_id}: {e}")
            raise

    def get_board_issues(
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
            result = self._make_request(
                "GET", f"board/{board_id}/issue", params, api_type="agile"
            )
            issues = result.get("issues", [])
            print(f"Найдено задач на доске: {len(issues)}")
            return issues
        except Exception as e:
            print(f"Ошибка при получении задач доски {board_id}: {e}")
            return []

    def get_board_backlog(
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
            result = self._make_request(
                "GET", f"board/{board_id}/backlog", params, api_type="agile"
            )
            issues = result.get("issues", [])
            print(f"Найдено задач в бэклоге: {len(issues)}")
            return issues
        except Exception as e:
            print(f"Ошибка при получении бэклога доски {board_id}: {e}")
            return []

    def create_sprint(
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
            result = self._make_request("POST", "sprint", sprint_data, api_type="agile")
            print(f"✅ Создан спринт: {name}")
            return result
        except Exception as e:
            print(f"❌ Ошибка при создании спринта: {e}")
            raise

    def get_sprint_issues(
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
            result = self._make_request(
                "GET", f"sprint/{sprint_id}/issue", params, api_type="agile"
            )
            issues = result.get("issues", [])
            print(f"Найдено задач в спринте: {len(issues)}")
            return issues
        except Exception as e:
            print(f"Ошибка при получении задач спринта {sprint_id}: {e}")
            return []

    def move_issues_to_sprint(self, sprint_id: int, issue_keys: List[str]) -> None:
        """
        Перемещает задачи в спринт

        Args:
            sprint_id: ID спринта
            issue_keys: Список ключей задач
        """
        move_data = {"issues": issue_keys}

        try:
            self._make_request(
                "POST", f"sprint/{sprint_id}/issue", move_data, api_type="agile"
            )
            print(f"✅ Перемещено {len(issue_keys)} задач в спринт {sprint_id}")
        except Exception as e:
            print(f"❌ Ошибка при перемещении задач в спринт: {e}")
            raise

    def move_issues_to_backlog(self, issue_keys: List[str]) -> None:
        """
        Перемещает задачи в бэклог

        Args:
            issue_keys: Список ключей задач
        """
        move_data = {"issues": issue_keys}

        try:
            self._make_request("POST", "backlog/issue", move_data, api_type="agile")
            print(f"✅ Перемещено {len(issue_keys)} задач в бэклог")
        except Exception as e:
            print(f"❌ Ошибка при перемещении задач в бэклог: {e}")
            raise
