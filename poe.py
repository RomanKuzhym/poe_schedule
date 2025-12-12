from copy import deepcopy
from enum import IntEnum
import logging

from bs4 import BeautifulSoup
from requests import post

log = logging.getLogger(__name__)

LINES = 6
SUBLINES = 2

class PowerState(IntEnum):
    Off = 0
    Switch = 1
    On = 2

PS = PowerState


def fetch_schedule_html(date) -> str:
    URL = "https://www.poe.pl.ua/customs/newgpv-info.php"

    headers = {
      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    datestr = date.strftime('%d-%m-%Y')
    resp = post(URL, data=f"seldate=%7B%22date_in%22%3A%22{datestr}%22%7D", headers=headers)
    resp.raise_for_status()
    return resp.text


def parse(html_content) -> list[list[PS]]:
    """
    Parse the HTML table from the POE site and return a schedule
    as a list of lists of PowerState values.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='turnoff-scheduleui-table')
    if table is None:
        raise ValueError("Cannot find schedule table in HTML")

    tbody = table.find('tbody')
    if tbody is None:
        raise ValueError("Cannot find tbody in schedule table")

    TITLE_CLASSES = {"turnoff-scheduleui-table-queue", "turnoff-scheduleui-table-subqueue"}
    ONOFF_MAP = {'light_1': PS.On, 'light_2': PS.Off, 'light_3': PS.Switch}

    rows: list[list[PS]] = []

    for row_idx, tr in enumerate(tbody.find_all('tr')):
        try:
            line = [
                ONOFF_MAP[next(c for c in td.get('class', []) if c in ONOFF_MAP)]
                for td in tr.find_all('td')
                if not any(c in TITLE_CLASSES for c in td.get('class', []))
            ]

            if len(line) != 24 * 2:
                raise ValueError(f"Time series must have 48 values, got {len(line)}")

            rows.append(line)

        except Exception as e:
            log.error(f"Failed to parse row #{row_idx}: {e}")
            continue

    if len(rows) != LINES * SUBLINES:
        log.warning(f"Unexpected number of rows: {len(rows)} (expected {LINES}*{SUBLINES}={LINES*SUBLINES})")

    return rows


def inverted_sched(schedule):
    """
    Return a new schedule with On/Off values inverted. Switch stays the same.
    """
    invert_map = {PS.On: PS.Off, PS.Off: PS.On, PS.Switch: PS.Switch}
    return [[invert_map[state] for state in line] for line in schedule]


def get_ranges(schedule, invert=False):
    """
    Convert a schedule of PowerState into a list of on/off ranges per line/subline.
    Each range is [start_hour, end_hour].
    """
    sched = inverted_sched(schedule) if invert else deepcopy(schedule)
    
    # Normalize Switch states: treat Switch as the next state
    for line in sched:
        for i in range(len(line) - 1):
            if line[i] == PS.Switch:
                line[i] = line[i + 1]

    all_ranges = []

    for line in sched:
        line_ranges = []
        start = None
        for idx, state in enumerate(line):
            hour = idx * 0.5
            if state == PS.Off and start is None:
                start = hour
            elif state == PS.On and start is not None:
                line_ranges.append([start, hour])
                start = None

        # If the line ends while Off, extend to 24:00
        if start is not None:
            line_ranges.append([start, 24])

        all_ranges.append(line_ranges)

    return all_ranges

