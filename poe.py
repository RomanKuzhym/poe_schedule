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
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='turnoff-scheduleui-table')

    TITLE_CLASSES = {"turnoff-scheduleui-table-queue", "turnoff-scheduleui-table-subqueue"}
    ONOFF_MAP = {
        'light_1': PS.On,
        'light_2': PS.Off,
        'light_3': PS.Switch
    }

    table_body = table.find('tbody')
    if table_body is None:
        raise Exception("Failed to find tbody")

    rows = []

    for row_idx, tr in enumerate(table_body.find_all('tr')):
        row = []
        try:
            for td in tr.find_all('td'):
                cell_classes = set(c.strip() for c in td.get('class', []))

                # Skip titles
                if cell_classes & TITLE_CLASSES:
                    continue

                onoff = next((ONOFF_MAP[c] for c in cell_classes if c in ONOFF_MAP), None)
                if onoff is None:
                    raise Exception(f"Cannot recognize cell type. Classes: {cell_classes}")

                row.append(onoff)

            if len(row) != 24 * 2:
                raise Exception("Failed to recognize time series. Must be 24 * 2 values")
            rows.append(row)

        except Exception as e:
            log.exception(f"Failed to parse a time row #{row_idx}: {e}")
            continue

    if len(rows) != LINES * SUBLINES:
        log.warning(f"Unexpected number of power lines and sublines: {len(rows)}")
        log.warning(f"Expected number: {LINES}*{SUBLINES}={LINES*SUBLINES}")

    return rows


def inverted_sched(schedule):
    '''
        Returns a schedule with inverted On/Off values. 
    '''
    def invert_state(s):
        return {
            PS.On: PS.Off,
            PS.Off: PS.On, 
            PS.Switch: PS.Switch}[s]
    return [[invert_state(v) for v in qu] for qu in schedule]



def get_ranges(sched, invert):

    # Accept the Switch->On state as an On->On state
    # and Switch->Off as an Off->Off
    # Consider only one Switch state in between On/Off states
    sched = inverted_sched(sched) if invert else deepcopy(sched)
    for qu in sched:
        for i in range(len(qu)-1):
            if qu[i] == PS.Switch:
                qu[i] = qu[i+1]

    ranges = []
    for qu in range (LINES * SUBLINES):
        prevstep = sched[qu][0]
        rangestart = 0
        rg = []
        for i, timestep in enumerate(sched[qu]):
            if prevstep == PS.On and timestep == PS.Off:
                rangestart = i * 0.5
                prevstep = PS.Off
            elif prevstep == PS.Off and timestep == PS.On:
                prevstep = PS.On
                rangestop = i * 0.5
                rg.append([rangestart, rangestop])
        # off until 24:00
        if prevstep == PS.Off:
            rg.append([rangestart, 24])

        ranges.append(rg)

    return ranges
