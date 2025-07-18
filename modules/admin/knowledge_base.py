from fastapi import Request
from openai import AsyncOpenAI
from sqladmin import ModelView

from modules.knowledge_base.models import KnowledgeBase


class KnowledgeBaseAdmin(ModelView, model=KnowledgeBase):
    icon = "fa-solid fa-brain"
    page_size = 50
    column_list = [KnowledgeBase.id, KnowledgeBase.type, KnowledgeBase.title, KnowledgeBase.content]
    form_excluded_columns = ["embedding"]

    async def on_model_change(
        self, data: dict, model: KnowledgeBase, is_created: bool, request: Request
    ) -> None:
        openai = AsyncOpenAI()

        text = f"type: {data['type']}\ntitle: {data['title']}\ncontent: {data['content']}"
        response = await openai.embeddings.create(
            input=text,
            model="text-embedding-3-small",
        )

        model.type = data["type"]
        model.title = data["title"]
        model.content = data["content"]
        model.embedding = response.data[0].embedding
