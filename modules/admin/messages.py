from sqladmin import ModelView

from modules.chats.models import AgentMessage, Message


class AgentMessagesAdmin(ModelView, model=AgentMessage):
    icon = "fa-regular fa-comment"
    page_size = 50
    column_default_sort = (Message.created_at, True)
    column_list = [AgentMessage.id, "user.id", AgentMessage.created_at]


class MessagesAdmin(ModelView, model=Message):
    icon = "fa-regular fa-comment"
    page_size = 50
    column_default_sort = (Message.created_at, True)
    column_list = [
        Message.id,
        "user.id",
        Message.direction,
        Message.created_at,
        "message",
    ]

    column_formatters = {
        "message": lambda m, _: (m.message[:60] + "…")
        if m.message and len(m.message) > 60
        else m.message
    }


