from sqladmin import ModelView

from modules.admin.utils import format_datetime_utc5, format_user_agent
from modules.users.models import User


class UserAdmin(ModelView, model=User):
    icon = "fa-solid fa-users"
    page_size = 50
    column_default_sort = (User.created_at, True)
    column_list = [
        User.id,
        User.username,
        User.browser_id,
        User.ip_address,
        User.country,
        User.city,
        User.created_at,
        "user_agent",
    ]
    column_searchable_list = ["username", "id", "browser_id"]
    column_sortable_list = [
        "id",
        "username",
        "browser_id",
        "ip_address",
        "country",
        "city",
        "created_at",
    ]
    form_excluded_columns = ["messages", "agent_messages"]

    # Enable filtering and export
    can_view_details = True
    can_export = True

    # Better column labels
    column_labels = {
        "id": "User ID",
        "username": "Username",
        "browser_id": "Browser ID",
        "ip_address": "IP Address",
        "country": "Country",
        "city": "City",
        "created_at": "Created At",
        "user_agent": "User Agent",
    }

    # Search placeholder
    def search_placeholder(self):
        return "Username | User ID | Browser ID"

    column_formatters = {
        "user_agent": lambda m, _: format_user_agent(m.user_agent) if m.user_agent else None,
        "created_at": lambda m, _: format_datetime_utc5(m.created_at),
    }

    def get_page_title(self, request, action: str) -> str:
        return "👤 User Management Panel"
