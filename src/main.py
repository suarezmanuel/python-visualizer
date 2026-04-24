import ast
import os
from typing import Iterator
from dataclasses import dataclass

class ImportsIterator:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def yield_imports_from_file(self) -> Iterator[ast.Import | ast.ImportFrom]:
        with open(self.file_path, 'r') as f:
            tree = ast.parse(f.read())
        for node in tree.body:
            if isinstance(node, (ast.ImportFrom, ast.Import)):
                yield node

    def __iter__(self):
        yield from self.yield_imports_from_file()

class Definition:
    pass

@dataclass
class LibDefinition(Definition):
    module: str
    def_name: str

class ModuleDefinition(Definition):
    folder: str
    module: str
    def_name: str

def is_module_a_library(root_folder_dirs: list[str], root_folder_files: list[str], module: str) -> bool:
    if '.' not in module:
        if module not in root_folder_dirs and f'{module}.py' not in root_folder_files:
            return True
    return False
        
# start from {module}, and look for {imp}'s absolute path
def get_module_abs_path(root_folder_path: str, level: int, module:str, imp: str) -> tuple[str, bool]:
    
    new_root_folder_path: str = root_folder_path

    if level > 0: # maybe {imp} is in a parent folder
        module = module.lstrip('.') # remove dots from left
        path_list: list[str] = root_folder_path.split('\\')
        new_root_folder_path: str = '\\'.join(path_list[slice(len(path_list)-level+1)]) # make the path shorter depending on prefix '.'

    if '.' in module: # maybe {imp} is in a child folder, e.g. 'from a.b.c.d import e' 
        # the code assumes no trailing '.' in {module}
        path_list: list[str] = imp.split('.')
        new_root_folder_path = new_root_folder_path + '\\'.join(path_list[slice(len(path_list)-1)]) # we dont want to include f'{imp}'

    # now that we found the folder path of the module with imp, do we add f'{module}.py' or f'{module}\\__init__.py' to find the module?
    new_file_module_path = new_root_folder_path + f'\\{module}.py'
    new_folder_module_path = new_root_folder_path + f'\\{module}\\__init__.py'
    
    if os.path.isdir(new_root_folder_path + f'\\{module}'):
        if not os.path.isfile(new_folder_module_path):
            print(f"{imp} imported from {module} at {root_folder_path}, but {new_folder_module_path} but has no __init__.py")
            exit(1)
        return new_folder_module_path
    elif os.path.isfile(new_file_module_path):
        return new_file_module_path
    else: 
        print(f"{imp} imported from {module} at {root_folder_path}, module {new_file_module_path} doesn't exist")
        exit(1)            

# solves imports of type 'from module import imp' of a module 'root'.
def resolve_imp(root_folder_path: str, root_folder_dirs: list[str], root_folder_files: list[str], level: int, root: str, module: str, imp: str) -> Definition:

    if is_module_a_library(root_folder_dirs=root_folder_dirs, root_folder_files=root_folder_files, module=module): # dont wander inside libraries
        return LibDefinition(module=imp, def_name=imp) # module_abs_path is 'os' for 'from os import time'
    
    module_abs_path = get_module_abs_path(root_folder_path=root_folder_path, level=level, module=module, imp=imp)
    
    print(f'{imp} in {root_folder_path}\\{root} imported from {module_abs_path}')

def resolve_import_from(root_folder_path:str, root_folder_dirs: list[str], root_folder_files: list[str], root: str, imp: ast.ImportFrom):
    for alias in imp.names:
        resolve_imp(root_folder_path=root_folder_path, root_folder_dirs=root_folder_dirs, root_folder_files=root_folder_files, level=imp.level, root=root, module=imp.module, imp=alias.name)
        # use alias.asname maybe

folder_abs_path = "C:\\Users\\manue\\Documents\\Code\\python-visualizer\\tests"
# TODO: write tests for every fucking function
# assumes 
# - absolute folder path
# - libs are imports who dont have a .py file locally, or a folder module locally
# - all imported libs exist
# - no trailing '.' in {imp}

# solves 'from X import Y', but what if 'import X;, X.Y'?
for root, dirnames, files in os.walk(folder_abs_path):
    for file in files:
        if not file.endswith('.py'): continue
        file_path = f'{root}\\{file}'
        for imp in ImportsIterator(file_path):
            if isinstance(imp, ast.ImportFrom):
                resolve_import_from(root_folder_path=root, root_folder_dirs=dirnames, root_folder_files=files, root=file, imp=imp)