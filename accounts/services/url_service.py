from urllib.parse import urlencode
from django.conf import settings

class UrlService:
    @staticmethod
    def frontend_url(path="", params=None):
        base = settings.FRONTEND_BASE_URL.rstrip("/")
        clean_path = "/" + path.strip("/") if path else ""
        url = f"{base}{clean_path}"
        if params:
            url = f"{url}?{urlencode(params)}"
        return url

    @staticmethod
    def reset_password_url(token):
        return UrlService.frontend_url(settings.AUTH_RESET_PASSWORD_PATH, {"token": str(token)})