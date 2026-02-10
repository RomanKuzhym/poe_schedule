import argparse
import copy
from datetime import datetime, timedelta
import logging

import polar_plot
import poe
from poe_print import print_lines, print_time_ranges_oneline
from indentprint import IndentPrint

log = logging.getLogger(__name__)

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
        help="Дата РРРР-ММ-ДД. За замовчуванням -- поточна дата",
        type=lambda s: datetime.strptime(s, '%Y-%m-%d'), 
        default=datetime.now().date())
    parser.add_argument(
        "--outages", 
        help="Показувати графік вимкнення замість увімкнення", 
        action='store_true',
        default=False)
    parser.add_argument(
        "--showplot", 
        help="Діаграма", 
        action='store_true',
        default=False)
    parser.add_argument(
        "--tomorrow",
        help="Графік на завтра (або на наступний день від заданої дати)",
        action='store_true',
        default=False)
    parser.add_argument(
        "--oneline",
        help="Відображати у вигляді простого рядка, без дати та переносів",
        action='store_true',
        default=False)
    parser.add_argument(
        "--clock",
        help="Відображати поточний час на діаграмі",
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
        log.error(f"Помилка обробки даних: {e}")
        log.error(f"{text!r}")
        exit(2)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s]: %(message)s'
    )

    args = parse_args()

    date = args.date
    if args.tomorrow:
        date += timedelta(days=1)
    # adapt to [0, LINES/SUBLINES) range
    if args.line is not None:
        args.line -= 1
    if args.subline is not None:
        args.subline -= 1

    schedule = fetch_schedule(date)
    sched_ranges = poe.get_ranges(schedule, not args.outages)
    if args.singleline:
        if args.subline is None or args.line is None:
            raise Exception("To show a plot specify line and subline numbers")
        print_time_ranges_oneline(sched_ranges, args.line, args.subline)
    else:
        print (f"{'Вимкнення' if args.outages else 'Увімкнення'} електроенергії за {date}")
        with IndentPrint():
            print_lines(sched_ranges, args.line, args.subline)

    if args.showplot:
        if args.subline is None or args.line is None:
            raise Exception("To show a plot specify line and subline numbers")
        polar_plot.show_schedule(
            args.line,
            args.subline,
            schedule,
            datetime.now().time() if args.clock else None)


if __name__ == '__main__':
    main()
