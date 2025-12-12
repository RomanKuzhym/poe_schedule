import argparse
import copy
import datetime

import polar_plot
import poe
from poe_print import print_schedule

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--line", 
        help="Номер черги",
        type=int, 
        choices=range(1, poe.LINES+1)
    )
    parser.add_argument(
        "--subline", 
        help="Номер підчерги",
        type=int, 
        choices=range(1, poe.SUBLINES+1))
    parser.add_argument(
        "--date", 
        help="Дата РРРР-ММ-ДД",
        type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'), 
        default=datetime.datetime.now().date())
    parser.add_argument(
        "--invert", 
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
       text = poe.fetch_schedule_html(date)
    except Exception as e:
        log.error(f"Не вдалося завантажити дані: {e}")
        exit(1)
    try:
        sched = poe.parse(text)
        return sched
    except Exception as e:
        log.error("Помилка обробки даних")
        with IndentPrint():
            log.error(e)
            log.error(text)
        exit(2)


def main():

    args = parse_args()

    date = args.date
    if args.tomorrow:
        date += datetime.timedelta(days=1)
    # adapt to [0, LINES/SUBLINES) range
    if args.line is not None:
        args.line -= 1
    if args.subline is not None:
        args.subline -= 1

    schedule = fetch_schedule(date)

    print_schedule(poe.get_ranges(schedule, args.invert), date, args.line, args.subline)
    if args.show_plot:
        if args.subline is None or args.line is None:
            raise Exception("To show a plot specify line and subline numbers")
        polar_plot.show_schedule(args.line, args.subline, schedule)


if __name__ == '__main__':
    main()
