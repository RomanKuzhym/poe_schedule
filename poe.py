import argparse
import copy
import datetime
import requests

import polar_plot
from poe_parse import PowerState, LINES, SUBLINES, parse as parse_schedule
from indentprint import IndentPrint

def fetch_schedule_html(date) -> str:
    URL = "https://www.poe.pl.ua/customs/newgpv-info.php"

    headers = {
      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    datestr = date.strftime('%d-%m-%Y')
    resp = requests.post(URL, data=f"seldate=%7B%22date_in%22%3A%22{datestr}%22%7D", headers=headers)
    return resp.text


def get_ranges(sched):
    ranges = []
    for qu in range (LINES * SUBLINES):
        prevstep = sched[qu][0]
        rangestart = 0
        rg = []
        for i, timestep in enumerate(sched[qu]):
            if prevstep == PowerState.On and timestep == PowerState.Off:
                rangestart = i * 0.5
                prevstep = PowerState.Off
            elif prevstep == PowerState.Off and timestep == PowerState.On:
                prevstep = PowerState.On
                rangestop = i * 0.5
                rg.append([rangestart, rangestop])
        # off until 24:00
        if prevstep == PowerState.Off:
            rg.append([rangestart, 24])

        ranges.append(rg)

    return ranges


def print_time_ranges(time_ranges):
    """Print one schedule for a subline.
    Args:
        time_ranges (list[list[int]]): list of pairs of floats from 0 to 24 
            (outage start and stop respectively).
    """
    for r in time_ranges:
        (h_from, m_from), (h_to, m_to) = divmod(r[0], 1), divmod(r[1], 1)
        print(f"{h_from:02.0f}:{60 * m_from:02.0f} - {h_to:02.0f}:{60 * m_to:02.0f}")


def print_lines(schedule, line_num=None, subline_num=None):
    selected_lines = [*range(0, LINES)] if line_num is None else [line_num]
    selected_sublines = [*range(0, SUBLINES)] if subline_num is None else [subline_num]

    for i in selected_lines:
        for j in selected_sublines:
            print(f"{i+1} черга {j+1} підчерга:")
            with IndentPrint():
                print_time_ranges(schedule[i*SUBLINES + j])

def print_schedule(schedule, date, line, subline, inverted=False):

    # Accept the Switch->On state as an On->On state
    # and Switch->Off as an Off->Off
    # Consider only one Switch state in between On/Off states
    sched = copy.deepcopy(schedule)
    for qu in sched:
        for i in range(len(qu)-1):
            if qu[i] == PowerState.Switch and qu[i+1] != PowerState.Switch:
                qu[i] = qu[i+1]

    if inverted:
        def invert_state(s):
            return {
                PowerState.On: PowerState.Off,
                PowerState.Off: PowerState.On, 
                PowerState.Switch: PowerState.Switch}[s]
        sched = [[invert_state(v) for v in qu] for qu in sched]

    print (f"Відключення електроенергії за {date}")
    with IndentPrint():
        print_lines(get_ranges(sched), line, subline)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--line", 
        help="Номер черги",
        type=int, 
        choices=range(1, LINES+1)
    )
    parser.add_argument(
        "--subline", 
        help="Номер підчерги",
        type=int, 
        choices=range(1, SUBLINES+1))
    parser.add_argument(
        "--date", 
        help="Дата РРРР-ММ-ДД",
        type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), 
        default=datetime.datetime.now().date())
    parser.add_argument(
        "--inverted", 
        help="Показувати графік увімкнення", 
        action='store_true',
        default=False)
    parser.add_argument(
        "--show_plot", 
        help="Діаграма", 
        action='store_true',
        default=False)
    parser.add_argument(
        "--tomorrow",
        help="Графік на завтра від заданої дати",
        action='store_true',
        default=False)

    return parser.parse_args()

def fetch_schedule(date):
    try:
       text = fetch_schedule_html(date)
    except Exception as e:
        print(f"Не вдалося завантажити дані: {e}")
        exit(1)
    try:
        sched = parse_schedule(text)
        return sched
    except Exception as e:
        print("Помилка обробки даних")
        with IndentPrint():
            print(e)
            print(text)
        exit(2)


def main():

    args = parse_args()

    date = args.date
    if args.tomorrow:
        date += datetime.timedelta(days=1)
    if args.line is not None:
        args.line -= 1
    if args.subline is not None:
        args.subline -= 1

    schedule = fetch_schedule(date)

    print_schedule(schedule, date, arg.line, arg.subline, arg.inverted)

    if args.show_plot:
        if args.subline is None or args.line is None:
            raise Exception("To show a plot specify line and subline numbers")
        polar_plot.show_schedule(args.line, args.subline, schedule)


if __name__ == '__main__':
    main()
