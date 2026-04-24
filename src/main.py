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

@dataclass
class ImportFromSingle:
    module_path: str
    module: str
    name: str
    asname: str | None

@dataclass
class ImportFrom:
    module: str
    histories: list[list[ImportFromSingle]]

    def __repr__(self):
        out: str = ""
        out += f"ImportFrom <module: {self.module}" + '\n'
        for history in self.histories:
            for imp in history:
                alias_string = f' as {imp.asname}' if imp.asname is not None else ''
                out += '\t' + f'from {imp.module} import {imp.name}{alias_string}' + '\n'
        out += ">"
        return out

def is_module_a_library(root_folder_path: str, module: str) -> bool:
    folder_entries = os.listdir(root_folder_path)
    root_folder_files: list[str] = [f for f in folder_entries if os.path.isfile(os.path.join(root_folder_path, f))]
    root_folder_dirs: list[str] = [d for d in folder_entries if os.path.isdir(os.path.join(root_folder_path, d))]
    if '.' not in module:
        if module not in root_folder_dirs and f'{module}.py' not in root_folder_files:
            return True
    return False
        
# look for {module}'s original path for module in root. e.g. root contains 'from a import b', we want the "true" path of 'a'
def get_module_abs_path(root: str, module: str) -> str: # TODO:

    root_folder_path = os.path.dirname(root)
    if is_module_a_library(root_folder_path=root_folder_path, module=module): # dont wander inside libraries
        return module
    
    new_root_folder_path: str = root_folder_path

    level: int = len(module) - len(module.lstrip('.'))
    if level > 0: # maybe {module} is a parent folder
        module = module.lstrip('.') # remove dots from left
        for _ in range(level):
            new_root_folder_path = os.path.dirname(new_root_folder_path)

    if '.' in module: # maybe {module} is a child folder, e.g. root contains 'from a.b.c.d import e' 
        # the code assumes no trailing '.' in {module}
        path_list: list[str] = module.split('.')
        new_root_folder_path = os.path.join(new_root_folder_path, *path_list[:-1]) # if root has path {r}, then new_root_folder_path is {r}/a/b/c

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
    
def resolve_import_from_single(history: list[ImportFromSingle], root: str, module: str, imp: str):
    module_path = get_module_abs_path(root, module)

    for imp_single in history:
        if imp_single.module_path == module_path:
            print(f"circular import detected when importing {module} from {root}, saved history: {history}")
            exit(1)

    if '\\' not in module_path:
        history.append(ImportFromSingle(module_path=module_path, module=module, name=module, asname=imp))
        return module_path # is a library 
    
    for module_def in DefinitionsIterator(module):
        if module_def.name == module:
            return 

    # check if {module} is in {root} by using {tree}
    module_found = False
    found_module: str = ""
    found_imp: str = ""
    found_imp_asname: str = ""

    for rimp in ImportsIterator(root):
        if isinstance(rimp, ast.ImportFrom) and imp in rimp.names:
            for alias in rimp.names:
                if (alias.asname is not None and alias.asname == imp) or (alias.asname is None and alias.name == imp):
                    module_found = True # for 'from a import b as c', module='a', name='b', asname='c'
                    found_module = root
                    found_imp = alias.name
                    found_imp_asname = alias.asname

    if not module_found:
        print(f"module {module} used in {root} not found")
        exit(1)
    
    history.append(ImportFromSingle(module_path=module_path, module=module, name=found_imp, asname=found_imp_asname))
    resolve_import_from_single(history=history, root=module_path, module=found_module, imp=found_imp)
    
# what if 'from a import b,c,d' and inside a you see 'from ab import b; from ac import c; from ad import d;'?
def resolve_import_from(root: str, imp: ast.ImportFrom) -> ImportFrom:
    result = ImportFrom(module=root, histories=[])
    for alias in imp.names:
        history = [ImportFromSingle(module_path=get_module_abs_path(root, imp.module), module=imp.module, name=imp.name, asname=imp.asname)]
        resolve_import_from_single(history=history, root=root, module=imp.module, imp=alias.name)
        result.histories += history
    return ImportFrom(module=module_abs_path, aliases=imp.names)

folder_abs_path = "C:\\Users\\manue\\Documents\\Code\\python-visualizer\\tests"
# TODO: write tests for every fucking function
# assumes 
# - absolute folder path
# - libs are imports who dont have a .py file locally, or a folder module locally
# - all imported libs exist
# - no trailing '.' in {imp}

# solves 'from X import Y', but what if 'import X;, X.Y'?
import pytest
import filecmp

@pytest.mark.parametrize("test_id", [i+1 for i in range(6)])
def test_resolve_import_from(test_id):
    project_root = 'C:\\Users\\manue\\Documents\\Code\\python-visualizer'
    test_folder = os.path.join(project_root, 'tests', f'test_{test_id}')
    correct_output = os.path.join(f'{test_folder}', 'compare', 'correct_output.txt')
    test_output = os.path.join(f'{test_folder}', 'compare', 'test_output.txt')
    Imports = []
    for root, dirnames, files in os.walk(test_folder):
        for file in files:
            if not file.endswith('.py'): continue
            file_path = os.path.join(f'{root}', f'{file}')
            for imp in ImportsIterator(file_path):
                if isinstance(imp, ast.ImportFrom):
                    Imports.append(resolve_import_from(root=root, imp=imp))
    
    with open(test_output, 'w') as f:
        for Import in Imports:
            f.write(f'{repr(Import)}\n')
    
    with open(test_output, 'r') as f:
        with open(correct_output, 'r') as g:
            assert f.read() == g.read()
    
pytest.main(["src/main.py"])