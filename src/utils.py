import os
from dataclasses import dataclass

from astroid import nodes

from src.imports_iterator import (
    ImportsIterator
)
import ast
ast.ImportFrom

@dataclass
class Node:
    path: str
    module: str

@dataclass
class Import:
    name: str
    asname: str

# from a import b 
# a.py; import os as b

# from Node import Import, Import, Import
# import Import Import


def resolve_dir_imports(directory: str = ".") -> None:
    """
    Prints all imports for each file inside the directory recursively

    Args:
        directory (str): directory to walk on to get its dependency graph
    """
    directory_tree = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".py"):
                directory_tree.append(os.path.join(dirpath, filename))
    object_nodes = []
    for file_path in directory_tree:
        print(file_path)
        it = ImportsIterator(file_path)
        for node in it:
            if isinstance(node, nodes.Import):
                print(f"\timport: {[name[0] for name in node.names]}")
                for node_name in node.names:
                    
            elif isinstance(node, nodes.ImportFrom):
                print(f"\tfrom {node.modname} import {node.names}")



def get_function_scope(directory: str = ".", function: str = "."):
    pass


def generate_nodes(directory: str = "."):
    dir_imports = resolve_dir_imports(directory)
    # Node -> [Imports]
    # Import can be Nodes
