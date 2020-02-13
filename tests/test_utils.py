import sys
from pathlib import Path

import pytest
from pyrsched.server.utils import check_search_path, resolve_module_file

class TestUtils:
    def test_search_path(self):
        root_path = Path(".").resolve()
        new_path = Path("./some_testpath/sub_path/testfile.txt")
        expected_path = (root_path / new_path).parent
        check_search_path(new_path)
        assert sys.path[0] == str(expected_path)

    def test_resolve_module_path(self):
        root_path = Path(".").resolve()
        search_path = Path("./tests/testdata/scheduler_config.py")
        expected = root_path / search_path
        module_file = resolve_module_file(str(search_path))
        assert module_file == expected.resolve()

    def test_resolve_module_path_not_found(self):
        root_path = Path(".").resolve()
        search_path = Path("./tests/testdata/nonexistent_gibberish.py")
        with pytest.raises(FileNotFoundError):  
            module_file = resolve_module_file(str(search_path)) 
