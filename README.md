# Jira Integration Manager

Python реализация интеграции с Jira, переведенная с PHP кода `YoutrackManager`.

## Описание

Этот модуль предоставляет функциональность для:
- Создания задач в Jira на основе различных сущностей (продукты, рекламодатели, зоны)
- Добавления комментариев к существующим задачам
- Форматирования данных для отображения в Jira
- Работы с таблицами и ссылками

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Импортируйте модуль в ваш проект:
```python
from jira_integration import JiraManager, JiraApi, IssueManagerInterface, FrontendUrlGenerator
```

## Основные компоненты

### JiraManager
Основной класс для работы с Jira. Содержит методы для:
- `create_issue_from_product()` - создание задачи на основе продукта
- `create_issue_from_advertiser()` - создание задачи на основе рекламодателя
- `create_issue_from_zone()` - создание задачи на основе зоны
- `add_comment_for_limits()` - добавление комментария о лимитах
- `add_comment_for_started_campaigns()` - комментарий о запущенных кампаниях
- `add_comment_for_stopped_campaigns()` - комментарий об остановленных кампаниях

### JiraApi
Класс для работы с API Jira:
- `create_issue()` - создание новой задачи
- `add_comment_to_issue()` - добавление комментария
- `update_issue_params()` - обновление параметров задачи
- `get_table_header()` - создание заголовка таблицы
- `get_table_line()` - создание строки таблицы

### IssueManagerInterface
Интерфейс для создания задач с использованием паттерна Builder.

### FrontendUrlGenerator
Генератор ссылок на фронтенд приложения.

## Пример использования

```python
from jira_integration import JiraManager, JiraApi, IssueManagerInterface, FrontendUrlGenerator

# Настройка API
jira_api = JiraApi(
    base_url="https://your-jira-instance.atlassian.net",
    username="your-email@example.com",
    api_token="your-api-token"
)

# Создание менеджера
issue_manager = IssueManagerInterface()
frontend_generator = FrontendUrlGenerator()
jira_manager = JiraManager(jira_api, issue_manager, frontend_generator)

# Создание задачи на основе продукта
issue = jira_manager.create_issue_from_product(product, user)
issue_id = jira_manager.send_issue_to_jira(issue)
```

## Вспомогательные методы

### Форматирование
- `get_link()` - создание HTML ссылки
- `get_md_link()` - создание Markdown ссылки
- `wrap_in_html()` - обертка в HTML теги
- `wrap_in_code()` - обертка в блок кода
- `all_formats_to_string()` - преобразование различных типов в строку

### Работа с данными
- `array_to_formatted_string()` - форматирование массивов
- `rate_to_string()` - преобразование rate в строку
- `limit_to_string()` - преобразование limit в строку
- `campaign_to_string()` - преобразование campaign в строку

## Конфигурация

Для работы с реальным API Jira необходимо:

1. Получить API токен в Jira
2. Настроить базовый URL вашего экземпляра Jira
3. Указать корректные учетные данные

## Структура проекта

```
jira-integration/
├── jira_integration.py    # Основной модуль
├── example_usage.py       # Примеры использования
├── requirements.txt       # Зависимости
├── README.md             # Документация
└── docker-compose.yaml   # Docker конфигурация
```

## Запуск примеров

```bash
python example_usage.py
```

## Особенности реализации

1. **Типизация**: Использованы type hints для лучшей читаемости кода
2. **Dataclasses**: Использованы dataclasses для структуры данных
3. **Enums**: Перечисления для констант
4. **Builder Pattern**: Паттерн Builder для создания задач
5. **Моки**: Включены мок-классы для тестирования

## Миграция с PHP

Основные изменения при переводе с PHP:
- Использование Python типов вместо PHP docblocks
- Dataclasses вместо PHP классов с геттерами/сеттерами
- Enum вместо PHP констант
- Type hints вместо PHPDoc аннотаций
- Python naming conventions (snake_case вместо camelCase)

## Лицензия

Этот код является переводом с PHP и сохраняет ту же функциональность.
