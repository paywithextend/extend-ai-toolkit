from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional


class ChatClient(ABC):
    """
    Abstract base class for LLM API clients.
    Implementations handle specific provider APIs (OpenAI, Anthropic, etc.)
    """

    @abstractmethod
    async def generate_completion(
            self,
            messages: List[Dict[str, Any]],
            functions: List[Dict[str, Any]],
            max_tokens: int) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Generate a completion from the LLM.

        Args:
            messages: List of message dictionaries with role and content
            functions: List of function definitions
            max_tokens: Maximum tokens to generate

        Returns:
            Tuple containing:
                - content: The text response if no function call (None if function call)
                - function_call: Dictionary with name and arguments if a function call is needed,
                  or None if no function call
        """
        pass

    @abstractmethod
    async def generate_with_tool_result(
            self,
            messages: List[Dict[str, Any]],
            max_tokens: int) -> str:
        """
        Generate a follow-up completion after a tool call.

        Args:
            messages: List of message dictionaries including tool results
            max_tokens: Maximum tokens to generate

        Returns:
            Text response from the model
        """
        pass
