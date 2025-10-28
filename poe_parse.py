from bs4 import BeautifulSoup
from enum import IntEnum

LINES = 6
SUBLINES = 2

class PowerState(IntEnum):
    Off = 0
    Switch = 1
    On = 2

def parse(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='turnoff-scheduleui-table')

    # Extract headers
    #headers = []
    #for tr in table.find_all('thead')[0].find_all('tr'):
    #    row = []
    #    for th in tr.find_all('th'):
    #        header_text = th.get_text(strip=True)
    #        row.append(header_text)
    #    headers.append(row)

    # Prepare data rows
    rows = []
    for tr in table.find_all('tbody')[0].find_all('tr'):
        row = []
        for td in tr.find_all('td'):
            # Skip title
            if td.attrs.get('class')[0] in ("turnoff-scheduleui-table-queue", "turnoff-scheduleui-table-subqueue"):
                continue
            ONOFF = {'light_1' : PowerState.On, 'light_2' : PowerState.Off, 'light_3' : PowerState.Switch}
            onoff = ONOFF.get(td.attrs.get('class')[0], None)
            if onoff is not None:
                cell_text = onoff.value
            else:
                cell_text = td.get_text(strip=True)
                pass
                #raise Exception("Cannot recognize cell type")
            row.append(cell_text)
        rows.append(row)

    return rows 
