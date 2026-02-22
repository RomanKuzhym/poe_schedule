import os
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
from datetime import time


def plot_uniform_ticks(ax, count, radius = [0, 1], color = 'black', linewidth=1):
    for a in range(count):
        t = a / count * 2 * np.pi
        ax.plot([t, t], radius, color=color, linewidth=linewidth)

def plot_clock(ax, hours, minutes, h_linewidth=2, m_linewidth=1,
    h_color='black', m_color='black'):
    h_angle = (hours / 12 + minutes * 5 / 3600) * 2 * np.pi
    ax.plot([h_angle, h_angle], [-2.6, -1.2], color=h_color, linewidth=h_linewidth)
    m_angle = minutes / 60 * 2 * np.pi
    ax.plot([m_angle, m_angle], [-2.6, -0.5], color=m_color, linewidth=m_linewidth)
    
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
    plot_uniform_ticks(ax, HOURS, [-0.2, -0.1], color='black', linewidth=2.5)
    plot_uniform_ticks(ax, HOURS, [-0.2, -0.1], color='slategrey', linewidth=1)

    QUATER_HRS = 4
    plot_uniform_ticks(ax, QUATER_HRS, [-0.4, -0.1], color='black', linewidth=3.5)
    plot_uniform_ticks(ax, QUATER_HRS, [-0.4, -0.1], color='slategrey', linewidth=2)

    ax.set_xticks(angles)
    ticklabels = [f"{int(hour/2) + timeinit}" if hour % 2 == 0 else "" for hour in hours]
    ticklabels[0] = 12
    ax.set_xticklabels(ticklabels)
    ax.grid(False)
    
    ax.set_title(title)
    ax.get_yaxis().set_visible(False)
    ax.set_ylim(-3, 1)

    plt.draw()

def generate_plot(title, sched, clocktime=None):
    plt.rcParams.update({'font.size': 8, 'font.weight': 'bold', 'text.color' : 'darkslategrey'})
    fig, ax = plt.subplots(1, 2, subplot_kw={'projection': 'polar'})
    fig.suptitle(title, fontsize=14)

    plot12hours(ax[0], sched[:24])
    plot12hours(ax[1], sched[24:])

    if clocktime:
        if type(clocktime) is not time:
            raise TypeError("time must be of type datetime.time")

        H_THICKNESS = 3
        M_THICKNESS = 1
        OUTLINE = 0.5
        
        minutes24h = clocktime.hour * 60 + clocktime.minute
        pastmidday = minutes24h > 12 * 60
        clock_ax = ax[[0, 1][pastmidday]]
        # plot twise to add an outline
        plot_clock(clock_ax, clocktime.hour, clocktime.minute,
            H_THICKNESS + 2 * OUTLINE, M_THICKNESS + 2 * OUTLINE, 'black', 'black')
        plot_clock(clock_ax, clocktime.hour, clocktime.minute,
            H_THICKNESS, M_THICKNESS, 'lightcoral', 'white')

    ax[0].text(0, -3, "AM", ha='center', va='center', fontsize=14,
        path_effects=[pe.withStroke(linewidth=1, foreground='lightgrey')])
    ax[1].text(0, -3, "PM", ha='center', va='center', fontsize=14,
        path_effects=[pe.withStroke(linewidth=1, foreground='lightgrey')])
    plt.tight_layout()

def show_plot():
    plt.show()

def write_plot(outpath: str):
    with open(outpath, 'w') as f:
        if not f.writable():
            raise Exception(f"Cannot save the plot to {outpath}")
    plt.savefig(outpath)

