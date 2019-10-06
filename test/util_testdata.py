from typing import Generic, TypeVar, Iterable, List, Tuple
from .util_tokens import MockToken, tokenize_string


IT = TypeVar("IT")
ET = TypeVar("ET")


class TestData(Generic[IT, ET]):
    @classmethod
    def of_mock_tokens(cls, test_name: str, input_str: str, expected_tokens: tuple):
        return TestData(
            test_name,
            tokenize_string(input_str),
            tuple(MockToken(*x) for x in expected_tokens)
        )

    def __init__(self, name: str, input_data: IT, expected: ET):
        self.name = name
        self.input_data = input_data
        self.expected = expected
    
    def __repr__(self):
        return f"TestData(name={self.name}, input_data={self.input_data}, expected={self.expected})"


def convert_to_names(data_iterable: Iterable[TestData]) -> List[str]:
    return [x.name for x in data_iterable]


def convert_to_parameters(data_iterable: Iterable[TestData[IT, ET]]) -> List[Tuple[IT, ET]]:
    return [(x.input_data, x.expected) for x in data_iterable]
