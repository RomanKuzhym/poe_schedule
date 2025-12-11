import requests
import datetime
import argparse
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


def get_ranges(raw_sched):
    ranges = []
    for qu in range (LINES * SUBLINES):
        prevstep = PowerState.On
        rangestart = 0
        rg = []
        for i, timestep in enumerate(raw_sched[qu]):
            if prevstep == PowerState.On and timestep in (PowerState.Off, PowerState.Switch):
                rangestart = i * 0.5
                prevstep = PowerState.Off
            # Switches on usually at switching time
            elif prevstep == PowerState.Off and timestep in (PowerState.On, PowerState.Switch):
                rangestop = i * 0.5
                prevstep = PowerState.On
                rg.append([rangestart, rangestop])
        # off until 24:00
        if prevstep == PowerState.Off:
            rg.append([rangestart, 24])

        ranges.append(rg)

    return ranges


def print_schedule(ranges):
    """Print one schedule for a subline.
    Args:
        ranges (list[list[int]]): list of pairs of floats from 0 to 24 
            (outage start and stop respectively).
    """
    for r in ranges:
        (h_from, m_from), (h_to, m_to) = divmod(r[0], 1), divmod(r[1], 1)
        print(f"{h_from:02.0f}:{60 * m_from:02.0f} - {h_to:02.0f}:{60 * m_to:02.0f}")


def print_lines(ranges, line_num=-1, subline_num=-1):
    selected_lines = [*range(0, LINES)] if line_num == -1 else [line_num]
    selected_sublines = [*range(0, SUBLINES)] if subline_num == -1 else [subline_num]

    for i in selected_lines:
        for j in selected_sublines:
            print(f"{i+1} черга {j+1} підчерга:")
            with IndentPrint():
                print_schedule(ranges[i*SUBLINES + j])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--line", type=int, choices=range(1, LINES+1))
    parser.add_argument("--subline", type=int, choices=range(1, SUBLINES+1))
    parser.add_argument("--date", type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), default=datetime.datetime.now().date())
    parser.add_argument("--show_plot", action='store_true', default=False)
    parser.add_argument("--tomorrow", action='store_true', default=False)

    args = parser.parse_args()
 
    sel_line = -1
    sel_subline = -1
    date = args.date
    if args.line is not None:
        sel_line = args.line - 1
    if args.subline  is not None:
        sel_subline = args.subline - 1
    if args.tomorrow:
        date += datetime.timedelta(days=1)
    try:
       text = fetch_schedule_html(date)
       raw_data = parse_schedule(text)
    except Exception as e:
        print("Не вдалося завантажити дані")
        with IndentPrint():
            print(e)
            print(text)
        return

    ranges = get_ranges(raw_data)

    print (f"Відключення електроенергії за {date}")
    with IndentPrint():
        print_lines(ranges, sel_line, sel_subline)

    if args.show_plot:
        if args.subline is None or args.line is None:
            raise Exception("To show a plot specify line and subline numbers")
        line = args.line - 1
        subline = args.subline - 1
        polar_plot.show_schedule(line, subline, raw_data)


if __name__ == '__main__':
    main()
