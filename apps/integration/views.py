from django.contrib.auth import logout
from django.shortcuts import redirect, render

from apps.integration.models import IntegrationProvider, CompanyIntegration
from .services import refresh_qbo_token_for_integration


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
    logout(request)
    return redirect('home')
