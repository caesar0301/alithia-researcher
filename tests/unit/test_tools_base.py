import pytest

from alithia.core.tools.base import Tool, ToolInput, ToolOutput


class EchoInput(ToolInput):
    text: str


class EchoOutput(ToolOutput):
    text: str


class EchoTool(Tool):
    InputModel = EchoInput

    def execute(self, inputs: EchoInput, **kwargs):
        return EchoOutput(text=inputs.text)


def test_tool_execute_and_call():
    tool = EchoTool()
    out = tool.execute(EchoInput(text="hello"))
    assert out.text == "hello"
    out2 = tool({"text": "world"})
    assert out2.text == "world"