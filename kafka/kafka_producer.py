"""
Kafka Producer Client для записи сообщений в Kafka
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError


class KafkaProducerClient:
    """Клиент для записи сообщений в Kafka"""

    def __init__(
        self,
        bootstrap_servers: List[str] = None,
        client_id: str = "jira-kafka-producer",
        **kwargs
    ):
        """
        Инициализация Kafka Producer

        Args:
            bootstrap_servers: Список серверов Kafka (по умолчанию ['localhost:9092'])
            client_id: Идентификатор клиента
            **kwargs: Дополнительные параметры для KafkaProducer
        """
        self.bootstrap_servers = bootstrap_servers or ['localhost:9092']
        self.client_id = client_id

        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Параметры по умолчанию
        default_config = {
            'bootstrap_servers': self.bootstrap_servers,
            'client_id': self.client_id,
            'value_serializer': lambda x: json.dumps(x, ensure_ascii=False).encode('utf-8'),
            'key_serializer': lambda x: x.encode('utf-8') if x else None,
            'acks': 'all',  # Ждем подтверждения от всех реплик
            'retries': 3,   # Количество попыток повторной отправки
            'retry_backoff_ms': 1000,  # Задержка между попытками
            'request_timeout_ms': 30000,  # Таймаут запроса
            'compression_type': 'gzip',  # Сжатие сообщений
        }

        # Объединяем параметры по умолчанию с переданными
        config = {**default_config, **kwargs}

        try:
            self.producer = KafkaProducer(**config)
            self.logger.info(f"✅ Kafka Producer инициализирован: {self.bootstrap_servers}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации Kafka Producer: {e}")
            raise

    def send_message(
        self,
        topic: str,
        message: Dict[str, Any],
        key: Optional[str] = None,
        partition: Optional[int] = None,
        timestamp_ms: Optional[int] = None
    ) -> bool:
        """
        Отправка сообщения в топик

        Args:
            topic: Название топика
            message: Сообщение для отправки
            key: Ключ сообщения (для партиционирования)
            partition: Номер партиции (если нужно указать конкретную)
            timestamp_ms: Временная метка сообщения

        Returns:
            bool: True если сообщение отправлено успешно
        """
        try:
            # Добавляем метаданные к сообщению
            enriched_message = {
                'data': message,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'producer_id': self.client_id,
                    'message_id': f"{self.client_id}_{datetime.now().timestamp()}"
                }
            }

            # Отправляем сообщение
            future = self.producer.send(
                topic=topic,
                value=enriched_message,
                key=key,
                partition=partition,
                timestamp_ms=timestamp_ms
            )

            # Ждем подтверждения
            record_metadata = future.get(timeout=10)

            self.logger.info(
                f"✅ Сообщение отправлено в топик '{topic}' "
                f"(партиция: {record_metadata.partition}, "
                f"offset: {record_metadata.offset})"
            )
            return True

        except KafkaError as e:
            self.logger.error(f"❌ Ошибка Kafka при отправке сообщения: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Неожиданная ошибка при отправке сообщения: {e}")
            return False

    def send_batch(
        self,
        topic: str,
        messages: List[Dict[str, Any]],
        key_field: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Отправка пакета сообщений

        Args:
            topic: Название топика
            messages: Список сообщений
            key_field: Поле для использования в качестве ключа

        Returns:
            Dict с результатами: {'success': count, 'failed': count}
        """
        results = {'success': 0, 'failed': 0}

        for message in messages:
            key = None
            if key_field and key_field in message:
                key = str(message[key_field])

            if self.send_message(topic, message, key=key):
                results['success'] += 1
            else:
                results['failed'] += 1

        self.logger.info(
            f"📦 Пакетная отправка завершена: "
            f"успешно: {results['success']}, "
            f"ошибок: {results['failed']}"
        )

        return results

    def flush(self):
        """Принудительная отправка всех буферизованных сообщений"""
        try:
            self.producer.flush()
            self.logger.info("🔄 Буфер очищен, все сообщения отправлены")
        except Exception as e:
            self.logger.error(f"❌ Ошибка при очистке буфера: {e}")

    def close(self):
        """Закрытие соединения с Kafka"""
        try:
            self.producer.close()
            self.logger.info("🔒 Kafka Producer закрыт")
        except Exception as e:
            self.logger.error(f"❌ Ошибка при закрытии Producer: {e}")

    def __enter__(self):
        """Поддержка контекстного менеджера"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка контекстного менеджера"""
        self.close()


