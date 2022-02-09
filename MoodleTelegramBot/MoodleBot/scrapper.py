import requests
import re
import concurrent.futures
from .data import ParserTypes, ScrappedResult, CourseConfig
from .urlscrapper import UrlScrapper
from .database import DatabaseConnection


# Small value in an attempt to reduce memory usage.
MAX_WORKERS = 2


def do_scrapper(session: requests.Session, course_url: str, course_id: str, course_name: str,
                parser_type_str: str) -> ScrappedResult:
    parser_type = ParserTypes.from_str(parser_type_str)
    scrapper = UrlScrapper(session, course_url, course_id, course_name, parser_type)
    return scrapper.scrapper(course_url)


class MoodleScraper:

    def __init__(self, url: str, database_file: str, username: str, password: str):
        self.username = username
        self.password = password
        self.base_url = url
        self.database_file = database_file
        self.log_parts = []
        self.found = False


    def login(self, session):
        login_url = f"{self.base_url}login/index.php"


        get_req = session.get(login_url)

        cookies = get_req.cookies.get_dict()

        pattern = '<input type="hidden" name="logintoken" value="\w{32}">'
        token = re.findall(pattern, get_req.text)
        token = re.findall("\w{32}", token[0])

        payload = {
            "logintoken": token,
            "username": self.username,
            "password": self.password,
        }

        session.post(login_url, cookies=cookies, data=payload)


    def scraper(self, courses: list[CourseConfig]) -> str:
        with requests.Session() as session:
            self.login(session)

            with concurrent.futures.ThreadPoolExecutor(max_workers=max(len(courses), MAX_WORKERS)) as executor:
                futures = (
                    executor.submit(
                        do_scrapper,
                        session,
                        f"{self.base_url}course/view.php?id={c.id}",
                        c.id,
                        c.name,
                        c.parser
                    )
                    for c in courses
                )
                for future in concurrent.futures.as_completed(futures):
                    try:
                        data = future.result()
                        self.update_database(data.course_id, data.course_name, data.texts)
                    except Exception as exc:
                        print(f"Error at future completion:\n{exc}")

        return self.generate_log()

    def update_database(self, course_id: str, course_name: str, texts: list[str]) -> None:
        table_name = f"courseid_{course_id}"  # must not start with a number.

        with DatabaseConnection(self.database_file) as db:
            if not DatabaseConnection.exists_database_table(db, table_name):
                db.execute(f"CREATE TABLE {table_name} (content TEXT UNIQUE)")

            db.execute(f"SELECT * FROM {table_name}")
            results = set([r[0] for r in db.fetchall()])

            added_course_name = False

            for text in texts:
                if (text not in results) and (text not in self.log_parts):
                    db.execute(f"INSERT INTO {table_name} VALUES (?)", (text,))

                    if not added_course_name:
                        self.log_parts.append(f"Matéria: {course_name}")
                        added_course_name = True
                        self.found = True

                    self.log_parts.append(text)

    def generate_log(self) -> str:
        def clean_extra(text: str) -> str:
            replace_pairs = [  # list, preserve order
                ["completo", ""],
                ["Não concluído", ""],
                ["Progresso do curso", ""],
                ["Seu progresso", ""],
                ["\n\n", "\n"],
            ]
            for pair in replace_pairs:
                while pair[0] in text:
                    text = text.replace(pair[0], pair[1])

            return text.strip()

        return "\n---------\n".join([f"\"{clean_extra(t)}\"" for t in self.log_parts])
