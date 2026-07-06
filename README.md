# architecture-studio — Junior Architect

An installable AI "junior architect" that chats with you and drafts in a live AutoCAD
session. You describe what you want ("draw a 5m wall along the north side and put a
door 1m in"), and it plans a sequence of AutoCAD operations and executes them via
AutoCAD's COM Automation API.

## Architecture

```
src/junior_architect/
  geometry.py        Point/vector math shared by every command (offsets, centroid, area)
  backend/
    base.py           AutoCADBackend interface every backend implements
    fake_backend.py   In-memory backend — records entities, no AutoCAD required
    win32_backend.py  Real backend — drives AutoCAD live over COM (Windows only)
  commands/
    registry.py       @command decorator + dispatch(); renders the catalog as
                       Claude tool-use tool definitions
    layers.py          create_layer, set_current_layer, freeze_layer, thaw_layer
    primitives.py       draw_line, draw_polyline, draw_rectangle, draw_circle,
                        draw_arc, add_text
    dimensions.py       add_linear_dimension, add_aligned_dimension
    hatching.py         add_hatch
    blocks.py           insert_block
    architecture.py     draw_wall, add_door, add_window, label_room — composite
                        architectural elements built on the primitives
    document.py         new_drawing, open_drawing, save_drawing, zoom_extents
  agent.py            JuniorArchitectAgent — Claude tool-use loop over the registry
  cli.py              `junior-architect` command (chat REPL)
```

Every drafting command is registered once via `@command(...)` and is simultaneously:
1. a plain Python function callable directly against any backend, and
2. a Claude tool definition the chat agent can invoke by name.

This is the "command wrapper library" layer — the first slice. It does not yet do
full floor-plan layout generation; it gives the agent (and you) a solid, tested set of
AutoCAD building blocks to draft with.

## Install

```bash
pip install -e .              # core (fake backend + agent, any OS)
pip install -e ".[windows]"   # + pywin32, for the real AutoCAD backend (Windows only)
pip install -e ".[dev]"       # + pytest
```

Requires an `ANTHROPIC_API_KEY` environment variable to run the chat agent.

## Usage

```bash
# Drive a live AutoCAD session (Windows, AutoCAD must be installed):
junior-architect --backend autocad

# Try it without AutoCAD, against the in-memory fake backend:
junior-architect --backend fake
```

```
Junior Architect ready. Describe what to draft (Ctrl-D to quit).
> Draw a 5m x 4m room with a door on the south wall and label it "Bedroom 1"
```

Programmatic use:

```python
from junior_architect import JuniorArchitectAgent, FakeBackend

agent = JuniorArchitectAgent(FakeBackend())
print(agent.send("Draw a 3m wall from (0,0) to (3,0) on layer A-WALL"))
```

Or call commands directly without the chat layer:

```python
from junior_architect.backend.fake_backend import FakeBackend
from junior_architect.commands import registry

backend = FakeBackend()
backend.create_layer("A-WALL")
registry.dispatch("draw_wall", backend, start=[0, 0], end=[5, 0], thickness=0.2, layer="A-WALL")
```

## Notes and current limitations

- The real backend talks to AutoCAD via COM Automation (`AutoCAD.Application`), so it
  only runs on Windows with AutoCAD installed and licensed. Everything else in this
  package is platform-independent and unit-tested against `FakeBackend`.
- `add_door` / `add_window` draw standard symbols along a wall direction but don't cut
  the wall opening automatically — that needs boolean/region operations on the wall
  solid, which is a natural next slice.
- Angles are degrees in every command's schema (natural for the chat agent to reason
  about) and are converted to radians at the backend boundary, matching AutoCAD's own
  COM convention.

## Tests

```bash
pytest
```

Tests run entirely against `FakeBackend`, so they don't require Windows, AutoCAD, or
an Anthropic API key.
