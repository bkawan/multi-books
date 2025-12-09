from django.conf import settings
from intuitlib.enums import Scopes

class IntegrationProviderChoice:
    QUICKBOOKS = "quickbooks_online"
    ZOHO = "zoho_books"

    CHOICES = [
        (QUICKBOOKS, "QuickBooks Online"),
        (ZOHO, "Zoho Books"),
    ]

INTEGRATION_PROVIDERS = [
    {
        "name": "quickbooks_online",
        "display_name": "QuickBooks Online",
        "auth_type": "oauth2",
        "is_active": True,
        "config": {
            "client_id": settings.QBO_CLIENT_ID,
            "client_secret": settings.QBO_CLIENT_SECRET,
            "redirect_uri": settings.QBO_REDIRECT_URI,
            "environment": settings.QBO_ENVIRONMENT,
            "scope": [scope.value for scope in [
                Scopes.ACCOUNTING,
                Scopes.OPENID,
                Scopes.PROFILE,
                Scopes.EMAIL,
                Scopes.PHONE,
                Scopes.ADDRESS
            ]],
            "api_base_url": settings.QBO_BASE_URL,
            "base_sand_box_url": "https://sandbox-quickbooks.api.intuit.com",
            "base_production_box_url": "https://quickbooks.api.intuit.com",
            "auth_url": "https://appcenter.intuit.com/connect/oauth2",
            "token_url": "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
            "revoke_url": "https://developer.api.intuit.com/v2/oauth2/tokens/revoke",

        }
    },

    {
        "name": "zoho_books",
        "display_name": "Zoho Books",
        "auth_type": "oauth2",
        "is_active": True,
        "config": {
            "client_id": settings.ZOHO_CLIENT_ID,
            "client_secret": settings.ZOHO_CLIENT_SECRET,
            "redirect_uri": settings.ZOHO_REDIRECT_URI,
            "scope": "ZohoBooks.fullaccess.all",

            "auth_url": "https://accounts.zoho.com/oauth/v2/auth",
            "token_url": "https://accounts.zoho.com/oauth/v2/token",
            "api_base_url": "https://books.zoho.com/api/v3"
        }
    }
]
