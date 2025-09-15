"""
Пример использования Jira Integration Manager
"""

from jira_integration import JiraManager, JiraApi, IssueManagerInterface, FrontendUrlGenerator
from jira_integration import ZoneYoutrackIssueDto, RevenueTypeEnum, AdvertiserDepartmentTypeEnum


class MockEntity:
    """Мок-класс для тестирования"""
    def __init__(self, id_val, name):
        self.id = id_val
        self.name = name


class MockProduct(MockEntity):
    """Мок-класс продукта"""
    def __init__(self, id_val, name):
        super().__init__(id_val, name)
        self.advertiser = MockAdvertiser(1, "Test Advertiser")
        self.campaigns = []
        self.categories = [MockEntity(1, "Category 1")]
        self.preview_url = "https://example.com/preview"
        self.kpi = "Test KPI"
        self.revenue_type = RevenueTypeEnum.PARSED
        self.limits = []
        self.is_with_preland = True
        self.is_direct_link = False
        self.is_without_direct_link = True


class MockAdvertiser(MockEntity):
    """Мок-класс рекламодателя"""
    def __init__(self, id_val, name):
        super().__init__(id_val, name)
        self.department = AdvertiserDepartmentTypeEnum.SSP
        self.geo_groups = [MockEntity(1, "US")]
        self.work_models = [MockEntity(1, "CPA")]
        self.traffic_types = [MockEntity(1, "Mobile")]
        self.revenue_type = RevenueTypeEnum.PARSED
        self.monthly_spend = 10000
        self.manager_comment = "Test comment"
        self.landing_info = "https://example.com"
        self.type = "test_type"
        self.is_new = True


class MockUser(MockEntity):
    """Мок-класс пользователя"""
    def __init__(self, id_val, name):
        super().__init__(id_val, name)
        self.youtrack_login = "test_user"


class MockIssueManager(IssueManagerInterface):
    """Мок-реализация менеджера задач"""
    def create_issue(self, project: str):
        from jira_integration import IssueBuilder
        return IssueBuilder()


def main():
    """Основная функция с примерами использования"""

    # Настройка API
    jira_api = JiraApi(
        base_url="http://localhost:8080",
        username="your-email@example.com",
        api_token="your-api-token"
    )

    # Создание менеджера задач
    issue_manager = MockIssueManager()

    # Создание генератора URL
    frontend_generator = FrontendUrlGenerator()

    # Создание основного менеджера
    jira_manager = JiraManager(jira_api, issue_manager, frontend_generator)

    # Создание тестовых данных
    user = MockUser(1, "Test User")
    advertiser = MockAdvertiser(1, "Test Advertiser")
    product = MockProduct(1, "Test Product")

    print("=== Примеры использования Jira Integration Manager ===\n")

    # 1. Создание задачи на основе продукта
    print("1. Создание задачи на основе продукта:")
    try:
        issue = jira_manager.create_issue_from_product(product, user)
        print(f"   Создана задача: {issue.summary}")
        print(f"   Описание: {issue.description[:100]}...")
    except Exception as e:
        print(f"   Ошибка: {e}")

    print()

    # 2. Создание задачи на основе рекламодателя
    print("2. Создание задачи на основе рекламодателя:")
    try:
        issue = jira_manager.create_issue_from_advertiser(advertiser, user)
        print(f"   Создана задача: {issue.summary}")
        print(f"   Исполнитель: {issue.assignee}")
    except Exception as e:
        print(f"   Ошибка: {e}")

    print()

    # 3. Создание задачи на основе зоны
    print("3. Создание задачи на основе зоны:")
    try:
        zone_dto = ZoneYoutrackIssueDto(
            summary="Test Zone Issue",
            description="Description for zone issue"
        )
        issue = jira_manager.create_issue_from_zone(zone_dto, user)
        print(f"   Создана задача: {issue.summary}")
    except Exception as e:
        print(f"   Ошибка: {e}")

    print()

    # 4. Работа с комментариями
    print("4. Добавление комментариев:")
    try:
        # Мок-данные для комментариев
        external_offer = MockEntity(1, "Test Offer")
        external_offer.issue = "TEST-123"

        changes = {
            "limit1": [
                {"period": "daily", "type": "impression", "value": 1000},
                {"period": "daily", "type": "impression", "value": 2000}
            ]
        }

        jira_manager.add_comment_for_limits(external_offer, product, changes)
        print("   Комментарий о лимитах добавлен")

        # Комментарий о запущенных кампаниях
        campaigns_data = [[
            {
                "issue_id": "TEST-123",
                "last_stopped_at": None,
                "campaign_id": 1,
                "campaign_name": "Test Campaign"
            }
        ]]
        jira_manager.add_comment_for_started_campaigns(campaigns_data)
        print("   Комментарий о запущенных кампаниях добавлен")

    except Exception as e:
        print(f"   Ошибка: {e}")

    print()

    # 5. Вспомогательные методы
    print("5. Вспомогательные методы:")
    try:
        # Создание ссылок
        html_link = jira_manager.get_link("https://example.com", "Example")
        md_link = jira_manager.get_md_link("https://example.com", "Example")
        print(f"   HTML ссылка: {html_link}")
        print(f"   Markdown ссылка: {md_link}")

        # Форматирование данных
        test_data = {"key1": "value1", "key2": ["item1", "item2"]}
        formatted = jira_manager.all_formats_to_string(test_data)
        print(f"   Отформатированные данные: {formatted[:50]}...")

        # Временной формат
        time_format = jira_manager.timestamp_range_to_compact_format(1609459200, 1609545600)
        print(f"   Временной диапазон: {time_format}")

    except Exception as e:
        print(f"   Ошибка: {e}")

    print("\n=== Примеры завершены ===")


if __name__ == "__main__":
    main()
