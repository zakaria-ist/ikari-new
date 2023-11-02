from django.apps import AppConfig


class AccountingConfig(AppConfig):
    name = 'accounting'

    def ready(self):
        import accounting.signals.fiscal_calendar_handler
