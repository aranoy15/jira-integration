"""
Kafka Consumer Client для чтения сообщений из Kafka
"""

import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from kafka import KafkaConsumer
from kafka.errors import KafkaError


class KafkaConsumerClient:
    """Клиент для чтения сообщений из Kafka"""

    def __init__(
        self,
        bootstrap_servers: List[str] = None,
        client_id: str = "jira-kafka-consumer",
        group_id: str = "jira-consumer-group",
        **kwargs
    ):
        """
        Инициализация Kafka Consumer

        Args:
            bootstrap_servers: Список серверов Kafka (по умолчанию ['localhost:9092'])
            client_id: Идентификатор клиента
            group_id: ID группы консьюмеров
            **kwargs: Дополнительные параметры для KafkaConsumer
        """
        self.bootstrap_servers = bootstrap_servers or ['localhost:9092']
        self.client_id = client_id
        self.group_id = group_id

        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Параметры по умолчанию
        default_config = {
            'bootstrap_servers': self.bootstrap_servers,
            'client_id': self.client_id,
            'group_id': self.group_id,
            'value_deserializer': lambda x: json.loads(x.decode('utf-8')),
            'key_deserializer': lambda x: x.decode('utf-8') if x else None,
            'auto_offset_reset': 'latest',  # Начинаем с последних сообщений
            'enable_auto_commit': True,     # Автоматическое подтверждение
            'auto_commit_interval_ms': 1000,
            'session_timeout_ms': 30000,
            'heartbeat_interval_ms': 10000,
            'max_poll_records': 500,       # Максимум сообщений за один poll
            'consumer_timeout_ms': 1000,   # Таймаут ожидания сообщений
        }

        # Объединяем параметры по умолчанию с переданными
        config = {**default_config, **kwargs}

        try:
            self.consumer = KafkaConsumer(**config)
            self.logger.info(f"✅ Kafka Consumer инициализирован: {self.bootstrap_servers}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации Kafka Consumer: {e}")
            raise

    def subscribe(self, topics: List[str]):
        """
        Подписка на топики

        Args:
            topics: Список топиков для подписки
        """
        try:
            self.consumer.subscribe(topics)
            self.logger.info(f"📡 Подписка на топики: {topics}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка подписки на топики: {e}")
            raise

    def poll(self, timeout_ms: int = 1000) -> Dict[str, List[Any]]:
        """
        Получение сообщений из топиков

        Args:
            timeout_ms: Таймаут ожидания сообщений в миллисекундах

        Returns:
            Dict с сообщениями по топикам
        """
        try:
            message_pack = self.consumer.poll(timeout_ms=timeout_ms)

            if message_pack:
                self.logger.info(f"📨 Получено сообщений: {sum(len(msgs) for msgs in message_pack.values())}")

            return message_pack

        except Exception as e:
            self.logger.error(f"❌ Ошибка получения сообщений: {e}")
            return {}

    def get_messages(
        self,
        topics: List[str],
        count: int = 10,
        timeout_ms: int = 5000
    ) -> List[Dict[str, Any]]:
        """
        Получение определенного количества сообщений

        Args:
            topics: Список топиков
            count: Количество сообщений для получения
            timeout_ms: Таймаут ожидания

        Returns:
            Список сообщений
        """
        messages = []

        try:
            # Подписываемся на топики
            self.subscribe(topics)

            # Получаем сообщения
            while len(messages) < count:
                message_pack = self.poll(timeout_ms)

                if not message_pack:
                    break

                # Обрабатываем сообщения
                for topic_partition, message_list in message_pack.items():
                    for message in message_list:
                        if len(messages) >= count:
                            break

                        message_data = {
                            'topic': topic_partition.topic,
                            'partition': topic_partition.partition,
                            'offset': message.offset,
                            'key': message.key,
                            'value': message.value,
                            'timestamp': message.timestamp,
                            'headers': dict(message.headers) if message.headers else {}
                        }

                        messages.append(message_data)

            self.logger.info(f"📨 Получено {len(messages)} сообщений")
            return messages

        except Exception as e:
            self.logger.error(f"❌ Ошибка получения сообщений: {e}")
            return []

    def consume_messages(
        self,
        topics: List[str],
        message_handler: Callable[[Dict[str, Any]], None],
        timeout_ms: int = 1000
    ):
        """
        Непрерывное потребление сообщений с обработчиком

        Args:
            topics: Список топиков
            message_handler: Функция для обработки сообщений
            timeout_ms: Таймаут ожидания сообщений
        """
        try:
            # Подписываемся на топики
            self.subscribe(topics)

            self.logger.info(f"🔄 Начинаем потребление сообщений из топиков: {topics}")

            while True:
                message_pack = self.poll(timeout_ms)

                if message_pack:
                    # Обрабатываем каждое сообщение
                    for topic_partition, message_list in message_pack.items():
                        for message in message_list:
                            message_data = {
                                'topic': topic_partition.topic,
                                'partition': topic_partition.partition,
                                'offset': message.offset,
                                'key': message.key,
                                'value': message.value,
                                'timestamp': message.timestamp,
                                'headers': dict(message.headers) if message.headers else {}
                            }

                            try:
                                message_handler(message_data)
                            except Exception as e:
                                self.logger.error(f"❌ Ошибка обработки сообщения: {e}")

        except KeyboardInterrupt:
            self.logger.info("⏹️ Остановка потребления сообщений")
        except Exception as e:
            self.logger.error(f"❌ Ошибка потребления сообщений: {e}")

    def get_latest_messages(
        self,
        topic: str,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Получение последних сообщений из топика

        Args:
            topic: Название топика
            count: Количество сообщений

        Returns:
            Список последних сообщений
        """
        try:
            # Создаем временный consumer с offset reset на earliest
            temp_consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset='latest',
                enable_auto_commit=False,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                key_deserializer=lambda x: x.decode('utf-8') if x else None,
                consumer_timeout_ms=1000
            )

            messages = []
            message_count = 0

            for message in temp_consumer:
                if message_count >= count:
                    break

                message_data = {
                    'topic': message.topic,
                    'partition': message.partition,
                    'offset': message.offset,
                    'key': message.key,
                    'value': message.value,
                    'timestamp': message.timestamp,
                    'headers': dict(message.headers) if message.headers else {}
                }

                messages.append(message_data)
                message_count += 1

            temp_consumer.close()
            self.logger.info(f"📨 Получено {len(messages)} последних сообщений из топика '{topic}'")
            return messages

        except Exception as e:
            self.logger.error(f"❌ Ошибка получения последних сообщений: {e}")
            return []

    def list_topics(self) -> List[str]:
        """
        Получение списка доступных топиков

        Returns:
            Список названий топиков
        """
        try:
            metadata = self.consumer.list_consumer_group_offsets()
            topics = self.consumer.topics()
            topic_list = list(topics)

            self.logger.info(f"📋 Найдено топиков: {len(topic_list)}")
            return topic_list

        except Exception as e:
            self.logger.error(f"❌ Ошибка получения списка топиков: {e}")
            return []

    def close(self):
        """Закрытие соединения с Kafka"""
        try:
            self.consumer.close()
            self.logger.info("🔒 Kafka Consumer закрыт")
        except Exception as e:
            self.logger.error(f"❌ Ошибка при закрытии Consumer: {e}")

    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка контекстного менеджера"""
        self.close()


