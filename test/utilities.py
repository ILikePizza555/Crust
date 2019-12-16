from typing import Iterable, Tuple

class NamedTestMatrix:
    """
    Stores tests and their names and provides a convient way of passing them to pytest.mark.parametrize
    """
    def __init__(self, arg_names: Iterable[str], test_data: Iterable[Tuple[str, ...]]):
        expected_data_length = len(arg_names) + 1

        for index, item in enumerate(test_data):
            if len(item) != expected_data_length:
                raise ValueError(f"Item {index} in test_data has an invalid length. Expected {expected_data_length}, got {len(item)}. Please ensure that test_data parameter is an iterable begnning with the test name and containing values for every item in arg_names.")

        self._arg_names = arg_names
        self._test_data = test_data

    @property
    def test_count(self):
        return len(self._test_data)

    @property
    def test_names(self):
        return tuple(x[0] for x in self._test_data)

    @property
    def arg_names(self):
        return self._arg_names
    
    @property
    def arg_values(self):
        return tuple(x[1:] for x in self._test_data)
