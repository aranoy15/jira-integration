"""
Jira Integration Manager - Python implementation
Переведено с PHP кода YoutrackManager
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum


class AdvertiserDepartmentTypeEnum(Enum):
    SSP = "SSP"


class AdvertiserTypeEnum(Enum):
    # Добавьте нужные типы
    pass


class RevenueTypeEnum(Enum):
    PARSED = "parsed"
    # Добавьте другие типы


class YouTrackUserEnum(Enum):
    D_PACHKO = "d_pachko"
    V_KALMYKOV = "v_kalmykov"
    E_MALIHINA = "e_malihina"


class LimitEnum(Enum):
    DEPRECATED_TYPE_LIST = {
        # Добавьте нужные типы
    }


@dataclass
class Issue:
    """Класс для работы с задачами Jira"""
    PROJECT_OPTIMIZATION = "OPT"
    TASK_ADV = "Task"
    TASK_PUB = "Task"
    PRODUCT_TO_REPLACE = "PRODUCT_TO_REPLACE"
    ADVERTISER_TO_REPLACE = "ADVERTISER_TO_REPLACE"
    SSP_ADVERTISER_TO_REPLACE = "SSP_ADVERTISER_TO_REPLACE"

    def __init__(self):
        self.project = ""
        self.type_task = ""
        self.summary = ""
        self.description = ""
        self.assignee = ""
        self.creator = ""
        self.priority = ""
        self.watchers = []

    @staticmethod
    def get_product_template_md() -> str:
        """Шаблон для задач по продуктам"""
        return """
**Создатель:** {0}
**Рекламодатель:** {1}
**Продукт:** {2}
**Preview URL:** {3}
**KPI:** {4}
**Категории:** {5}
**Тип доходности:** {6}

{7}

{8}

{9}

**Кампании:**
{10}

**Campaign IDs:** {11}
        """.strip()

    @staticmethod
    def get_advertiser_template() -> str:
        """Шаблон для задач по рекламодателям"""
        return """
**Создатель:** {0}
**Рекламодатель:** {1}
**Гео:** {2}
**Модели работы:** {3}
**Типы трафика:** {4}
**Landing Info:** {5}
**Тип рекламодателя:** {6}
        """.strip()

    @staticmethod
    def get_ssp_advertiser_template() -> str:
        """Шаблон для SSP рекламодателей"""
        return """
**Создатель:** {0}
**Рекламодатель:** {1}
**Тип доходности:** {2}
**Месячные траты:** {3}
**Комментарий менеджера:** {4}
        """.strip()


@dataclass
class ZoneYoutrackIssueDto:
    """DTO для задач по зонам"""
    summary: str
    description: str


class JiraApi:
    """API для работы с Jira"""

    def __init__(self, base_url: str, username: str, api_token: str):
        self.base_url = base_url
        self.username = username
        self.api_token = api_token
        self.session = None  # Здесь будет requests.Session

    def get_table_header(self, headers: List[str]) -> str:
        """Создает заголовок таблицы в формате Jira"""
        header_row = "| " + " | ".join(headers) + " |"
        separator_row = "|" + "|".join([" --- " for _ in headers]) + "|"
        return header_row + "\n" + separator_row + "\n"

    def get_table_line(self, cells: List[str]) -> str:
        """Создает строку таблицы в формате Jira"""
        return "| " + " | ".join(cells) + " |\n"

    def add_comment_to_issue(self, issue_id: str, body: str) -> None:
        """Добавляет комментарий к задаче"""
        # Реализация добавления комментария
        print(f"Adding comment to issue {issue_id}: {body}")

    def create_issue(self, issue: Issue) -> str:
        """Создает новую задачу"""
        # Реализация создания задачи
        print(f"Creating issue: {issue.summary}")
        return "ISSUE-123"  # Возвращаем ID созданной задачи

    def update_issue_params(self, issue_id: str, issue: Issue) -> None:
        """Обновляет параметры задачи"""
        # Реализация обновления задачи
        print(f"Updating issue {issue_id} with params")


class IssueManagerInterface:
    """Интерфейс для менеджера задач"""

    def create_issue(self, project: str) -> 'IssueBuilder':
        """Создает новую задачу"""
        return IssueBuilder()


class IssueBuilder:
    """Builder для создания задач"""

    def __init__(self):
        self.issue = Issue()

    def set_type_task(self, task_type: str) -> 'IssueBuilder':
        self.issue.type_task = task_type
        return self

    def set_summary(self, summary: str) -> 'IssueBuilder':
        self.issue.summary = summary
        return self

    def set_description(self, description: str) -> 'IssueBuilder':
        self.issue.description = description
        return self

    def set_assignee(self, assignee: str) -> 'IssueBuilder':
        self.issue.assignee = assignee
        return self

    def set_creator(self, creator: str) -> 'IssueBuilder':
        self.issue.creator = creator
        return self

    def set_priority(self, priority: str) -> 'IssueBuilder':
        self.issue.priority = priority
        return self

    def add_watcher(self, watcher: str) -> 'IssueBuilder':
        self.issue.watchers.append(watcher)
        return self

    def build(self) -> Issue:
        return self.issue


class FrontendUrlGenerator:
    """Генератор URL для фронтенда"""

    def get_link_to_entity(self, entity) -> str:
        """Генерирует ссылку на сущность"""
        # Простая реализация
        return f"https://frontend.example.com/{entity.__class__.__name__.lower()}/{getattr(entity, 'id', 'unknown')}"

    def get_link_to_class_name(self, class_name: str, entity_id: str) -> str:
        """Генерирует ссылку по имени класса и ID"""
        return f"https://frontend.example.com/{class_name.lower()}/{entity_id}"


class JiraManager:
    """Основной класс для работы с Jira (аналог YoutrackManager)"""

    def __init__(self, jira_api: JiraApi, issue_manager: IssueManagerInterface,
                 frontend_url_generator: FrontendUrlGenerator):
        self.api = jira_api
        self.issue_manager = issue_manager
        self.frontend_url_generator = frontend_url_generator

    @staticmethod
    def get_link(url: str, name: str) -> str:
        """Создает HTML ссылку"""
        return f'<a href="{url}">{name}</a>'

    @staticmethod
    def get_md_link(url: str, name: str) -> str:
        """Создает Markdown ссылку"""
        return f'[{name}]({url})'

    @staticmethod
    def wrap_in_html(string: str) -> str:
        """Оборачивает строку в HTML теги"""
        return f'<html>{string}</html>'

    @staticmethod
    def wrap_in_code(string: str, language: str = 'json') -> str:
        """Оборачивает строку в блок кода"""
        return f'```{language}\n{string}\n```'

    def array_to_formatted_string(self, array: Union[list, dict]) -> str:
        """Преобразует массив в отформатированную строку"""
        result = ''

        if isinstance(array, dict):
            items = array.items()
        else:
            items = enumerate(array)

        for key, value in items:
            if isinstance(value, (list, dict)):
                if not isinstance(key, int):
                    result += f'<strong>{key}</strong>: {self.array_to_formatted_string(value)}'
                else:
                    result += self.array_to_formatted_string(value)
            else:
                if not isinstance(key, int):
                    result += f'<strong>{key}</strong>: {value}<br>'
                else:
                    result += f'<li>{value}</li>'

        return result

    def all_formats_to_string(self, value: Any) -> str:
        """Преобразует различные типы данных в строку для отображения в Jira"""
        if isinstance(value, (list, dict)):
            new_value = self.array_to_formatted_string(value)
        elif isinstance(value, bool):
            new_value = 'true' if value else 'false'
        else:
            new_value = str(value)

        return self.wrap_in_html(new_value)

    def add_comment_for_limits(self, external_offer, product, changes: List[Dict]) -> None:
        """Добавляет комментарий о лимитах"""
        if hasattr(external_offer, 'issue') and external_offer.issue:
            issue_id = external_offer.issue
            body = self.api.get_table_header([
                ' Product limit ',
                ' old values ',
                ' new values ',
            ])

            for key, value in changes.items():
                # Обработка изменений лимитов
                link = self.frontend_url_generator.get_link_to_entity(product)
                body += self.api.get_table_line([
                    self.get_link(link, product.name),
                    self.all_formats_to_string(value[0]),
                    self.all_formats_to_string(value[1]),
                ])

            self.api.add_comment_to_issue(issue_id, body)

    def add_comment_for_started_campaigns(self, products: List[List[Dict]]) -> None:
        """Добавляет комментарий о запущенных кампаниях"""
        for row in products:
            if not row[0].get('last_stopped_at'):
                time_diff = '0'
            else:
                time_diff = self.timestamp_range_to_compact_format(
                    row[0]['last_stopped_at'], int(time.time())
                )

            issue_id = row[0]['issue_id']
            body = f'Relaunched campaigns after domain block: (stop time: {time_diff})\n'

            for campaign in row:
                link = self.frontend_url_generator.get_link_to_class_name(
                    'Campaign', campaign['campaign_id']
                )
                body += f"[{campaign['campaign_id']}]({link}) - {campaign['campaign_name']}\n"

            self.api.add_comment_to_issue(issue_id, body)

    def add_comment_for_stopped_campaigns(self, products: List[List[Dict]]) -> None:
        """Добавляет комментарий об остановленных кампаниях"""
        for row in products:
            issue_id = row[0]['issue_id']
            body = 'Campaigns stopped by domain block:\n'

            for campaign in row:
                link = self.frontend_url_generator.get_link_to_class_name(
                    'Campaign', campaign['campaign_id']
                )
                body += f"[{campaign['campaign_id']}]({link}) - {campaign['campaign_name']}\n"

            self.api.add_comment_to_issue(issue_id, body)

    def create_issue_from_product(self, product, creator, campaigns: List = None) -> Issue:
        """Создает задачу на основе продукта"""
        advertiser = product.advertiser
        current_date = datetime.now()

        if campaigns is None or len(campaigns) < 0:
            campaigns = product.campaigns

        campaign_ids = [campaign.id for campaign in campaigns]

        # Формирование описания кампаний
        campaigns_text = []
        for campaign in campaigns:
            # Здесь должна быть логика получения rates
            rates_text = self._get_rates_text(campaign, current_date)
            campaign_text = self.campaign_to_string(campaign)
            if rates_text:
                campaign_text += f"\n{rates_text}\n"
            campaigns_text.append(campaign_text)

        advertiser_link = self.frontend_url_generator.get_link_to_entity(advertiser)
        product_link = self.frontend_url_generator.get_link_to_entity(product)
        category_names = ', '.join([category.name for category in product.categories])
        settings = self.get_product_settings_string(product)

        rates = ''
        if product.revenue_type != RevenueTypeEnum.PARSED:
            rates_text = self._get_product_rates_text(product)
            rates = f'* Rates: \n{rates_text}\n'

        limits_text = self._get_limits_text(product)
        limits = f'* Limits: \n{limits_text}\n' if limits_text else ''

        data = [
            creator.name,
            advertiser_link,
            product_link,
            product.preview_url,
            product.kpi,
            category_names,
            RevenueTypeEnum.LABELS.get(product.revenue_type, ''),
            settings,
            rates,
            limits,
            '\n'.join(campaigns_text),
            ','.join(map(str, campaign_ids)),
        ]

        description = Issue.get_product_template_md().format(*data)

        issue = self.issue_manager.create_issue(Issue.PROJECT_OPTIMIZATION) \
            .set_type_task(Issue.TASK_ADV) \
            .set_summary(f"{advertiser.id} | {advertiser.name} - {product.name} ({product.id})") \
            .set_description(description) \
            .add_watcher(YouTrackUserEnum.D_PACHKO.value) \
            .set_creator(creator) \
            .set_priority('Major' if advertiser.is_new else 'Normal') \
            .build()

        if hasattr(creator, 'youtrack_login') and creator.youtrack_login:
            issue.watchers.append(creator.youtrack_login)

        return issue

    def create_issue_from_advertiser(self, advertiser, creator) -> Issue:
        """Создает задачу на основе рекламодателя"""
        advertiser_link = self.frontend_url_generator.get_link_to_entity(advertiser)
        geos = [gg.name for gg in advertiser.geo_groups]
        work_models = [wm.name for wm in advertiser.work_models]
        traffic_types = [tt.name for tt in advertiser.traffic_types]
        revenue_type = advertiser.revenue_type
        monthly_spend = advertiser.monthly_spend
        manager_comment = advertiser.manager_comment

        separator = ', '
        data = []
        template = ''
        search_query = ''

        if advertiser.department == AdvertiserDepartmentTypeEnum.SSP:
            template = Issue.get_ssp_advertiser_template()
            search_query = Issue.SSP_ADVERTISER_TO_REPLACE

            data = [
                creator.name,
                advertiser_link,
                RevenueTypeEnum.LABELS.get(revenue_type),
                monthly_spend,
                manager_comment,
            ]
        else:
            template = Issue.get_advertiser_template()
            search_query = Issue.ADVERTISER_TO_REPLACE

            data = [
                creator.name,
                advertiser_link,
                separator.join(geos),
                separator.join(work_models),
                separator.join(traffic_types),
                advertiser.landing_info,
                AdvertiserTypeEnum.LABELS.get(advertiser.type, ''),
            ]

        description = template.format(*data)

        issue = self.issue_manager.create_issue(Issue.PROJECT_OPTIMIZATION) \
            .set_type_task(Issue.TASK_ADV) \
            .set_summary(f"{advertiser.id} | {advertiser.name}") \
            .set_description(description) \
            .set_assignee(
                YouTrackUserEnum.V_KALMYKOV.value if advertiser.department == AdvertiserDepartmentTypeEnum.SSP
                else YouTrackUserEnum.E_MALIHINA.value
            ) \
            .set_creator(creator) \
            .build()

        if hasattr(creator, 'youtrack_login') and creator.youtrack_login:
            issue.watchers.append(creator.youtrack_login)

        return issue

    def create_issue_from_zone(self, dto: ZoneYoutrackIssueDto, creator) -> Issue:
        """Создает задачу на основе зоны"""
        return self.issue_manager.create_issue(Issue.PROJECT_OPTIMIZATION) \
            .set_type_task(Issue.TASK_PUB) \
            .set_summary(dto.summary) \
            .set_description(dto.description) \
            .set_creator(creator) \
            .build()

    def update_issue_params(self, issue_id: str, issue: Issue) -> None:
        """Обновляет параметры задачи"""
        self.api.update_issue_params(issue_id, issue)

    def send_issue_to_jira(self, issue: Issue) -> str:
        """Отправляет задачу в Jira"""
        return self.api.create_issue(issue)

    def rate_to_string(self, rate) -> str:
        """Преобразует rate в строку"""
        value = ''
        if hasattr(rate, 'price'):
            value = rate.price

        return f"  * {rate.type}: {', '.join(rate.geo)} - {value} {rate.currency}\n"

    def limit_to_string(self, limit) -> str:
        """Преобразует limit в строку"""
        return f"  * {limit.type_title}: {limit.period_name} - {limit.value}\n"

    def campaign_to_string(self, campaign) -> str:
        """Преобразует campaign в строку"""
        return f"* {self.get_md_link(self.frontend_url_generator.get_link_to_entity(campaign), f'{campaign.id} {campaign.name}')}"

    def get_product_settings_string(self, product) -> str:
        """Получает строку настроек продукта"""
        settings = '* Settings: \n'
        settings += f'  - With preland: {"Yes" if product.is_with_preland else "No"}\n'
        settings += f'  - Direct link: {"Yes" if product.is_direct_link else "No"}\n'
        settings += f'  - Without direct link: {"Yes" if product.is_without_direct_link else "No"}\n'
        return settings

    def timestamp_range_to_compact_format(self, timestamp_start: int, timestamp_end: int) -> str:
        """Преобразует временной диапазон в компактный формат"""
        diff = timestamp_end - timestamp_start
        days = diff // (24 * 60 * 60)
        diff -= days * 24 * 60 * 60
        hours = diff // (60 * 60)
        diff -= hours * 60 * 60
        minutes = diff // 60
        diff -= minutes * 60
        seconds = diff

        time_str = ''
        if days > 0:
            time_str += f'{days}d '
        if hours > 0:
            time_str += f'{hours}h '
        if minutes > 0:
            time_str += f'{minutes}m '
        if seconds > 0:
            time_str += f'{seconds}s'

        return time_str

    def _get_rates_text(self, campaign, current_date) -> str:
        """Получает текст rates для кампании"""
        # Здесь должна быть логика получения rates
        return ""

    def _get_product_rates_text(self, product) -> str:
        """Получает текст rates для продукта"""
        # Здесь должна быть логика получения rates продукта
        return ""

    def _get_limits_text(self, product) -> str:
        """Получает текст limits для продукта"""
        limits = [self.limit_to_string(limit) for limit in product.limits]
        return '\n'.join(limits)


# Пример использования
if __name__ == "__main__":
    # Создание экземпляров
    jira_api = JiraApi("https://your-jira-instance.com", "username", "api_token")
    issue_manager = IssueManagerInterface()
    frontend_generator = FrontendUrlGenerator()

    # Создание менеджера
    jira_manager = JiraManager(jira_api, issue_manager, frontend_generator)

    print("Jira Integration Manager создан успешно!")
