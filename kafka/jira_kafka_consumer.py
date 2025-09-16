"""
Простой Kafka Consumer для Jira задач (issues)
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from kafka_consumer import KafkaConsumerClient


class JiraKafkaConsumer:
    """Простой Consumer для чтения Jira задач из Kafka"""

    def __init__(
        self,
        bootstrap_servers: List[str] = None,
        client_id: str = "jira-kafka-consumer",
        group_id: str = "jira-consumer-group"
    ):
        """
        Инициализация Jira Consumer

        Args:
            bootstrap_servers: Список серверов Kafka
            client_id: Идентификатор клиента
            group_id: ID группы консьюмеров
        """
        self.consumer = KafkaConsumerClient(
            bootstrap_servers=bootstrap_servers,
            client_id=client_id,
            group_id=group_id
        )

        # Топик для задач
        self.issues_topic = 'jira-issues'

        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_issue_events(
        self,
        count: int = 10,
        issue_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Получение событий по задачам

        Args:
            count: Количество событий
            issue_key: Фильтр по ключу задачи (если указан)

        Returns:
            Список событий по задачам
        """
        try:
            messages = self.consumer.get_messages([self.issues_topic], count)

            # Фильтруем по ключу задачи если указан
            if issue_key:
                messages = [
                    msg for msg in messages
                    if msg.get('value', {}).get('issue', {}).get('key') == issue_key
                ]

            self.logger.info(f"📝 Получено {len(messages)} событий по задачам")
            return messages

        except Exception as e:
            self.logger.error(f"❌ Ошибка получения событий по задачам: {e}")
            return []

    def get_latest_issue_events(
        self,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Получение последних событий по задачам

        Args:
            count: Количество событий

        Returns:
            Список последних событий по задачам
        """
        try:
            messages = self.consumer.get_latest_messages(self.issues_topic, count)
            self.logger.info(f"📨 Получено {len(messages)} последних событий по задачам")
            return messages

        except Exception as e:
            self.logger.error(f"❌ Ошибка получения последних событий по задачам: {e}")
            return []

    def consume_issue_events(
        self,
        issue_handler: Callable[[Dict[str, Any]], None],
        issue_key: Optional[str] = None
    ):
        """
        Непрерывное потребление событий по задачам

        Args:
            issue_handler: Функция для обработки событий по задачам
            issue_key: Фильтр по ключу задачи
        """
        def filtered_handler(message_data):
            # Фильтруем по ключу задачи если указан
            if issue_key:
                issue_data = message_data.get('value', {}).get('issue', {})
                if issue_data.get('key') != issue_key:
                    return

            issue_handler(message_data)

        self.consumer.consume_messages([self.issues_topic], filtered_handler)

    def close(self):
        """Закрытие соединения"""
        self.consumer.close()

    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка контекстного менеджера"""
        self.close()


