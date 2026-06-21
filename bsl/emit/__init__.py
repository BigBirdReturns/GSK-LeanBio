"""Emitter port and adapters.

The port (`Emitter`) is the AXM-shaped mating surface: candidates in, an emitted
artifact out. `FileSink` is the standalone, dependency-free default.
`GenesisEmitter` is the optional growth-surface backend that docks the AXM
cryptographic kernel to produce a signed, conformant shard.
"""

from .port import Emitter, SourceDoc, EmitResult
from .file_sink import FileSink

__all__ = ["Emitter", "SourceDoc", "EmitResult", "FileSink"]
