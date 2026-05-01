import os

import pytest
import astroid

from src.imports.utils import (
    resolve_import_from
)

from src.imports.import_from import (
    ImportsIterator
)


# TODO: write tests for every fucking function
# assumes 
# - absolute folder path
# - libs are imports who dont have a .py file locally, or a folder module locally
# - all imported libs exist
# - no trailing '.' in {imp}


@pytest.mark.parametrize("test_id", [i + 1 for i in range(6)])
def test_resolve_import_from(test_id: int):
    project_root = '.'
    test_folder = os.path.join(project_root, 'tests', f'test_{test_id}')
    correct_output = os.path.join(f'{test_folder}', 'compare', 'correct_output.txt')
    test_output = os.path.join(f'{test_folder}', 'compare', 'test_output.txt')
    imports = []
    for root, dirnames, files in os.walk(test_folder):
        for file in files:
            if not file.endswith('.py'): continue
            file_path = os.path.join(f'{root}', f'{file}')
            for imp in ImportsIterator(file_path):
                if isinstance(imp, astroid.ImportFrom):
                    imports.append(resolve_import_from(root=root, imp=imp))

    with open(test_output, 'w') as f:
        for Import in imports:
            f.write(f'{repr(Import)}\n')

    with open(test_output, 'r') as f:
        with open(correct_output, 'r') as g:
            assert f.read() == g.read()
