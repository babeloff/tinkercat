"""
TinkerCat Python Bindings

Python bindings for the TinkerCat Kotlin multiplatform implementation.
This package provides a Pythonic interface to the native TinkerCat library
compiled from Kotlin/Native.

Example usage:
    from tinkercat import TinkerCat

    # Create a new graph — two equivalent factory forms:
    graph = TinkerCat()        # concise
    graph = TinkerCat.open()   # self-documenting

    # Add vertices
    alice = graph.add_vertex("person", name="Alice", age=30)
    bob = graph.add_vertex("person", name="Bob", age=25)

    # Add an edge
    edge = graph.add_edge("knows", alice, bob, since=2020)

    # Query the graph
    print(f"Graph has {graph.vertex_count} vertices and {graph.edge_count} edges")
"""

__version__ = "0.1.1"
__author__ = "Apache TinkerPop"
__email__ = "dev@tinkerpop.apache.org"

# Import main classes for public API
from .graph import TinkerCat, Vertex, Edge
from .exceptions import TinkerCatError
from .bindings import NATIVE_AVAILABLE

# Define what gets imported with "from tinkercat import *"
__all__ = [
    "TinkerCat",
    "Vertex",
    "Edge",
    "TinkerCatError",
    "NATIVE_AVAILABLE",
]

# Package metadata
__package_info__ = {
    "name": "tinkercat",
    "version": __version__,
    "description": "Python bindings for TinkerCat Kotlin multiplatform implementation",
    "author": __author__,
    "email": __email__,
    "license": "Apache License 2.0",
    "url": "https://github.com/apache/tinkerpop",
}
