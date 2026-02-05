from indentprint import IndentPrint
from poe import LINES, SUBLINES


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

