import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass

from astroid import nodes

from src.imports_iterator import (
    ImportsIterator
)


# from a import b
# a.py; import os as b

# from Node import Import, Import, Import
# import Import Import


@dataclass
class ImportItem:
    name: str
    asname: str | None = None
    node: Optional["Node"] = None  # if this import is a package

    def __repr__(self):
        return f"name: {self.name}, asname: {self.asname}"


@dataclass
class Node:
    path: str
    module: str
    imports: List["ImportItem"]


def path_to_module(file_path: str, project_root: str) -> str:
    file_path = Path(file_path).resolve()
    project_root = Path(project_root).resolve()

    relative = file_path.with_suffix("").relative_to(project_root)
    return ".".join(relative.parts)


def build_dir_imports(directory: str = ".") -> Tuple[List[Node], Dict[str, Node]]:
    """
    Builds all imports for each file inside the directory recursively

    Args:
        directory (str): directory to walk on to get its dependency graph

    Returns:
        A list of nodes (Node)
    """
    directory_tree = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".py"):
                directory_tree.append(os.path.join(dirpath, filename))

    node_list: List[Node] = []
    module_index: Dict[str, Node] = {}

    for file_path in directory_tree:
        it = ImportsIterator(file_path)
        module_name = path_to_module(file_path, directory)
        current_node = Node(path=file_path, module=module_name, imports=[])
        for node in it:
            for name in node.names:
                current_node.imports.append(ImportItem(*name))
        node_list.append(current_node)
        module_index[module_name] = current_node
    return node_list, module_index


def resolve_dir_import(node_list: List[Node], module_index: Dict[str, Node]) -> List[Node]:
    """
    Prints all imports for each file inside the directory recursively

    Args:
        node_list (List[Node]): all nodes that were previously built
        module_index (Dict[str, Node]): an index for each module and it's node to make
        resolving easier

    Returns:
        A list of nodes (Node) that also have resolved imports inside them
    """
    for node_object in node_list:
        for imp in node_object.imports:
            if imp.name in module_index:
                imp.node = module_index[imp.name]
            else:
                for mod_name, target_node in module_index.items():
                    if mod_name.endswith(imp.name):
                        imp.node = target_node
                        break
    return node_list


def generate_nodes(directory: str = "."):
    dir_imports = resolve_dir_import(*build_dir_imports(directory))

    print("\n"
          "##############################################################\n"
          "##############################################################\n"
          "##############################################################\n")
    for node in dir_imports:
        print(f"{node.path}, {node.module}")
        for imp in node.imports:
            print(f"\timport {imp}, node {imp.node}")


def get_function_scope(directory: str = ".", function: str = "."):
    pass
