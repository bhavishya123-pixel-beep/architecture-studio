"""Chat-driven interface: turns natural-language drafting instructions into a
sequence of AutoCAD commands, executed via Claude's tool-use API.
"""
import json
import os
from typing import Optional

from .backend.base import AutoCADBackend
from .commands import registry

SYSTEM_PROMPT = """You are a junior architect operating AutoCAD on behalf of a senior architect.
You draft using the provided tools: layers, lines, polylines, rectangles, circles, arcs, text,
dimensions, hatching, block insertion, and composite architectural elements
(walls, doors, windows, room labels).

Prefer the composite architecture tools (draw_wall, add_door, add_window, label_room) for
building elements, and the primitives for anything else. Always create or select an
appropriate layer before drawing, following common AutoCAD architectural layer naming
(A-WALL, A-DOOR, A-WIND, A-ANNO-DIMS, A-ANNO-TEXT, A-FLOR-HATCH, etc.).

Work in a sensible coordinate system (meters, unless the user specifies otherwise). Think
through the drafting plan briefly, then execute it step by step using the tools. Report back
concisely what you drew and any assumptions you made.
"""


class JuniorArchitectAgent:
    def __init__(
        self,
        backend: AutoCADBackend,
        model: str = "claude-sonnet-5",
        api_key: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> None:
        import anthropic

        self.client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.backend = backend
        self.model = model
        self.max_tokens = max_tokens
        self.messages = []

    def _execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        try:
            result = registry.dispatch(tool_name, self.backend, **tool_input)
            return {"ok": True, "result": result}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def send(self, user_message: str) -> str:
        """Send one user turn, running the tool-use loop to completion, and return the reply text."""
        self.messages.append({"role": "user", "content": user_message})
        tools = registry.as_anthropic_tools()

        while True:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=self.messages,
            )
            self.messages.append({"role": "assistant", "content": response.content})

            tool_calls = [block for block in response.content if block.type == "tool_use"]
            if not tool_calls:
                return "".join(block.text for block in response.content if block.type == "text")

            tool_results = []
            for call in tool_calls:
                result = self._execute_tool(call.name, call.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": call.id,
                        "content": json.dumps(result),
                        "is_error": not result["ok"],
                    }
                )
            self.messages.append({"role": "user", "content": tool_results})
