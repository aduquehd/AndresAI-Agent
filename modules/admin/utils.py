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
    return Markup(f'''
        <div style="font-size: 0.875rem;">
            <div style="color: #2196F3;">
                <i class="fa-solid fa-globe"></i> {browser_info}
            </div>
            <div style="color: #666; font-size: 0.75rem;">
                <i class="fa-solid fa-desktop"></i> {os_info}
            </div>
        </div>
    ''')