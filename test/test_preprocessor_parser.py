import pytest # NOQA
import logging
from pathlib import Path
from src.preprocessor.tokenizer import tokenize_file
from src.preprocessor.parser import Parser


class ParserTestData():
    @classmethod
    def from_file(cls, file: Path) -> "ParserTestData":
        with open(file) as file_contents:
            test_attributes = parse_test_attribute_line(file_contents.readline())
            test_name = test_attributes.pop("TESTNAME")
            value = tokenize_file(file_contents.read())

            return cls(file, test_name, test_attributes, value)

    def __init__(self, path: Path, name: str, attributes: dict, value):
        self.path = path
        self.name = name
        self.attributes = attributes
        self.value = value


def parse_test_attribute_line(line: str):
    QUALIFIER = "#pragma TEST"
    if not line.startswith(QUALIFIER):
        raise ValueError("Not a valid test attribute line")

    keyvalues = (x.split("=") for x in line[len(QUALIFIER):].strip().split())
    return {x[0]: x[1] for x in keyvalues}


def load_test_data():
    TEST_DATA_DIRECTORY = Path("./test/data/parser")
    assert TEST_DATA_DIRECTORY.is_dir()

    test_data = []

    for file in TEST_DATA_DIRECTORY.iterdir():
        try:
            test_data.append(ParserTestData.from_file(file))
            logging.info(f"Loaded test {test_data[-1].name}.")
        except ValueError:
            logging.warn(f"File {file} does not have a test line as it's first line. Ignoring.")
        except KeyError as e:
            logging.error(f"Error: Test {file} does not have a TESTNAME attribute.")
            raise e

    return test_data
