from django.core.management.base import BaseCommand

from apps.integration import provider_config
from apps.integration.models import IntegrationProvider


class Command(BaseCommand):
    help = "Import Integration Providers from Django settings"

    def handle(self, *args, **options):
        providers = provider_config.INTEGRATION_PROVIDERS
        if not providers:
            self.stdout.write(self.style.WARNING("No providers found in settings."))
            return

        for item in providers:
            provider, created = IntegrationProvider.objects.update_or_create(
                name=item["name"],
                defaults={
                    "display_name": item["display_name"],
                    "auth_type": item["auth_type"],
                    "is_active": item["is_active"],
                    "config": item["config"],
                },
            )

            msg = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{msg}: {provider.name}"))

        self.stdout.write(self.style.SUCCESS("Import completed."))
