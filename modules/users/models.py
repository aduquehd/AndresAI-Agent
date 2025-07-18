from typing import ForwardRef, List, Optional

from sqlmodel import Field, Relationship, SQLModel


# Forward reference to avoid circular dependency
MessagesRef = ForwardRef("Message")
AgentMessagesRef = ForwardRef("AgentMessage")


class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="user")
    agent_messages: List["AgentMessage"] = Relationship(back_populates="user")
