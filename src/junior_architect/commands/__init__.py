"""Central catalog of AutoCAD drafting commands available to the chat agent.

Importing this package registers every command module below into
`registry.REGISTRY`.
"""
from . import registry  # noqa: F401  (re-exported for `from .commands import registry`)
from . import architecture, blocks, dimensions, document, hatching, layers, primitives  # noqa: F401
