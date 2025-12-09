from django.db import models
from .encryption import encrypt_value, decrypt_value
import json


class EncryptedJSONField(models.JSONField):
    """
    JSONField with automatic encryption/decryption using Fernet
    """

    def get_prep_value(self, value):
        """
        Called before saving to DB
        """
        if value is None:
            return None
        # Convert dict to JSON string, then encrypt
        json_str = json.dumps(value)
        return encrypt_value(json_str)

    def from_db_value(self, value, expression, connection):
        """
        Called when reading from DB
        """
        if value is None:
            return None
        # Decrypt and convert JSON string back to dict
        decrypted = decrypt_value(value)
        return json.loads(decrypted)

    def to_python(self, value):
        """
        Convert value to dict
        """
        if isinstance(value, dict) or value is None:
            return value
        # Decrypt if it's a string
        decrypted = decrypt_value(value)
        return json.loads(decrypted)
