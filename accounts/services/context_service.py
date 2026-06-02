from accounts.services.device_service import DeviceService

class ContextService:
    @staticmethod
    def get_client_ip(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    @staticmethod
    def get_context(request):
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        device = DeviceService.parse(user_agent)
        return {"ip": ContextService.get_client_ip(request), "user_agent": user_agent, "browser": device["browser"], "os": device["os"], "device": device["device"], "risk_score": 0}