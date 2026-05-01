from typing import Iterator

import astroid
from astroid import nodes


class ImportsIterator:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def yield_imports_from_file(self) -> Iterator[nodes.Import | nodes.ImportFrom]:
        if self.file_path.endswith(".py"):
            with open(self.file_path, 'r') as f:
                tree = astroid.parse(f.read())

            yield from tree.nodes_of_class((nodes.Import, nodes.ImportFrom))

    def __iter__(self):
        yield from self.yield_imports_from_file()
