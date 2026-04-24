when running python tests/test_1/a.py, it runs it as a top-level script without knowing any package context
so to solve add tests/test_1/__init__.py and then run python -m tests.test_1.a