class DeviceService:
    @staticmethod
    def parse(user_agent):
        ua = user_agent or ""
        browser = "Unknown"
        os = "Unknown"
        device = "Desktop"
        if "Chrome" in ua:
            browser = "Chrome"
        elif "Firefox" in ua:
            browser = "Firefox"
        elif "Safari" in ua:
            browser = "Safari"
        elif "Edg" in ua:
            browser = "Edge"
        if "Windows" in ua:
            os = "Windows"
        elif "Mac OS" in ua:
            os = "macOS"
        elif "Linux" in ua:
            os = "Linux"
        elif "Android" in ua:
            os = "Android"
            device = "Mobile"
        elif "iPhone" in ua:
            os = "iOS"
            device = "Mobile"
        return {"browser": browser, "os": os, "device": device}