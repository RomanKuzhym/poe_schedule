import matplotlib.pyplot as plt
import numpy as np

def plot12hours(ax, schedule, title='', timeinit=0):

    # Set the direction of the polar plot (0 at the top)
    ax.set_theta_direction(-1)

    # Set the location of 0 degrees to the top
    ax.set_theta_offset(np.pi / 2)

    hours = np.arange(0, 24)  # 1 to 12 hours, 30 min step
    values = np.array(schedule)

    # Convert hours to radians for the polar plot
    angles = (hours / 24) * 2 * np.pi

    # Plot the data as bars
    bars = ax.bar(angles, values, width=2 * np.pi / 24, align='edge', alpha=0.75, color='skyblue')

    ax.set_xticks(angles)
    ax.set_xticklabels([f"{int(hour/2) + timeinit}:{'00' if hour % 2 ==0 else '30'}" for hour in hours])

    ax.set_title(title)
    ax.get_yaxis().set_visible(False)
    plt.draw()

def show_schedule(qu_num, raw_sched):
    plt.rcParams.update({'font.size': 8})
    fig, ax = plt.subplots(1, 2, subplot_kw={'projection': 'polar'})

    plot12hours(ax[0], raw_sched[qu_num][:24], f"{qu_num + 1} черга відключення з 00:00 по 12:00")
    plot12hours(ax[1], raw_sched[qu_num][24:], f"{qu_num + 1} черга відключення з 12:00 по 24:00", 12)
    plt.show()
