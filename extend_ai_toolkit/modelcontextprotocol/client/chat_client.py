"""Provider-neutral turn objects; providers retain their native message formats."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class AssistantTurn:
    message: dict[str, Any]
    calls: tuple[ToolCall, ...] = ()
    text: str = ""


class ChatClient(ABC):
    @abstractmethod
    async def complete(self, messages, tools, max_tokens) -> AssistantTurn:
        raise NotImplementedError

    @abstractmethod
    def result_messages(self, results):
        raise NotImplementedError

    async def aclose(self):
        pass
