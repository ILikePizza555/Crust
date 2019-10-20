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

            return cls(file, test_name, test_attributes)

    def __init__(self, path: Path, name: str, attributes: dict):
        self.path = path
        self.name = name
        self.attributes = attributes


def parse_test_attribute_line(line: str):
    QUALIFIER = "#pragma TEST"
    if not line.startswith(QUALIFIER):
        raise ValueError("Not a valid test attribute line")

    keyvalues = (x.split("=") for x in line[len(QUALIFIER):].strip().split())
    return {x[0]: x[1] for x in keyvalues}


def load_test_file(filepath) -> ParserTestData:
    try:
        test_data = ParserTestData.from_file(filepath)
        logging.info(f"Loaded test {test_data.name}.")
        return test_data
    except ValueError:
        logging.warn(f"File {filepath} does not have a test line as it's first line. Ignoring.")
    except KeyError as e:
        logging.error(f"Error: Test {filepath} does not have a TESTNAME attribute.")
        raise e


TEST_DATA_DIRECTORY = Path("./test/data/parser")
TEST_DATA = {test.name: test for test in (load_test_file(t) for t in TEST_DATA_DIRECTORY.iterdir())}