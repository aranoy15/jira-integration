import asyncio
import logging
import os
from typing import Dict

from lib.jira_client import JiraClient, JiraIssue
from lib.jira_provider import JiraProviderBase, JiraJsonProvider

class JiraIntegration:
    def __init__(self, jira_provider: JiraProviderBase):
        """Инициализация интеграции"""
        self.jira_client = None
        self.queue = asyncio.Queue(maxsize=1000)
        self.running = False
        self.stop_event = asyncio.Event()
        self.jira_provider = jira_provider

    async def start(self):
        """Запуск асинхронного сервиса"""

        self.jira_client = JiraClient(
            base_url=os.getenv('JIRA_BASE_URL'),
            username=os.getenv('JIRA_USERNAME'),
            api_token=os.getenv('JIRA_API_TOKEN'),
            password=os.getenv('JIRA_PASSWORD'),
            auth_type=os.getenv('JIRA_AUTH_TYPE')
        )

        self.running = True
        async with self.jira_client:
            await self.run()

    async def run(self):
        """Запуск интеграции"""
        logging.info("Starting Jira integration")
        self.running = True

        tasks = [
            asyncio.create_task(self.jira_poller()),
            asyncio.create_task(self.issue_processor()),
            asyncio.create_task(self.monitor_queue()),
        ]

        try:
            await asyncio.gather(*tasks)
        except (KeyboardInterrupt, asyncio.CancelledError):
            logging.info("Received interrupt signal, stopping...")
            self.running = False
            self.stop_event.set()
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logging.error(f"Error: {e}")
            self.running = False
            self.stop_event.set()
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)


    async def jira_poller(self):
        """Опрос Jira"""
        logging.info("Starting Jira poller")
        while self.running:
            try:
                issues = self.jira_provider.get_issues()
                logging.info(f"Получено {len(issues)} задач из провайдера")
                if issues:
                    logging.info(f"Первая задача: {issues[0]}")

                for issue in issues:
                    await self.queue.put({
                        'type': 'issue_update',
                        'data': issue
                    })
                    logging.info(f"Задача {issue.get('key', 'N/A')} добавлена в очередь")

            except Exception as e:
                logging.error(f"Ошибка в jira_poller: {type(e).__name__}: {e}")
                import traceback
                logging.error(f"Traceback: {traceback.format_exc()}")

            await asyncio.sleep(60)


    async def issue_processor(self):
        """Обработка задач из очереди"""
        logging.info("Starting issue processor")

        while self.running:
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                if item['type'] == 'issue_update':
                    raw_issue = item['data']
                    await self.handle_issue(raw_issue)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                logging.info("Issue processor cancelled")
                break
            except Exception as e:
                logging.error(f"Error processing issue: {type(e).__name__}: {e}")
                import traceback
                logging.error(f"Traceback: {traceback.format_exc()}")
                await asyncio.wait_for(self.stop_event.wait(), timeout=1.0)

    async def handle_issue(self, raw_issue: Dict):
        """
        Обработка задачи

        Args:
            raw_issue: Сырая задача
        """
        try:
            issue_key = raw_issue.get('key', 'UNKNOWN')
            fields = raw_issue.get('fields', {})

            logging.info(f"Processing issue: {issue_key}")

            projects = await self.jira_client.get_projects()
            if not projects:
                logging.error("Нет доступных проектов в Jira")
                return

            project_key = projects[0]['key']
            logging.info(f"Using project: {project_key}")

            project_info = await self.jira_client.get_project(project_key)
            issue_types = project_info.get('issueTypes', [])

            issue_type = issue_types[0]['name'] if issue_types else 'Task'
            logging.info(f"Using issue type: {issue_type}")

            issue = JiraIssue(
                project_key=project_key,
                issue_type=issue_type,
                summary=fields.get('summary', 'No summary'),
                description=fields.get('description', 'No description')
            )

            logging.info(f"Creating issue with data: {issue}")
            issue_key = await self.jira_client.create_issue(issue)
            logging.info(f"Issue created: {issue_key}")

        except Exception as e:
            logging.error(f"Error creating issue: {type(e).__name__}: {e}")
            logging.error(f"Raw issue data: {raw_issue}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")

    async def monitor_queue(self):
        """Мониторинг очереди"""
        logging.info("Starting queue monitor")
        while self.running:
            try:
                size = self.queue.qsize()
                logging.info(f"Queue size: {size}")

                try:
                    await asyncio.wait_for(self.stop_event.wait(), timeout=1.0)
                    break
                except asyncio.TimeoutError:
                    continue

            except asyncio.CancelledError:
                logging.info("Queue monitor cancelled")
                break
            except Exception as e:
                logging.error(f"Error checking queue size: {e}")
                await asyncio.sleep(1.0)


    async def stop(self):
        """Остановка интеграции"""
        logging.info("Stopping Jira integration")
        self.running = False
        self.stop_event.set()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    json_file_path = os.getenv('JIRA_JSON_FILE_PATH', 'data/sample_data.json')
    jira_provider = JiraJsonProvider(json_file_path=json_file_path)

    jira_integration = JiraIntegration(jira_provider=jira_provider)
    await jira_integration.start()

if __name__ == "__main__":
    asyncio.run(main())
