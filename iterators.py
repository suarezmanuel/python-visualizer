from copy import deepcopy
from dataclasses import dataclass, field
import os
from typing import NamedTuple

class TreeAbstractIterator():

    def do_nothing(*args):
        pass

    @dataclass
    class TreeState:
        i: int = 0
        f: str = ""
        files: list[str] = field(default_factory=list)

    class YieldResult(NamedTuple):
        name: str
        is_node: bool

    def __init__(self, root_path, MAX_DEPTH=-1, RECURSE_HIDDEN=False, before=None, on_node=None, on_leaf=None, state=None):
        self.root_path = root_path
        self.MAX_DEPTH = MAX_DEPTH
        self.LIMIT_DEPTH = MAX_DEPTH != -1
        self.RECURSE_HIDDEN = RECURSE_HIDDEN
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
            if os.path.isdir(f_path) and (self.RECURSE_HIDDEN or '.' not in f_path):
                save_state = deepcopy(self.state)
                self.on_node(self.state)
                yield self.YieldResult(name=f, is_node=True)
                yield from self.recurse(depth=depth+1, folder_path=f_path)
                self.state = save_state # so actual recursion can happen
            else:
                self.on_leaf(self.state)
                yield self.YieldResult(name=f, is_node=False)
    
    def __iter__(self):
        yield from self.recurse(0, self.root_path)