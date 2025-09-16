# Kafka Integration для Jira

Простая интеграция между Jira и Apache Kafka для отправки и получения событий по задачам.

## 📁 Структура файлов

```
kafka/
├── docker-compose-kafka.yaml          # Конфигурация Kafka с Docker
├── kafka_producer.py                  # Базовый Kafka Producer клиент
├── kafka_consumer.py                  # Базовый Kafka Consumer клиент
├── jira_kafka_producer.py             # Producer для Jira задач
├── jira_kafka_consumer.py             # Consumer для Jira задач
└── README.md                          # Эта документация
```

## 🚀 Быстрый старт

### 1. Запуск Kafka

```bash
# Запуск Kafka с Docker Compose
docker compose -f docker-compose-kafka.yaml up -d
```

### 2. Установка зависимостей

```bash
pip install -r ../requirements.txt
```

### 3. Проверка работы

Откройте Kafka UI: http://localhost:8081

## 📚 Компоненты

### KafkaProducerClient

Базовый клиент для отправки сообщений в Kafka.

**Особенности:**
- ✅ Автоматическая сериализация JSON
- ✅ Поддержка партиционирования по ключу
- ✅ Надежная доставка (acks='all')
- ✅ Автоматические повторы при ошибках
- ✅ Сжатие сообщений (gzip)
- ✅ Контекстный менеджер
- ✅ Пакетная отправка сообщений

**Пример использования:**

```python
from kafka_producer import KafkaProducerClient

# Создание клиента
with KafkaProducerClient() as producer:
    # Отправка одного сообщения
    message = {'user_id': '123', 'action': 'login'}
    producer.send_message('user-events', message, key='123')

    # Пакетная отправка
    messages = [
        {'user_id': '123', 'action': 'page_view'},
        {'user_id': '124', 'action': 'page_view'},
    ]
    producer.send_batch('user-events', messages, key_field='user_id')
```

### KafkaConsumerClient

Базовый клиент для чтения сообщений из Kafka.

**Особенности:**
- ✅ Автоматическая десериализация JSON
- ✅ Поддержка групп консьюмеров
- ✅ Автоматическое подтверждение сообщений
- ✅ Получение последних сообщений
- ✅ Непрерывное потребление
- ✅ Контекстный менеджер

**Пример использования:**

```python
from kafka_consumer import KafkaConsumerClient

# Создание клиента
with KafkaConsumerClient() as consumer:
    # Получение сообщений
    messages = consumer.get_messages(['test-topic'], count=10)

    # Непрерывное потребление
    def message_handler(message_data):
        consumer.logger.info(f"Получено: {message_data['value']}")

    consumer.consume_messages(['test-topic'], message_handler)
```

### JiraKafkaProducer

Специализированный producer для отправки Jira задач.

**Поддерживаемые операции:**
- 📝 Отправка одной задачи
- 📦 Пакетная отправка задач
- 🔄 Различные типы событий (created, updated, deleted)

**Пример использования:**

```python
from jira_kafka_producer import JiraKafkaProducer

with JiraKafkaProducer() as producer:
    # Отправка одной задачи
    issue_data = {
        'key': 'PROJ-123',
        'summary': 'Тестовая задача',
        'status': 'In Progress',
        'assignee': 'user@example.com',
        'priority': 'High'
    }
    producer.send_issue_event(issue_data, event_type='created')

    # Пакетная отправка
    issues = [
        {'key': 'PROJ-124', 'summary': 'Вторая задача'},
        {'key': 'PROJ-125', 'summary': 'Третья задача'}
    ]
    producer.send_issues_batch(issues, event_type='created')
```

### JiraKafkaConsumer

Специализированный consumer для чтения Jira задач.

**Поддерживаемые операции:**
- 📝 Получение событий по задачам
- 🔍 Фильтрация по ключу задачи
- 📨 Получение последних событий
- 🔄 Непрерывное потребление событий

**Пример использования:**

```python
from jira_kafka_consumer import JiraKafkaConsumer

with JiraKafkaConsumer() as consumer:
    # Получение последних событий
    events = consumer.get_latest_issue_events(count=10)

    # Получение событий по конкретной задаче
    specific_events = consumer.get_issue_events(count=10, issue_key='PROJ-123')

    # Непрерывное потребление
    def issue_handler(message_data):
        event_data = message_data.get('value', {})
        issue_data = event_data.get('issue', {})
        consumer.logger.info(f"Событие по задаче {issue_data.get('key')}: {event_data.get('event_type')}")

    consumer.consume_issue_events(issue_handler)
```

## 🔧 Конфигурация

### Kafka Producer настройки

```python
producer_config = {
    'bootstrap_servers': ['localhost:9092'],
    'client_id': 'jira-kafka-producer',
    'acks': 'all',                    # Ждем подтверждения от всех реплик
    'retries': 3,                     # Количество попыток
    'retry_backoff_ms': 1000,         # Задержка между попытками
    'request_timeout_ms': 30000,      # Таймаут запроса
    'compression_type': 'gzip',       # Сжатие сообщений
}
```

### Kafka Consumer настройки

```python
consumer_config = {
    'bootstrap_servers': ['localhost:9092'],
    'client_id': 'jira-kafka-consumer',
    'group_id': 'jira-consumer-group',
    'auto_offset_reset': 'latest',   # Начинаем с последних сообщений
    'enable_auto_commit': True,       # Автоматическое подтверждение
    'session_timeout_ms': 30000,     # Таймаут сессии
    'max_poll_records': 500,          # Максимум сообщений за poll
}
```

### Топик Kafka

По умолчанию используется топик `jira-issues` для всех событий по задачам.

## 📊 Мониторинг

### Kafka UI

Откройте http://localhost:8081 для веб-интерфейса управления Kafka.

### Логирование

Все клиенты используют стандартное логирование Python:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Проверка топиков

```bash
# Список топиков
docker exec -it kafka-broker kafka-topics --list --bootstrap-server localhost:9092

# Создание топика для Jira задач
docker exec -it kafka-broker kafka-topics --create --topic jira-issues --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Просмотр сообщений
docker exec -it kafka-broker kafka-console-consumer --topic jira-issues --bootstrap-server localhost:9092 --from-beginning
```

## 🛠️ Разработка

### Структура сообщений

Все сообщения имеют единую структуру:

```json
{
  "event_type": "created",
  "issue": {
    "key": "PROJ-123",
    "summary": "Тестовая задача",
    "status": "In Progress",
    "assignee": "user@example.com",
    "priority": "High"
  },
  "timestamp": "2024-01-01T12:00:00",
  "source": "jira-integration"
}
```

### Обработка ошибок

Все клиенты включают обработку ошибок:

- ✅ Повторы при временных ошибках
- ✅ Логирование всех ошибок
- ✅ Graceful degradation
- ✅ Контекстные менеджеры для автоматического закрытия

### Тестирование

Для тестирования создайте отдельный тестовый файл:

```python
# test_kafka_integration.py
from kafka_producer import KafkaProducerClient
from kafka_consumer import KafkaConsumerClient
from jira_kafka_producer import JiraKafkaProducer
from jira_kafka_consumer import JiraKafkaConsumer

def test_basic_producer():
    """Тест базового producer"""
    with KafkaProducerClient() as producer:
        message = {'test': 'data', 'timestamp': '2024-01-01'}
        success = producer.send_message('test-topic', message)
        print(f"Producer test: {'✅ Success' if success else '❌ Failed'}")

def test_basic_consumer():
    """Тест базового consumer"""
    with KafkaConsumerClient() as consumer:
        messages = consumer.get_messages(['test-topic'], count=5)
        print(f"Consumer test: Found {len(messages)} messages")

def test_jira_producer():
    """Тест Jira producer"""
    with JiraKafkaProducer() as producer:
        issue_data = {
            'key': 'TEST-123',
            'summary': 'Test Issue',
            'status': 'To Do'
        }
        success = producer.send_issue_event(issue_data)
        print(f"Jira Producer test: {'✅ Success' if success else '❌ Failed'}")

def test_jira_consumer():
    """Тест Jira consumer"""
    with JiraKafkaConsumer() as consumer:
        events = consumer.get_latest_issue_events(count=5)
        print(f"Jira Consumer test: Found {len(events)} events")

if __name__ == "__main__":
    print("🧪 Running Kafka integration tests...")
    test_basic_producer()
    test_basic_consumer()
    test_jira_producer()
    test_jira_consumer()
    print("✅ All tests completed!")
```

Запуск тестов:
```bash
python test_kafka_integration.py
```

## 🔒 Безопасность

- 🔐 API токены хранятся в переменных окружения
- 🚫 `.env` файлы исключены из Git
- 🔒 Kafka работает в изолированной сети
- 📝 Все операции логируются

## 📈 Производительность

- ⚡ Пакетная отправка сообщений
- 🗜️ Сжатие сообщений (gzip)
- 🔄 Асинхронная обработка
- 📊 Мониторинг производительности через Kafka UI

## 🆘 Устранение неполадок

### Kafka недоступен

```bash
# Проверка статуса контейнеров
docker compose -f docker-compose-kafka.yaml ps

# Просмотр логов
docker compose -f docker-compose-kafka.yaml logs -f kafka
```

### Ошибки подключения

1. Проверьте, что Kafka запущен: `docker ps`
2. Проверьте порты: `netstat -tlnp | grep 9092`
3. Проверьте переменные окружения
4. Проверьте логи приложения

### Проблемы с топиками

```bash
# Пересоздание топика
docker exec -it kafka-broker kafka-topics --delete --topic jira-issues --bootstrap-server localhost:9092
docker exec -it kafka-broker kafka-topics --create --topic jira-issues --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

## 📋 Доступные сервисы

| Сервис | URL | Описание |
|--------|-----|----------|
| Kafka Broker | localhost:9092 | Основной брокер сообщений |
| Kafka UI | http://localhost:8081 | Веб-интерфейс управления |

## 🛑 Остановка

```bash
# Остановка Kafka
docker compose -f docker-compose-kafka.yaml down

# Остановка с удалением данных
docker compose -f docker-compose-kafka.yaml down -v
```

## 📋 Требования

- Docker
- Docker Compose
- Python 3.7+
- Минимум 2GB RAM
