import matplotlib.pyplot as plt
import numpy as np

from poe import LINES, SUBLINES


def plot_uniform_ticks(ax, count, radius = [0, 1], color = 'black', linewidth=1):
    for a in range(count):
        t = a / count * 2 * np.pi
        ax.plot([t, t], radius, color=color, linewidth=linewidth)
    

def plot12hours(ax, schedule, title='', timeinit=0):

    # Set the direction of the polar plot (0 at the top)
    ax.set_theta_direction(-1)

    # Set the location of 0 degrees to the top
    ax.set_theta_offset(np.pi / 2)

    hours = np.arange(0, 24)  # 1 to 12 hours, 30 min step
    values = np.array(schedule)

    # Convert hours to radians for the polar plot
    angles = (hours / 24) * 2 * np.pi
    off = values == 0
    switching = values == 1
    on = values == 2

    # Plot the data as bars
    ax.bar(angles, off, width=2 * np.pi / 24, align='edge', alpha=0.75, color='#010621')
    ax.bar(angles, switching, width=2 * np.pi / 24, align='edge', alpha=0.75, color='#967423')
    ax.bar(angles, on, width=2 * np.pi / 24, align='edge', alpha=0.75, color='#ffb300')

    theta = np.linspace(0, 2*np.pi, 1000)
    ax.plot(np.linspace(0, 2*np.pi, 1000), np.full_like(theta, 0), linewidth=0.8)


    HALF_HOURS = 24
    plot_uniform_ticks(ax, HALF_HOURS, [0, 1], color='slategrey', linewidth=1)

    HOURS = 12
    plot_uniform_ticks(ax, HOURS, [-0.2, -0.1], color='slategrey', linewidth=1)

    QUATER_HRS = 4
    plot_uniform_ticks(ax, QUATER_HRS, [-0.4, -0.1], color='slategrey', linewidth=2)

    ax.set_xticks(angles)
    ax.set_xticklabels([f"{int(hour/2) + timeinit}:{'00' if hour % 2 ==0 else '30'}" for hour in hours])
    ax.grid(False)
    
    ax.set_title(title)
    ax.get_yaxis().set_visible(False)
    ax.set_ylim(-3, 1)

    plt.draw()

def show_schedule(line, subline, raw_sched):
    idx = line * SUBLINES + subline
    plt.rcParams.update({'font.size': 8})
    fig, ax = plt.subplots(1, 2, subplot_kw={'projection': 'polar'})
    fig.suptitle(f"{line + 1} черга {subline+1} підчерга")
    ax[0].text(0, -3, "AM", ha="center", va='center', fontsize=20, color='darkslategrey')
    ax[1].text(0, -3, "PM", ha="center", va='center', fontsize=20, color='darkslategrey')
    plot12hours(ax[0], raw_sched[idx][:24])
    plot12hours(ax[1], raw_sched[idx][24:])
    plt.tight_layout()
    plt.show()
