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
        Message.ip_address,
        Message.country,
        Message.city,
        Message.response_time_ms,
        Message.created_at,
        "message",
        "user_agent",
    ]

    column_formatters = {
        "message": lambda m, _: (m.message[:60] + "…")
        if m.message and len(m.message) > 60
        else m.message,
        "user_agent": lambda m, _: (m.user_agent[:50] + "…")
        if m.user_agent and len(m.user_agent) > 50
        else m.user_agent,
        "response_time_ms": lambda m, _: f"{m.response_time_ms}ms"
        if m.response_time_ms
        else None,
    }


