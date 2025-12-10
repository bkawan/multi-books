import uuid

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.company.constants import CompanyStatusChoices
from apps.company.models import Company
from apps.integration.models import IntegrationProvider, CompanyIntegration
from apps.integration.selectors import get_qbo_customers
from apps.integration.services import create_or_update_qbo_customers


class QuickBooksConnectAPIView(APIView):
    """
    API endpoint to redirect a user to QuickBooks OAuth authorization page.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, company_id):
        user_company = getattr(request.user, 'company', None)
        if not user_company:
            return Response({'error': 'You are not authorized to access this page.'},
                            status=status.HTTP_401_UNAUTHORIZED)
        if user_company.id != company_id:
            return Response({'error': 'You are not authorized to access this company.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        if (user_company.status not in [CompanyStatusChoices.ACTIVE, CompanyStatusChoices.ACCEPTED]
                or not user_company.is_active):
            return Response({
                'data': {
                    'company': {
                        "name": user_company.name,
                        "status": user_company.status,
                        "is_active": user_company.is_active,
                    }
                },
                'error': 'Your company is not active. Contact your administrator.'
            },
                status=status.HTTP_400_BAD_REQUEST)

        # Get QuickBooks IntegrationProvider from DB
        provider = get_object_or_404(IntegrationProvider, name="quickbooks_online")

        # Load OAuth config from provider.config
        config = provider.config
        client_id = config.get("client_id")
        client_secret = config.get("client_secret")
        redirect_uri = config.get("redirect_uri")
        environment = config.get("environment")
        scope_list = config.get("scope", [])

        # Convert strings to Scopes enum if needed
        scopes_enum = []
        for s in scope_list:
            try:
                scopes_enum.append(Scopes(s))
            except ValueError:
                scopes_enum.append(s)

        # Generate state for CSRF protection
        state = str(uuid.uuid4())
        request.session['qb_oauth_state'] = state
        request.session['qb_company_id'] = company_id

        # Initialize AuthClient dynamically from DB
        auth_client = AuthClient(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            environment=environment,
        )

        # Get authorization URL dynamically with scopes from DB
        authorization_url = auth_client.get_authorization_url(
            scopes_enum,
            state_token=state
        )

        # DRF redirect response
        return redirect(authorization_url)


class QuickBooksCallbackAPIView(APIView):
    """
    QuickBooks OAuth callback API:
    - Validates state token
    - Ensures company belongs to logged-in user
    - Prevents other users from connecting the same QuickBooks account
    - Updates existing integration if same company
    - Returns home page URL in response
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1️⃣ Get query params
        code = request.GET.get("code")
        state = request.GET.get("state")
        realm_id = request.GET.get("realmId")

        # 2️⃣ Validate state and company in session
        saved_state = request.session.get("qb_oauth_state")
        company_id = request.session.get("qb_company_id")

        if not state or state != saved_state:
            return Response({"error": "Invalid state parameter"}, status=status.HTTP_400_BAD_REQUEST)
        if not company_id:
            return Response({"error": "Company ID not found in session"}, status=status.HTTP_400_BAD_REQUEST)

        # 3️⃣ Fetch company and check ownership
        company = get_object_or_404(Company, id=company_id, is_active=True)
        if company != request.user.company:
            return Response(
                {"error": "You are not authorized to connect QuickBooks for this company."},
                status=status.HTTP_403_FORBIDDEN
            )

        # 4️⃣ Get QuickBooks provider
        provider = get_object_or_404(IntegrationProvider, name="quickbooks_online", is_active=True)

        # 5️⃣ Initialize QuickBooks AuthClient
        config = provider.config
        auth_client = AuthClient(
            client_id=config.get("client_id"),
            client_secret=config.get("client_secret"),
            redirect_uri=config.get("redirect_uri"),
            environment=config.get("environment"),
        )

        # 6️⃣ Exchange code for tokens
        try:
            auth_client.get_bearer_token(code, realm_id=realm_id)
        except Exception as e:
            return Response({"error": f"Error obtaining token: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 7️⃣ Check existing integration
        existing_integration = CompanyIntegration.objects.filter(
            provider=provider,
            provider_identifier=realm_id
        ).first()

        if existing_integration:
            if existing_integration.company != company:
                # Already connected to another company → reject
                return Response(
                    {"error": "This QuickBooks account is already connected to another company."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Same company → update
            company_integration = existing_integration
        else:
            # Create new integration
            company_integration = CompanyIntegration(company=company, provider=provider)

        # 8️⃣ Save/update integration
        company_integration.credentials = {
            "access_token": auth_client.access_token,
            "refresh_token": auth_client.refresh_token,
            "expires_in": auth_client.expires_in,
            "token_created_at": timezone.now().isoformat(),
        }
        company_integration.provider_data = {"realm_id": realm_id}
        company_integration.provider_identifier = realm_id
        company_integration.is_active = True
        company_integration.save()

        # 9️⃣ Cleanup session
        request.session.pop("qb_oauth_state", None)
        request.session.pop("qb_company_id", None)

        # 🔟 Return success with home URL
        success_redirect_url = reverse_lazy('home')
        success_redirect_url = request.build_absolute_uri(success_redirect_url)
        return Response({
            "detail": "QuickBooks connected successfully!",
            "redirect_url": success_redirect_url
        }, status=status.HTTP_200_OK)


class QuickBooksOnlineSyncCustomersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, company_id):
        # ToDo need to check request user company
        # ToDo need to check if admin is doing on behalf of company
        # 1. Find integration
        if request.user.company.id != company_id:
            return Response(
                {"error": "You are not authorized for this company."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if not request.user.company.can_sync_provider():
            return Response(
                {"error": "Your company can not be sync"},
                status=status.HTTP_400_BAD_REQUEST
            )

        company_integration = CompanyIntegration.objects.filter(
            company_id=company_id,
            provider__name="quickbooks_online"
        ).first()

        if not company_integration.is_active:
            return Response(
                {"error": "Integration is not Active"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not company_integration:
            return Response(
                {"error": "QuickBooks not connected for this company"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Fetch remote + update local DB
        try:
            customers = get_qbo_customers(company_integration)
            create_or_update_qbo_customers(company_integration, customers)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 3. Send JSON response
        return Response({"message": "Successfully Fetch and updated in Database"}, status=status.HTTP_200_OK)
