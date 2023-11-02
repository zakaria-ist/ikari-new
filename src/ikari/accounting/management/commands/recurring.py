from django.core.management.base import BaseCommand, CommandError
from accounting.cron_task import runRecurringTask


class Command(BaseCommand):
    def handle(self, *args, **options):
        runRecurringTask()
