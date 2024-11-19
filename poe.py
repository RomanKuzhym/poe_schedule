import requests
import datetime
import polar_plot
import poe_parse


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
    for qu in range (6):
        prevstep = 0
        rangestart = 0
        rg = []
        for i, timestep in enumerate(raw_sched[qu]):
            if timestep == 1 and prevstep == 0:
                rangestart = i * 0.5
                prevstep = 1
            if timestep == 0 and prevstep == 1:
                rangestop = i * 0.5
                prevstep = 0
                rg.append([rangestart, rangestop])

        ranges.append(rg)
        
    return ranges

def main():
    date = datetime.datetime.now().date()# + datetime.timedelta(days=1)
    print (f"Відключення електроенергії за {date}")
    raw_data = poe_parse.parse(fetch_schedule_html(date))
    #for q in raw_data:
    #    print(q)
    ranges = get_ranges(raw_data)
    for i,r in enumerate(ranges):
        print(f"{i+1} черга:")
        for series in r:
            h_from, min_from = divmod(series[0], 1)
            h_to, min_to = divmod(series[1], 1)
            td_from = datetime.timedelta(hours=h_from, minutes=60*min_from)
            td_to = datetime.timedelta(hours=h_to, minutes=60*min_to)
            print(f"      {td_from} - {td_to}")

    polar_plot.show_schedule(1, raw_data)

if __name__ == '__main__':
    main()
