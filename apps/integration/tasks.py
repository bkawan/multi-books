import logging

from celery import shared_task
from django.utils import timezone

from apps.integration.models import CompanyIntegration
from apps.integration.selectors import get_qbo_customers, get_qbo_invoices
from apps.integration.services import create_or_update_qbo_customers, create_or_update_qbo_invoices

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_qbo_customers(self, company_integration_id):
    """
    Pull customers from QuickBooks and update local DB.
    - Retries if external API fails (3 times)
    - Checks company + integration status safely
    """
    try:
        company_integration = CompanyIntegration.objects.select_related("company").get(
            id=company_integration_id
        )
    except CompanyIntegration.DoesNotExist:
        logger.error(f"CompanyIntegration {company_integration_id} does not exist.")
        return

    company = company_integration.company

    # --- Validation Checks ---
    if not company_integration.is_active:
        logger.warning(f"Integration {company_integration_id} is inactive. Skipping sync.")
        return

    if not company.can_sync_provider():
        logger.warning(
            f"Company {company.id} is not allowed to sync provider. Skipping."
        )
        return

    try:
        # Fetch from QuickBooks
        customers = get_qbo_customers(company_integration)

        # Update local DB
        create_or_update_qbo_customers(company_integration, customers)

        logger.info(
            f"Synced {len(customers)} QuickBooks customers "
            f"for company {company.id} at {timezone.now()}."
        )

        # Optional: update last synced timestamp
        company_integration.last_synced_at = timezone.now()
        company_integration.save(update_fields=["last_synced_at"])

    except Exception as exc:
        logger.error(
            f"QuickBooks customer sync failed for integration {company_integration_id}: {exc}"
        )

        # Optional retry (3 attempts)
        try:
            raise self.retry(exc=exc, countdown=60)
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for QuickBooks sync.")


@shared_task(bind=True, max_retries=3)
def sync_qbo_invoices(self, company_integration_id):
    """
    Pull customers from QuickBooks and update local DB.
    - Retries if external API fails (3 times)
    - Checks company + integration status safely
    """
    try:
        company_integration = CompanyIntegration.objects.select_related("company").get(
            id=company_integration_id
        )
    except CompanyIntegration.DoesNotExist:
        logger.error(f"CompanyIntegration {company_integration_id} does not exist.")
        return

    company = company_integration.company

    # --- Validation Checks ---
    if not company_integration.is_active:
        logger.warning(f"Integration {company_integration_id} is inactive. Skipping sync.")
        return

    if not company.can_sync_provider():
        logger.warning(
            f"Company {company.id} is not allowed to sync provider. Skipping."
        )
        return

    try:
        # Fetch from QuickBooks
        invoices = get_qbo_invoices(company_integration)

        # Update local DB
        create_or_update_qbo_invoices(company_integration, invoices)

        logger.info(
            f"Synced {len(invoices)} QuickBooks invoices"
            f"for company {company.id} at {timezone.now()}."
        )

        # Optional: update last synced timestamp
        company_integration.last_synced_at = timezone.now()
        company_integration.save(update_fields=["last_synced_at"])

    except Exception as exc:
        logger.error(
            f"QuickBooks Invoice  sync failed for integration {company_integration_id}: {exc}"
        )

        # Optional retry (3 attempts)
        try:
            raise self.retry(exc=exc, countdown=60)
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for QuickBooks sync.")
