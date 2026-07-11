import logging

from junior_architect.backend.fake_backend import FakeBackend
from junior_architect.backend.logging_backend import LoggingBackend
from junior_architect.commands import registry


def test_logging_backend_forwards_to_inner_and_logs(caplog):
    inner = FakeBackend()
    backend = LoggingBackend(inner)
    with caplog.at_level(logging.INFO, logger="junior_architect"):
        registry.dispatch("draw_line", backend, start=[0, 0], end=[10, 0])
    # The operation actually reached the inner backend...
    assert len(inner.entities) == 1
    assert inner.entities[0].kind == "LINE"
    # ...and was logged.
    assert any("add_line" in rec.message for rec in caplog.records)


def test_dry_run_does_not_touch_inner_backend(caplog):
    inner = FakeBackend()
    backend = LoggingBackend(inner, dry_run=True)
    with caplog.at_level(logging.INFO, logger="junior_architect"):
        handle = registry.dispatch("draw_circle", backend, center=[1, 1], radius=2)
    # Nothing was drawn on the inner backend.
    assert inner.entities == []
    # A synthetic handle was returned instead.
    assert handle.startswith("DRY-")
    # The log line is marked as a dry run.
    assert any("[dry-run]" in rec.message and "add_circle" in rec.message for rec in caplog.records)


def test_dry_run_synthetic_handles_are_unique():
    backend = LoggingBackend(FakeBackend(), dry_run=True)
    a = registry.dispatch("draw_line", backend, start=[0, 0], end=[1, 1])
    b = registry.dispatch("draw_line", backend, start=[1, 1], end=[2, 2])
    assert a != b


def test_dry_run_composite_wall_emits_no_inner_entities(caplog):
    inner = FakeBackend()
    inner.create_layer("A-WALL")
    backend = LoggingBackend(inner, dry_run=True)
    with caplog.at_level(logging.INFO, logger="junior_architect"):
        registry.dispatch("draw_wall", backend, start=[0, 0], end=[5, 0], thickness=0.2, layer="A-WALL")
    # draw_wall is a composite that calls add_polyline; in dry-run nothing lands.
    assert inner.entities == []
    assert any("add_polyline" in rec.message for rec in caplog.records)


def test_verbose_layer_ops_are_logged_and_applied(caplog):
    inner = FakeBackend()
    backend = LoggingBackend(inner)
    with caplog.at_level(logging.INFO, logger="junior_architect"):
        registry.dispatch("create_layer", backend, name="A-WALL", color=4)
        registry.dispatch("set_current_layer", backend, name="A-WALL")
    assert "A-WALL" in inner.layers
    assert inner.current_layer == "A-WALL"
    messages = " ".join(rec.message for rec in caplog.records)
    assert "create_layer" in messages
    assert "set_current_layer" in messages
