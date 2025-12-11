import matplotlib.pyplot as plt
import numpy as np

from poe_parse import LINES, SUBLINES

def plot12hours(ax, schedule, title='', timeinit=0):

    # Set the direction of the polar plot (0 at the top)
    ax.set_theta_direction(-1)

    # Set the location of 0 degrees to the top
    ax.set_theta_offset(np.pi / 2)

    hours = np.arange(0, 24)  # 1 to 12 hours, 30 min step
    values = np.array(schedule)

    # Convert hours to radians for the polar plot
    angles = (hours / 24) * 2 * np.pi

    reds = values == 0
    yellows = values == 1
    blues = values == 2

    # Plot the data as bars
    ax.bar(angles, reds, width=2 * np.pi / 24, align='edge', alpha=0.75, color='#010621')
    ax.bar(angles, yellows, width=2 * np.pi / 24, align='edge', alpha=0.75, color='grey')
    ax.bar(angles, blues, width=2 * np.pi / 24, align='edge', alpha=0.75, color='yellow')

    ax.set_xticks(angles)
    ax.set_xticklabels([f"{int(hour/2) + timeinit}:{'00' if hour % 2 ==0 else '30'}" for hour in hours])
    ax.grid(color='slategray')
    ax.set_title(title)
    ax.get_yaxis().set_visible(False)
    ax.set_ylim(-3, 1)

    plt.draw()

def show_schedule(line, subline, raw_sched):
    idx = line * SUBLINES + subline
    plt.rcParams.update({'font.size': 8})
    fig, ax = plt.subplots(1, 2, subplot_kw={'projection': 'polar'})
    fig.suptitle(f"{line + 1} черга {subline+1} підчерга")
    plot12hours(ax[0], raw_sched[idx][:24], "00:00 - 12:00")
    plot12hours(ax[1], raw_sched[idx][24:], "12:00 - 24:00", 12)
    plt.tight_layout()
    plt.show()
