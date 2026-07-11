from junior_architect.commands import registry


def test_registry_has_expected_commands():
    expected = {
        "draw_line",
        "draw_polyline",
        "draw_rectangle",
        "draw_circle",
        "draw_arc",
        "add_text",
        "create_layer",
        "set_current_layer",
        "freeze_layer",
        "thaw_layer",
        "add_linear_dimension",
        "add_aligned_dimension",
        "add_hatch",
        "insert_block",
        "draw_wall",
        "add_door",
        "add_window",
        "label_room",
        "new_drawing",
        "open_drawing",
        "save_drawing",
        "zoom_extents",
    }
    assert expected.issubset(set(registry.REGISTRY))


def test_tool_schema_shape():
    tools = registry.as_anthropic_tools()
    by_name = {t["name"]: t for t in tools}
    line_tool = by_name["draw_line"]
    assert line_tool["input_schema"]["type"] == "object"
    assert "start" in line_tool["input_schema"]["properties"]
    assert "start" in line_tool["input_schema"]["required"]


def test_dispatch_unknown_command_raises_keyerror():
    import pytest

    with pytest.raises(KeyError):
        registry.dispatch("not_a_real_command", None)
