import requests
from typing import Any
from bs4 import BeautifulSoup
from .data import ParserTypes, ScrappedResult


class UrlScrapper:

    def __init__(self, session: requests.Session, course_url: str, course_id: str, course_name: str,
                 parser_type: ParserTypes):
        self.session = session
        self.course_url = course_url
        self.course_id = course_id
        self.course_name = course_name

        self.use_older_parser = ParserTypes.is_older_parser(parser_type)
        self.use_sections_parser = ParserTypes.is_sections_parser(parser_type)
        self.use_new_parser = ParserTypes.is_new_parser(parser_type)

        self.checked_urls = set()

    def scrapper(self, url: str) -> ScrappedResult:
        self.checked_urls.add(url)

        req = self.session.get(url)
        if req.status_code == 200:
            soup = BeautifulSoup(req.text, "html.parser")

            course_contents = soup.find_all("div", class_="course-content")
            if len(course_contents) != 1:
                raise AssertionError("Error, invalid credentials: len(course_contents) != 1")

            texts = []

            topics_elems = course_contents[0].find_all("ul", class_="topics")
            if len(topics_elems) >= 1:
                if self.use_older_parser:  # old style
                    for topic_elem in topics_elems:
                        texts.extend(self.parse_old(topic_elem))
                if self.use_sections_parser:  # check sections
                    texts.extend(self.parse_sections(topics_elems[0]))
            elif len(topics_elems) == 0:
                if self.use_new_parser:  # new style
                    texts.extend(self.parse_new(course_contents[0]))

            return ScrappedResult(url, self.course_id, self.course_name, texts)
        else:
            print(f"Error, URL {url} returned status code {req.status_code}")

    def parse_old(self, topics_elem: Any) -> list[str]:
        lis = topics_elem.find_all("li")
        if len(lis) <= 0:
            raise AssertionError("Error, maybe invalid credentials? len(lis) <= 0")

        texts = []
        for li in lis:
            contents = li.find_all("div", class_="content")
            if len(contents) > 0:
                text = contents[0].text
                texts.append(text)

        return texts

    def parse_sections(self, topics_elem: Any) -> list[str]:
        section_name = topics_elem.find_all("h3", class_="sectionname")
        section_title = topics_elem.find_all("h4", class_="section-title")

        sections = section_name + section_title

        texts = []
        for sec in sections:
            for a in sec.find_all('a', href=True):
                href = a['href']
                if href not in self.checked_urls:
                    print(f"[i] Recursively checking: {href}")
                    texts.extend(self.scrapper(href).texts)

        return texts

    def parse_new(self, course_content: Any) -> list[str]:
        texts = []

        for content in course_content.find_all("div", class_="content"):
            activities = content.find_all("li", class_="activity")
            for activity in activities:
                text = activity.text
                texts.append(text)

        for a in course_content.find_all('a', href=True):
            href = a['href'].replace("§ion=", "&section=")
            if self.course_url in href and href not in self.checked_urls:
                print(f"[i] Recursively checking: {href}")
                texts.extend(self.scrapper(href).texts)

        return texts
