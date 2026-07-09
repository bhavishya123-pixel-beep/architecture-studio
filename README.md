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
    logging_backend.py Wraps any backend to log every op; dry-run previews a plan
  commands/
    registry.py       @command decorator + dispatch(); renders the catalog as
                       Claude tool-use tool definitions
    layers.py          create_layer, set_current_layer, freeze_layer, thaw_layer
    primitives.py       draw_line, draw_polyline, draw_rectangle, draw_circle,
                        draw_arc, add_text
    dimensions.py       add_linear_dimension, add_aligned_dimension
    hatching.py         add_hatch
    blocks.py           insert_block
    architecture.py     draw_wall, draw_wall_with_openings, add_door, add_window,
                        label_room — composite architectural elements built on
                        the primitives
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

### Watching and previewing what the agent draws

Two flags wrap the chosen backend in a `LoggingBackend` so you can see exactly
what the agent is doing — especially useful for the live AutoCAD path, which
can't be unit-tested off Windows:

```bash
# Log every AutoCAD operation as it executes:
junior-architect --backend autocad --verbose

# Preview a whole drafting plan WITHOUT drawing anything (implies --verbose):
junior-architect --backend autocad --dry-run
```

A dry run logs each call (composite elements expanded into their primitives)
and returns synthetic `DRY-nnnn` handles instead of touching AutoCAD:

```
[dry-run] create_layer(name='A-WALL', color=4, linetype='Continuous')
[dry-run] add_polyline(points=[(0, 0.1, 0), (4, 0.1, 0), (4, -0.1, 0), (0, -0.1, 0)], closed=True, layer='A-WALL')
[dry-run] add_line(start=(1.5, 0, 0), end=(2.4, 0, 0), layer='A-DOOR')
[dry-run] add_arc(center=(1.5, 0, 0), radius=0.9, start_angle=0, end_angle=1.5708, layer='A-DOOR')
```

`LoggingBackend` is a plain backend wrapper, so it works programmatically too:

```python
from junior_architect import JuniorArchitectAgent, FakeBackend, LoggingBackend

backend = LoggingBackend(FakeBackend(), dry_run=True)
agent = JuniorArchitectAgent(backend)
agent.send("Draw a 4x3m bedroom with a door and label it")  # logs the plan, draws nothing
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
- `add_door` / `add_window` draw standard symbols along a wall direction. To actually cut
  the opening out of the wall, use `draw_wall_with_openings`, which draws wall segments
  around each opening and caps the wall thickness with jamb lines at the opening edges —
  then place the door/window symbol at the same offset point.
- Angles are degrees in every command's schema (natural for the chat agent to reason
  about) and are converted to radians at the backend boundary, matching AutoCAD's own
  COM convention.

## Tests

```bash
pytest
```

Tests run entirely against `FakeBackend`, so they don't require Windows, AutoCAD, or
an Anthropic API key.
