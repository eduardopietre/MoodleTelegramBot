from dataclasses import dataclass
from .data import CourseConfig


@dataclass
class ScrapperConfig:
    notify: [str]
    database: str
    login_user: str
    login_pass: str
    base_url: str
    courses: [CourseConfig]

    @staticmethod
    def from_dict(d: dict, un_cypher):
        return ScrapperConfig(
            notify=d["notify"],
            database=d["database"],
            base_url=d["base_url"],
            login_user=un_cypher(d["login"]),
            login_pass=un_cypher(d["password"]),
            courses=[
                CourseConfig(
                    id=sub_d["id"],
                    name=sub_d["name"],
                    parser=sub_d["parser"]
                ) for sub_d in d["courses"]
            ]
        )

