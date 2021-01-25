import json
import datetime
import calendar

from bugcrawler.lang.Java import Java
from bugcrawler.lang.Scala import Scala
from bugcrawler.lang.Kotlin import Kotlin
from bugcrawler.lang.Groovy import Groovy
from bugcrawler.bugdb import DBInterface


class BugCrawler():
    LANGS_MAP = {
        'java': Java,
        'scala': Scala,
        'kotlin': Kotlin,
        'groovy': Groovy
    }

    def __init__(self, lang, filters, output=None):
        self.filters = self._get_filters(filters)
        self.lang = self._get_lang(lang, self.filters)
        self.dbcon = DBInterface(self.lang, self.filters)
        self.output = output

    def _get_lang(self, lang, filters):
        # gets an lang string, checks its validity
        # and returns an initialized lang object
        lang = lang.lower()
        if lang not in self.LANGS_MAP.keys():
            raise ValueError("Invalid lang")

        return self.LANGS_MAP[lang](filters)

    def _format_date(self, date):
        if len(date.split("-")) != 3:
            raise ValueError("Invalid date")

        year, month, day = date.split("-")
        dateobj = datetime.date(int(year), int(month), int(day))
        return calendar.timegm(dateobj.timetuple())

    def _get_filters(self, filters):
        # gets a filters script, checks its validity
        # and returns a filters dictionary
        formatted = filters
        return formatted

    def _do_output(self, data):
        to_print = json.loads(data)
        if not self.output:
            print(to_print)
            return
        with open(self.output, "w+") as f:
            f.write(to_print)

    def get(self):
        data = self.lang.retrieve()
        self.dbcon.create(data)
