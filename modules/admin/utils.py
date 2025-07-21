from datetime import timedelta, timezone

from markupsafe import Markup


def format_user_agent(user_agent_string):
    """Parse user agent string and return formatted browser/OS info."""
    if not user_agent_string:
        return ""

    # Extract browser info
    browser = "Unknown"
    version = ""
    os_info = "Unknown OS"

    # Parse OS
    if "Windows NT" in user_agent_string:
        if "Windows NT 10.0" in user_agent_string:
            os_info = "Windows 10/11"
        elif "Windows NT 6.3" in user_agent_string:
            os_info = "Windows 8.1"
        elif "Windows NT 6.2" in user_agent_string:
            os_info = "Windows 8"
        elif "Windows NT 6.1" in user_agent_string:
            os_info = "Windows 7"
        else:
            os_info = "Windows"
    elif "Mac OS X" in user_agent_string:
        os_info = "macOS"
        if "Intel" in user_agent_string:
            os_info += " (Intel)"
        elif "ARM" in user_agent_string:
            os_info += " (Apple Silicon)"
    elif "Android" in user_agent_string:
        os_info = "Android"
    elif "iPhone" in user_agent_string:
        os_info = "iOS (iPhone)"
    elif "iPad" in user_agent_string:
        os_info = "iOS (iPad)"
    elif "Linux" in user_agent_string:
        os_info = "Linux"

    # Parse browser - check from most specific to least specific
    if "Edg/" in user_agent_string:
        browser = "Edge"
        try:
            version = user_agent_string.split("Edg/")[1].split()[0].split(".")[0]
        except (IndexError, AttributeError):
            pass
    elif "Chrome/" in user_agent_string and "Safari/" in user_agent_string:
        browser = "Chrome"
        try:
            version = user_agent_string.split("Chrome/")[1].split()[0].split(".")[0]
        except (IndexError, AttributeError):
            pass
    elif "Firefox/" in user_agent_string:
        browser = "Firefox"
        try:
            version = user_agent_string.split("Firefox/")[1].split()[0].split(".")[0]
        except (IndexError, AttributeError):
            pass
    elif "Safari/" in user_agent_string and "Version/" in user_agent_string:
        browser = "Safari"
        try:
            version = user_agent_string.split("Version/")[1].split()[0].split(".")[0]
        except (IndexError, AttributeError):
            pass

    # Format the output
    browser_info = f"{browser} {version}" if version else browser

    # Create a nice HTML output with icons
    return Markup(f"""
        <div style="font-size: 0.875rem;">
            <div style="color: #2196F3;">
                <i class="fa-solid fa-globe"></i> {browser_info}
            </div>
            <div style="color: #666; font-size: 0.75rem;">
                <i class="fa-solid fa-desktop"></i> {os_info}
            </div>
        </div>
    """)


def format_datetime_utc5(dt):
    """Format datetime to UTC-5 timezone with readable format."""
    if not dt:
        return ""

    # Create UTC-5 timezone
    utc_minus_5 = timezone(timedelta(hours=-5))

    # Convert to UTC-5 if the datetime is timezone-aware
    if dt.tzinfo is not None:
        local_dt = dt.astimezone(utc_minus_5)
    else:
        # Assume UTC if no timezone info
        utc_dt = dt.replace(tzinfo=timezone.utc)
        local_dt = utc_dt.astimezone(utc_minus_5)

    # Format: "Dec 21 10:30:45 AM"
    return local_dt.strftime("%b %d, %I:%M:%S %p")
