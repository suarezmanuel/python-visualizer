# create a graph in memory, an adjacency list
from iterators import TreeAbstractIterator
from dataclasses import dataclass, field
import re
import graphviz
from a import o

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

    # first a dictionary that matches paths to Module's is created, fills each Module's name, path
    # then create a tree; a root Module that represents the project, fill each node's children
    # then pass the tree in post-order, and fill the imports to be SourceModules; the modules with the definition, they might have is_local=False
    # EXTRA: fill a queue with imports to be deciphered, and then create a dictionary that will match those imports with their aliases
    # 
    # 
    # Module: name, path, is_local, imports, children
    #
    # create all Modules without imports, fill name, path.
    # scan again, fill is_local, imports, children if is a folder scan for __init__.py
    #
    # from .a.b.c.d import e
    # convert '.a.b.c.d' into a path, link the module
    #
    # from X import Y
    #
    # Module -> SourceModule
    #
    # we want the most direct connection, look inside modules[X], and find who imports Y, or Z as Y until no more imports. 
    # find_origin(start_module: Module, import: str, path_taken: list[Module])
    # if start_module in path_taken: print('circular import detected'); exit(1)
    #
    #
    #
    # later on, check if Y in from X import Y as Z, is an object or not.
    #  

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

class ImportsGraph:

    LIBS_NOT_TO_INCLUDE: list[str] = ["typing"]
    GRAPH_NAME = 'my_graph'
    FILE_NAME = 'graph.gv'
    ENGINE = 'sfdp'
    GRAPH_ATTRIBUTES = {
        'overlap': 'false', 
        'fontname': 'Helvetica', 
        'fontsize': '20', 
        'outputorder': "edgesfirst", 
        'concentrate': "true"
    }
    NODE_ATTR = {
        'shape': 'box', 
        'style': 'rounded,filled', 
        'fontsize': '16'
    }
    LIB_NODE_COLOR = 'lightblue'
    MODULE_NODE_COLOR = 'orange'

    def __init__(self, folder_path: str):
        self._create_graph(folder_path)

    def _create_graph(self, folder_path):
        modules_dict: dict[str, list[ImportType]] = build_adjacency_list(folder_path)
        # TODO: make an adjacency list cleaner, in case of a local file importing an alias from another local file. 
        
        orphan_modules = []
        for module_name in modules_dict.keys():
            is_orphan = True
            for imp in modules_dict[module_name]:
                if imp.module_name not in self.LIBS_NOT_TO_INCLUDE and imp.module_alias not in self.LIBS_NOT_TO_INCLUDE and imp.sub_module not in self.LIBS_NOT_TO_INCLUDE and imp.sub_module_alias not in self.LIBS_NOT_TO_INCLUDE:
                    is_orphan = False
            for other_module_name in modules_dict.keys():
                for imp in modules_dict[other_module_name]:
                    if module_name == imp.module_name or module_name == imp.module_alias or module_name == imp.sub_module or module_name == imp.sub_module_alias:
                        is_orphan = False
            if is_orphan == True:
                orphan_modules.append(module_name)

                
        used_names = [module_name for module_name in orphan_modules]
        libs = [module_name for module_name in modules_dict.keys() if module_name not in used_names and '.py' not in module_name]
        used_names += [module_name for module_name in libs]
        project_modules = [module_name for module_name in modules_dict.keys() if module_name not in used_names and '.py' in module_name]
        used_names += [module_name for module_name in project_modules]
        assert len(used_names) == len(modules_dict) 
        f = graphviz.Digraph(self.GRAPH_NAME, filename=self.FILE_NAME, engine=self.ENGINE)

        f.attr(**self.GRAPH_ATTRIBUTES)

        
        # f.attr('node', fillcolor=self.LIB_NODE_COLOR, **self.NODE_ATTR)
        f.node('orphan_anchor', style='invis', label='', width='0')
        for module_name in orphan_modules:
            f.node(module_name)
            f.edge('orphan_anchor', module_name)

        f.attr('node', fillcolor=self.LIB_NODE_COLOR, **self.NODE_ATTR)
        for lib_name in libs:
            if lib_name in self.LIBS_NOT_TO_INCLUDE: continue
            f.node(lib_name)

        f.attr('node', fillcolor=self.MODULE_NODE_COLOR, **self.NODE_ATTR)
        for module_name in project_modules:
            f.node(module_name)

        for imp_a_module_name in modules_dict.keys():
            for imp_b in modules_dict[imp_a_module_name]:
                if imp_b.module_name in self.LIBS_NOT_TO_INCLUDE: continue
                if imp_a_module_name in project_modules:
                    if module_name in project_modules or module_name in libs:
                        f.edge(imp_a_module_name, imp_b.module_name)

        f.view()


# tree("/Users/manuel/Code/minecraft", RECURSE_HIDDEN=True)
ImportsGraph("C:/Users/manue/Documents/Code/python-visualizer/pyAGE")
# print(get_leaves("/Users/manuel/Code/visualizer", MAX_DEPTH=0, FULL_PATHS=False))