import requests
import datetime
import polar_plot
import poe_parse
from poe_parse import PowerState, LINES, SUBLINES

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
            elif prevstep in (PowerState.Off, PowerState.Switch) and timestep == PowerState.On:
                rangestop = i * 0.5
                prevstep = PowerState.On
                rg.append([rangestart, rangestop])

        ranges.append(rg)

    return ranges

def main():
    date = datetime.datetime.now().date()# + datetime.timedelta(days=1)
    try:
        fetch_schedule_html(date)
    except:
        print("Не вдалося завантажити дані")
        return

    print (f"Відключення електроенергії за {date}")
    raw_data = poe_parse.parse(fetch_schedule_html(date))
    #for q in raw_data:
    #    print(q)
    ranges = get_ranges(raw_data)

    subline_idx = lambda i,j: i * SUBLINES + j
    for i in range(LINES):
        print(f"{i+1} черга:")
        for j in range(SUBLINES):
            print(f"   {j+1} підчерга:")
            r = ranges[subline_idx(i,j)]
            for series in r:
                h_from, min_from = divmod(series[0], 1)
                h_to, min_to = divmod(series[1], 1)
                td_from = datetime.timedelta(hours=h_from, minutes=60*min_from)
                td_to = datetime.timedelta(hours=h_to, minutes=60*min_to)
                print(f"      {td_from} - {td_to}")


    polar_plot.show_schedule(1, 1, raw_data)

if __name__ == '__main__':
    main()
