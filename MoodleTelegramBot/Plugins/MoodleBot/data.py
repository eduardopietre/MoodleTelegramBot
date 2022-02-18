from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class CourseConfig:
    id: str
    name: str
    parser: str


@dataclass
class ScrappedResult:
    course_url: str
    course_id: str
    course_name: str
    texts: list[str]


class ParserTypes(Enum):
    ALL = auto()
    OLDER = auto()
    NEW = auto()
    SECTION = auto()
    OLDER_AND_SECTION = auto()

    @staticmethod
    def from_str(s: str):
        pairs = {
            "all": ParserTypes.ALL,
            "older": ParserTypes.OLDER,
            "new": ParserTypes.NEW,
            "section": ParserTypes.SECTION,
            "older and section": ParserTypes.OLDER_AND_SECTION,
        }

        if s not in pairs:
            raise NotImplementedError

        return pairs[s]

    @staticmethod
    def is_older_parser(parser_type):
        return parser_type == ParserTypes.OLDER or parser_type == ParserTypes.OLDER_AND_SECTION or parser_type == ParserTypes.ALL

    @staticmethod
    def is_sections_parser(parser_type):
        return parser_type == ParserTypes.SECTION or parser_type == ParserTypes.OLDER_AND_SECTION or parser_type == ParserTypes.ALL

    @staticmethod
    def is_new_parser(parser_type):
        return parser_type == ParserTypes.NEW or parser_type == ParserTypes.ALL
