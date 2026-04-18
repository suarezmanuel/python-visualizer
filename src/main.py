# create a graph in memory, an adjacency list
from iterators import TreeAbstractIterator
from dataclasses import dataclass, field
import re
import graphviz

def tree(folder_path, **kwargs):
    if folder_path == "":
        return
    
    @dataclass
    class CustomState(TreeAbstractIterator.TreeState):
        lines_arr: list[bool] = field(default_factory=list)
        paddings: list[int] = field(default_factory=list)
    
    def before(s):
        prefix = ""
        for j in range(len(s.paddings)):
            if s.lines_arr[j]:
                prefix += '│' + ' '*(s.paddings[j]-1)
            else:
                prefix += ' '*s.paddings[j]
        prefix += '└' + '─'*7
        print(f"{prefix}{s.f}")

    def on_node(s):
        does_parent_have_next=s.i < (len(s.files)-1)
        s.lines_arr.append(does_parent_have_next)
        parent_str_len = 8+len(s.f)
        s.paddings.append(parent_str_len)

    root = str.split(folder_path, '/').pop()
    print(root)
    titer = TreeAbstractIterator(folder_path, before=before, on_node=on_node, state=CustomState(lines_arr=[False], paddings=[len(root)]), **kwargs)
    for _ in titer:
        pass

def get_leaves(folder_path, **kwargs):
    titer = TreeAbstractIterator(folder_path, **kwargs)
    return [name for name, is_node in titer if not is_node]

@dataclass
class ImportType:
    module_name: str = ""                # import os
    module_alias: str | None = None      # import pandas as pd
    sub_module: str | None = None        # from datetime import datetime
    sub_module_alias: str | None = None  # from datetime import datetime as dt

    def __repr__(self) -> str:
        BOLD = '\033[1m'
        DLOB = '\033[0m'
        out = "<"
        if self.module_name:
            out += f"module_name: {BOLD}{self.module_name}{DLOB}"
        if self.module_alias:
            out += f", module_alias: {BOLD}{self.module_alias}{DLOB}"
        if self.sub_module:
            out += f", sub_module: {BOLD}{self.sub_module}{DLOB}"
        if self.sub_module_alias:
            out += f", sub_module_alias: {BOLD}{self.sub_module_alias}{DLOB}"
        out += ">\n"
        return out

def get_file_imports(file_name):

    imports: list[ImportType] = []
    IMPORT_X = "^import\\s+([\\w ]+\\w+)"
    FROM_X_IMPORT_LIST = "^from[ ]+(\\w+)[ ]+import[ ]+([\\w, ]+)"
    Y_AS_Z = "(\\w+)[ ]+as[ ]+(\\w+)"

    # i want to make a state machine for this, with enums
    with open(file_name, 'r', encoding='latin-1') as file:
        for line in file:
            match = re.search(IMPORT_X, line)
            if match:
                module = match.group(1)                
                sub_match = re.search(Y_AS_Z, module)
                if not sub_match and ' as ' in module:
                    continue
                if sub_match:
                    module = sub_match.group(1)
                    alias = sub_match.group(2)
                    imports.append(ImportType(module_name=module, module_alias=alias))
                else:
                    imports.append(ImportType(module_name=module))
            else: 
                match = re.search(FROM_X_IMPORT_LIST, line)
                if match:
                    module = match.group(1)
                    sub_modules = match.group(2).split(',')

                    for sub_module in sub_modules:
                        sub_match = re.search(Y_AS_Z, sub_module)
                        if not sub_match and ' as ' in sub_module:
                            continue
                        
                        if sub_match:
                            sub_module = sub_match.group(1)
                            alias = sub_match.group(2)
                            imports.append(ImportType(module_name=module, sub_module=sub_module, sub_module_alias=alias))
                        else:
                            sub_module = sub_module.replace(' ', '') # remove unwanted spaces between the commas if doesnt have alias
                            imports.append(ImportType(module_name=module, sub_module=sub_module))
    return imports

def build_adjacency_list(folder_path) -> dict[str, list[ImportType]]:
    leaves = get_leaves(folder_path, FULL_PATHS=True)
    modules_dict: dict[str, list[ImportType]] = {}
    for l in leaves:
        if l.endswith('.py'):
            module_name = l.split('/')[-1]
            print(module_name)
            module_imports = get_file_imports(l)
            modules_dict[module_name] = module_imports
            for imp in module_imports:
                if imp.module_name not in modules_dict:
                    modules_dict[imp.module_name] = []
    return modules_dict

def create_graph(folder_path):

    modules_dict: dict[str, list[ImportType]] = build_adjacency_list(folder_path)

    f = graphviz.Digraph('my_graph', filename='fsm.gv', engine='sfdp')

    f.attr(
        overlap='false', # Crucial: prevents nodes from sitting on top of each other
        fontname='Helvetica',
        fontsize='20',    # Bigger labels for a bigger graph
        outputorder="edgesfirst",
        concentrate="true"
    )

    f.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue', fontsize='16')

    for module_name in modules_dict.keys():
        f.node(module_name)

    for module_name in modules_dict.keys():
        for imp in modules_dict[module_name]:
            f.edge(module_name, imp.module_name)

    f.view()

# tree("/Users/manuel/Code/minecraft", RECURSE_HIDDEN=True)
create_graph("/Users/manuel/Code/visualizer/lib/python3.13/site-packages/pip")
# print(get_leaves("/Users/manuel/Code/visualizer", MAX_DEPTH=0, FULL_PATHS=False))