import os
from astroid import nodes

from src.imports.import_from import (
    ImportFromSingle,
    ImportsIterator
)


def is_module_a_library(root_folder_path: str, module: str) -> bool:
    folder_entries = os.listdir(root_folder_path)
    root_folder_files: list[str] = [f for f in folder_entries if os.path.isfile(os.path.join(root_folder_path, f))]
    root_folder_dirs: list[str] = [d for d in folder_entries if os.path.isdir(os.path.join(root_folder_path, d))]
    if '.' not in module:
        if module not in root_folder_dirs and f'{module}.py' not in root_folder_files:
            return True
    return False


# look for {module}'s original path for module in root. e.g. root contains 'from a import b', we want the "true" path of 'a'
def get_module_abs_path(root: str, module: str) -> str:  # TODO:

    root_folder_path = os.path.dirname(root)
    if is_module_a_library(root_folder_path=root_folder_path, module=module):  # dont wander inside libraries
        return module

    new_root_folder_path: str = root_folder_path

    level: int = len(module) - len(module.lstrip('.'))
    if level > 0:  # maybe {module} is a parent folder
        module = module.lstrip('.')  # remove dots from left
        for _ in range(level):
            new_root_folder_path = os.path.dirname(new_root_folder_path)

    if '.' in module:  # maybe {module} is a child folder, e.g. root contains 'from a.b.c.d import e'
        # the code assumes no trailing '.' in {module}
        path_list: list[str] = module.split('.')
        new_root_folder_path = os.path.join(new_root_folder_path, *path_list[
                                                                   :-1])  # if root has path {r}, then new_root_folder_path is {r}/a/b/c

    # now that we found the folder path of the module, do we add f'{module}.py' or f'{module}\\__init__.py' to find the module?
    new_file_module_path = os.path.join(new_root_folder_path, f'{module}.py')
    new_folder_module_path = os.path.join(new_root_folder_path, f'{module}', '__init__.py')

    if os.path.isdir(os.path.join(new_root_folder_path, f'{module}')):
        if not os.path.isfile(new_folder_module_path):
            print(f"{module} should be at {root_folder_path}, but {new_folder_module_path} but has no __init__.py")
            exit(1)
        return new_folder_module_path
    elif os.path.isfile(new_file_module_path):
        return new_file_module_path
    else:
        print(f"{module} should be at {root_folder_path}, module {new_file_module_path} doesn't exist")
        exit(1)


# def resolve_import_from_single(history: list[ImportFromSingle], root: str, module: str):
#     module_path = get_module_abs_path(root, module)
#
#     for imp_single in history:
#         if imp_single.module_path == module_path:
#             print(f"circular import detected when importing {module} from {root}, saved history: {history}")
#             exit(1)
#
#     if '\\' not in module_path:
#         history.append(ImportFromSingle(module_path=module_path, module=module, name=module))
#         return module_path  # is a library
#
#     for module_def in DefinitionsIterator(module):
#         if module_def.name == module:
#             return
#
#             # check if {module} is in {root} by using {tree}
#     module_found = False
#     found_module: str = ""
#     found_imp: str = ""
#     found_imp_asname: str = ""
#
#     for rimp in ImportsIterator(root):
#         if isinstance(rimp, astroid.ImportFrom) and imp in rimp.names:
#             for alias in rimp.names:
#                 if (alias.asname is not None and alias.asname == imp) or (alias.asname is None and alias.name == imp):
#                     module_found = True  # for 'from a import b as c', module='a', name='b', asname='c'
#                     found_module = root
#                     found_imp = alias.name
#                     found_imp_asname = alias.asname
#
#     if not module_found:
#         print(f"module {module} used in {root} not found")
#         exit(1)
#
#     history.append(ImportFromSingle(module_path=module_path, module=module, name=found_imp, asname=found_imp_asname))
#     resolve_import_from_single(history=history, root=module_path, module=found_module, imp=found_imp)
#
#
# # what if 'from a import b,c,d' and inside a you see 'from ab import b; from ac import c; from ad import d;'?
# def resolve_import_from(root: str, imp: astroid.ImportFrom) -> ImportFrom:
#     result = ImportFrom(module=root, histories=[])
#     for alias in imp.names:
#         history = [ImportFromSingle(module_path=get_module_abs_path(root, imp.modname), module=imp.modname)]
#         resolve_import_from_single(history=history, root=root, module=imp.modname)
#         result.histories += history
#     return ImportFrom(module=module_abs_path, aliases=imp.names)
#

def iterate_resolve_over_directory(directory: str = ".") -> None:
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

    for file_path in directory_tree:
        it = ImportsIterator(file_path)
        for node in it:
            if isinstance(node, nodes.Import):
                print("import:", [name[0] for name in node.names])
            elif isinstance(node, nodes.ImportFrom):
                print("from:", node.modname, node.names)
