from typing import Iterator
from dataclasses import dataclass

import astroid
from astroid import nodes


class ImportsIterator:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def yield_imports_from_file(self) -> Iterator[nodes.Import | nodes.ImportFrom]:
        with open(self.file_path, 'r') as f:
            tree = astroid.parse(f.read())

        yield from tree.nodes_of_class((nodes.Import, nodes.ImportFrom))

    def __iter__(self):
        yield from self.yield_imports_from_file()


@dataclass
class ImportFromSingle:
    module_path: str
    module: str
    name: str
    asname: str | None


# @dataclass
# class ImportFrom:
#     module: str
#     histories: list[list[ImportFromSingle]]
#
#     def __repr__(self):
#         out: str = ""
#         out += f"ImportFrom <module: {self.module}" + '\n'
#         for history in self.histories:
#             for imp in history:
#                 alias_string = f' as {imp.asname}' if imp.asname is not None else ''
#                 out += '\t' + f'from {imp.module} import {imp.name}{alias_string}' + '\n'
#         out += ">"
#         return out
