from sqladmin import ModelView

from modules.users.models import User


class UserAdmin(ModelView, model=User):
    icon = "fa-solid fa-users"
    column_list = [User.id, User.username]
    form_excluded_columns = ["messages"]

    def get_page_title(self, request, action: str) -> str:
        return "👤 User Management Panel"
