import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass

import astroid

from src.imports_iterator import ImportsIterator


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


def path_to_module(file_path: str, project_root: str, is_dir: bool = False) -> str:
    file_path = Path(file_path).resolve()
    project_root = Path(project_root).resolve()

    relative = file_path.relative_to(project_root)

    if is_dir:
        return ".".join(relative.parts)

    if relative.name == "__init__.py":
        return ".".join(relative.parent.parts)

    return ".".join(relative.with_suffix("").parts)


def build_dir_imports(directory: str = ".") -> Tuple[List[Node], Dict[str, Node]]:
    """
    Builds all imports for each file inside the directory recursively

    Args:
        directory (str): directory to walk on to get its dependency graph

    Returns:
        A list of nodes (Node)
    """
    node_list: List[Node] = []
    module_index: Dict[str, Node] = {}

    for dirpath, dirnames, filenames in os.walk(directory):
        module_name = path_to_module(dirpath, directory, is_dir=True)

        node = Node(
            path=dirpath,
            module=module_name,
            imports=[]
        )

        node_list.append(node)
        module_index[module_name] = node

        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(dirpath, filename)
                module_name = path_to_module(file_path, directory)
                current_node = Node(path=file_path, module=module_name, imports=[])
                node_list.append(current_node)
                module_index[module_name] = current_node

    return node_list, module_index


def parse_imports(node_list: List[Node], module_index: Dict[str, Node]) -> Tuple[List[Node], Dict[str, Node]]:
    for node in node_list:
        for child in ImportsIterator(node.path):
            # import x, y as z
            if isinstance(child, astroid.nodes.Import):
                for name, asname in child.names:
                    node.imports.append(
                        ImportItem(name=name, asname=asname)
                    )

            # from x import y
            elif isinstance(child, astroid.nodes.ImportFrom):
                base = child.modname

                for name, asname in child.names:
                    full_name = f"{base}.{name}" if base else name

                    node.imports.append(
                        ImportItem(name=full_name, asname=asname)
                    )

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
    dir_imports = resolve_dir_import(*parse_imports(*build_dir_imports(directory)))
    for node in dir_imports:
        print(f"{node.path}, {node.module}")
        for imp in node.imports:
            print(f"\t{imp}, node {imp.node}")


def get_function_scope(directory: str = ".", function: str = "."):
    pass
