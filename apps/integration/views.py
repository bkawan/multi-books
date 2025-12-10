import uuid

from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.utils import timezone
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

from apps.company.models import Company
from .services import create_or_update_qbo_customers, refresh_qbo_token_for_integration
from apps.integration.models import IntegrationProvider, CompanyIntegration
from apps.integration.selectors import get_qbo_customers, get_qbo_invoices
from .services import create_or_update_qbo_invoices


# @login_required
def get_customers_api(request, company_id):
    company_integration = CompanyIntegration.objects.filter(
        company_id=company_id,
        provider__name="quickbooks_online"
    ).first()

    if not company_integration:
        return JsonResponse({"error": "QuickBooks not connected for this company"}, status=400)

    try:
        customers = get_qbo_customers(company_integration)
        create_or_update_qbo_customers(company_integration, customers)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"customers": customers})


# @login_required
def get_invoices_api(request, company_id):
    company_integration = CompanyIntegration.objects.filter(
        company_id=company_id,
        provider__name="quickbooks_online"
    ).first()

    if not company_integration:
        return JsonResponse({"error": "QuickBooks not connected for this company"}, status=400)
    try:
        invoices = get_qbo_invoices(company_integration)
        create_or_update_qbo_invoices(company_integration, invoices)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"invoices": invoices})


def home(request):
    """
    Home page: Shows Connect / Logout depending on QuickBooks (or other integration) DB status.
    """
    qb_connected = False
    qb_integration_data = None

    if request.user.is_authenticated and getattr(request.user, 'company', None):
        company = request.user.company

        try:
            # Get the QuickBooks provider
            qb_provider = IntegrationProvider.objects.get(name="quickbooks_online", is_active=True)

            # Get the company integration
            company_integration = CompanyIntegration.objects.filter(
                company=company, provider=qb_provider, is_active=True
            ).first()

            if company_integration:
                # Refresh access token if expired
                access_token = refresh_qbo_token_for_integration(company_integration)

                if access_token:
                    qb_connected = True
                    qb_integration_data = {
                        "access_token": access_token,
                        "provider_name": qb_provider.display_name,
                        "provider_identifier": company_integration.provider_identifier,
                    }

        except IntegrationProvider.DoesNotExist:
            qb_connected = False

    context = {
        "qb_connected": qb_connected,
        "qb_integration": qb_integration_data,
        "user": request.user,
    }

    return render(request, "index.html", context)


def logout_view(request):
    logout(request)  # clears the user session
    return redirect('home')  # redirect to home page or login
