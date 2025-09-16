"""
Простой Kafka клиент для Jira задач (issues)
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from kafka_producer import KafkaProducerClient


class JiraKafkaProducer:
    """Простой producer для отправки Jira задач в Kafka"""

    def __init__(
        self,
        bootstrap_servers: List[str] = None,
        client_id: str = "jira-kafka-client"
    ):
        """
        Инициализация клиента

        Args:
            bootstrap_servers: Список серверов Kafka
            client_id: Идентификатор клиента
        """
        self.producer = KafkaProducerClient(
            bootstrap_servers=bootstrap_servers,
            client_id=client_id
        )

        # Топик для задач
        self.issues_topic = 'jira-issues'

    def send_issue_event(
        self,
        issue_data: Dict[str, Any],
        event_type: str = 'created',
        issue_key: Optional[str] = None
    ) -> bool:
        """
        Отправка события по задаче

        Args:
            issue_data: Данные задачи
            event_type: Тип события (created, updated, deleted, etc.)
            issue_key: Ключ задачи (для партиционирования)

        Returns:
            bool: True если событие отправлено успешно
        """
        event_message = {
            'event_type': event_type,
            'issue': issue_data,
            'timestamp': datetime.now().isoformat(),
            'source': 'jira-integration'
        }

        key = issue_key or issue_data.get('key')
        return self.producer.send_message(
            topic=self.issues_topic,
            message=event_message,
            key=key
        )

    def send_issues_batch(
        self,
        issues: List[Dict[str, Any]],
        event_type: str = 'created'
    ) -> Dict[str, int]:
        """
        Отправка пакета задач

        Args:
            issues: Список задач
            event_type: Тип события

        Returns:
            Dict с результатами отправки
        """
        events = []
        for issue in issues:
            event_message = {
                'event_type': event_type,
                'issue': issue,
                'timestamp': datetime.now().isoformat(),
                'source': 'jira-integration'
            }
            events.append(event_message)

        return self.producer.send_batch(self.issues_topic, events, key_field='key')

    def flush(self):
        """Принудительная отправка всех буферизованных сообщений"""
        self.producer.flush()

    def close(self):
        """Закрытие соединения"""
        self.producer.close()

    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка контекстного менеджера"""
        self.close()


