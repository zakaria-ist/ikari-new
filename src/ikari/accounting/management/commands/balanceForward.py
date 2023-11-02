from django.core.management.base import BaseCommand, CommandError
from accounting.cron_task import updateAccountHistory


class Command(BaseCommand):
    def handle(self, *args, **options):
        updateAccountHistory()

