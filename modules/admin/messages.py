import hashlib
import html

from markupsafe import Markup
from sqladmin import ModelView

from modules.admin.utils import format_datetime_utc5, format_user_agent
from modules.chats.models import AgentMessage, Message, MessageDirectionEnum


def _generate_user_color(user_id):
    """Generate a consistent color for a user ID using hash."""
    if not user_id:
        return "#666666"  # Default gray for None values

    # Create hash of user ID and take first 6 characters for color
    hash_object = hashlib.md5(str(user_id).encode())
    hex_dig = hash_object.hexdigest()[:6]

    # Ensure the color is not too light (minimum brightness)
    color = f"#{hex_dig}"

    # Convert to RGB to check brightness and adjust if needed
    r = int(hex_dig[0:2], 16)
    g = int(hex_dig[2:4], 16)
    b = int(hex_dig[4:6], 16)

    # Calculate brightness (0-255)
    brightness = (r * 299 + g * 587 + b * 114) / 1000

    # If too light, darken it
    if brightness > 180:
        r = max(0, r - 80)
        g = max(0, g - 80)
        b = max(0, b - 80)
        color = f"#{r:02x}{g:02x}{b:02x}"

    return color


def _format_user_id_with_highlight(message, _):
    """Format user ID with consistent color highlighting."""
    if not message.user_id:
        return "N/A"

    user_id = message.user_id
    color = _generate_user_color(user_id)

    return Markup(f"""
        <span style="
            background-color: {color}; 
            color: white; 
            padding: 2px 6px; 
            border-radius: 4px; 
            font-weight: bold;
            font-size: 11px;
        ">{user_id}</span>
    """)


def _format_message_with_tooltip(message):
    """Format message with truncated display and alert popup."""
    if not message:
        return ""

    # Truncate display text if too long
    if len(message) > 60:
        display_text = message[:60] + "…"
        # Use base64 encoding to safely pass the message to JavaScript
        import base64

        encoded_message = base64.b64encode(message.encode("utf-8")).decode("ascii")

        return Markup(f"""
            <div>
                <span>{html.escape(display_text)}</span>
                <button 
                    type="button" 
                    style="
                        margin-left: 5px; 
                        padding: 2px 6px; 
                        font-size: 10px; 
                        background: #1976d2; 
                        color: white; 
                        border: none; 
                        border-radius: 3px; 
                        cursor: pointer;
                    "
                    onclick="
                        var message = atob('{encoded_message}');
                        alert(message);
                    "
                >View</button>
            </div>
        """)
    else:
        return html.escape(message)


class AgentMessagesAdmin(ModelView, model=AgentMessage):
    icon = "fa-regular fa-comment"
    page_size = 50
    column_default_sort = (Message.created_at, True)
    column_list = [AgentMessage.id, "user.id", AgentMessage.created_at]


class MessagesAdmin(ModelView, model=Message):
    name = "Message"
    name_plural = "Messages"
    icon = "fa-regular fa-comment"
    page_size = 50
    column_default_sort = (Message.created_at, True)
    column_list = [
        Message.id,
        "user.id",
        "direction",
        Message.ip_address,
        Message.country,
        Message.city,
        Message.response_time_ms,
        Message.created_at,
        "message",
        "user_agent",
    ]
    column_searchable_list = ["user_id", "direction"]
    column_sortable_list = [
        "id",
        "user_id",
        "direction",
        "ip_address",
        "country",
        "city",
        "response_time_ms",
        "created_at",
    ]

    # Enable filtering
    can_view_details = True
    can_export = True
    form_choices = {
        "direction": [(choice.value, choice.value.title()) for choice in MessageDirectionEnum]
    }

    # Better column labels
    column_labels = {
        "id": "Message ID",
        "user.id": "User ID",
        "direction": "Direction",
        "ip_address": "IP Address",
        "country": "Country",
        "city": "City",
        "response_time_ms": "Response Time",
        "created_at": "Created At",
        "message": "Message Content",
        "user_agent": "User Agent",
        "user_id": "User ID",
    }

    # Search placeholder
    def search_placeholder(self):
        return "User ID | Direction"

    column_formatters = {
        "user.id": _format_user_id_with_highlight,
        "message": lambda m, _: _format_message_with_tooltip(m.message),
        "user_agent": lambda m, _: format_user_agent(m.user_agent) if m.user_agent else None,
        "response_time_ms": lambda m, _: f"{m.response_time_ms}ms" if m.response_time_ms else None,
        "created_at": lambda m, _: format_datetime_utc5(m.created_at),
        "direction": lambda m, _: Markup(
            f'<span style="color: #4CAF50;"><i class="fa-solid fa-arrow-down"></i> {m.direction.value.title()}</span>'
            if m.direction.value == "incoming"
            else f'<span style="color: #2196F3;"><i class="fa-solid fa-arrow-up"></i> {m.direction.value.title()}</span>'
        ),
    }
