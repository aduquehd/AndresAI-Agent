from sqladmin import ModelView

from modules.agent.models import AgentContext


class AgentContextAdmin(ModelView, model=AgentContext):
    icon = "fa-solid fa-robot"
    column_list = [AgentContext.id, AgentContext.status, AgentContext.created_at]
    column_default_sort = (AgentContext.created_at, True)
