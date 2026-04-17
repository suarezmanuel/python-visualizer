from copy import deepcopy
from dataclasses import dataclass, field
import os

class TreeIterator():
    def __init__(self, root_path, MAX_DEPTH=-1):
        self.root_path = root_path
        self.MAX_DEPTH = MAX_DEPTH
        self.LIMIT_DEPTH = MAX_DEPTH != -1

    def recurse(self, depth, folder_path):
        if self.LIMIT_DEPTH and depth > self.MAX_DEPTH: return
        files = os.listdir(folder_path)
        for f in files:
            f_path = f"{folder_path}/{f}"
            if os.path.isdir(f_path):
                yield f,1
                yield from self.recurse(depth=depth+1, folder_path=f_path)
            else:
                yield f,0
    
    def __iter__(self):
        yield from self.recurse(0, self.root_path)

class TreeAbstractIterator():

    def do_nothing(*args):
        pass

    @dataclass
    class TreeState:
        i: int = 0
        f: str = ""
        files: list[str] = field(default_factory=list)

    def __init__(self, root_path, MAX_DEPTH=-1, before=None, on_node=None, on_leaf=None, state=None):
        self.root_path = root_path
        self.MAX_DEPTH = MAX_DEPTH
        self.LIMIT_DEPTH = MAX_DEPTH != -1
        self.before = before or (lambda _: None)
        self.on_node = on_node or (lambda _: None)
        self.on_leaf = on_leaf or (lambda _: None)
        self.state = state or self.TreeState()

    def recurse(self, depth, folder_path):
        if self.LIMIT_DEPTH and depth > self.MAX_DEPTH: return
        files = os.listdir(folder_path)
        for i, f in enumerate(files):
            f_path = f"{folder_path}/{f}"

            self.state.f = f
            self.state.i = i
            self.state.files = files

            self.before(self.state)
            if os.path.isdir(f_path):
                save_state = deepcopy(self.state)
                self.on_node(self.state)
                yield f,1
                yield from self.recurse(depth=depth+1, folder_path=f_path)
                self.state = save_state # so actual recursion can happen
            else:
                self.on_leaf(self.state)
                yield f,0
    
    def __iter__(self):
        yield from self.recurse(0, self.root_path)

class TreeLeafIterator():
    def __init__(self, root_path):
        self.root_path = root_path

    def recurse(self, folder_path):
        files = os.listdir(folder_path)
        for f in files:
            f_path = f"{folder_path}/{f}"
            if os.path.isdir(f_path):
                yield from self.recurse(f_path)
            else:
                yield f
    
    def __iter__(self):
        yield from self.recurse(self.root_path)