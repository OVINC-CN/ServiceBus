from django.utils.translation import gettext_lazy

from core.models import TextChoices

# Char Length
SMS_CHAR_LENGTH = 12
SHORT_CHAR_LENGTH = 32
MEDIUM_CHAR_LENGTH = 64
MAX_CHAR_LENGTH = 255
PHONE_NUMBER_CHAR_LENGTH = 11
VERIFY_CODE_LENGTH = 6

# Pagination
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Cache
DEFAULT_CACHE_TIMEOUT = 60

# App Auth
APP_AUTH_HEADER_KEY = "HTTP_OVINC_APP"
APP_AUTH_ID_KEY = "app_code"
APP_AUTH_SECRET_KEY = "app_secret"


# Request
class ViewActionChoices(TextChoices):
    LIST = "list", gettext_lazy("LIST")
    CREATE = "create", gettext_lazy("CREATE")
    UPDATE = "update", gettext_lazy("UPDATE")
    PARTIAL_UPDATE = "partial_update", gettext_lazy("PARTIAL_UPDATE")
    DESTROY = "destroy", gettext_lazy("DESTROY")
