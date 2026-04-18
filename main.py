# create a graph in memory, an adjacency list
from iterators import TreeAbstractIterator
from dataclasses import dataclass, field

def tree(folder_path, MAX_DEPTH=-1):
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
                prefix += '|' + ' '*(s.paddings[j]-1)
            else:
                prefix += ' '*s.paddings[j]
        prefix += 'L' + '_'*7
        print(f"{prefix}{s.f}")

    def on_node(s):
        does_parent_have_next=s.i < (len(s.files)-1)
        s.lines_arr.append(does_parent_have_next)
        parent_str_len = 8+len(s.f)
        s.paddings.append(parent_str_len)

    def on_leaf(s):
        pass

    root = str.split(folder_path, '/').pop()
    print(root)
    titer = TreeAbstractIterator(folder_path, MAX_DEPTH=MAX_DEPTH, before=before, on_node=on_node, on_leaf=on_leaf, state=CustomState(lines_arr=[False], paddings=[len(root)]))
    for _ in titer:
        pass

    # root = str.split(folder_path, '/').pop()
    # print(root)
    # _tree(depth=0, lines_arr=[0], paddings=[len(root)], folder_path=folder_path)

def get_leaves(folder_path):
    titer = TreeAbstractIterator(folder_path)
    return [name for name, is_node in titer if not is_node]

def find_references(file_name, folder_path):
    pass
    
def build_adjacency_list(folder_path):
    leaves = get_leaves(folder_path)
    list = {l:[] for l in leaves}
    # list = populate_adjacency_list(list, folder_path)
    return list


tree("/Users/manuel/Code/visualizer", MAX_DEPTH=0)

# print(get_leaves("/Users/manuel/Code/visualizer/test"))

# titer = TreeAbstractIterator("/Users/manuel/Code/visualizer", MAX_DEPTH=0, on_leaf=lambda state: state.update({"count": state["count"]+1}), on_node=lambda *args: None, state={"count": 0})
# for f in titer:
#     pass
# print(titer.state)