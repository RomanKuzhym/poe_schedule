from bs4 import BeautifulSoup

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
            ONOFF = {'light_on' : True, 'light_off' : False}
            onoff = ONOFF.get(td.attrs.get('class')[0], None)
            if onoff is not None:
                cell_text = int(onoff)
            else:    
                cell_text = td.get_text(strip=True)
                pass
                #raise Exception("Cannot recognize 
            row.append(cell_text)
        rows.append(row)

    raw_data = [r[1:] for r in rows] # Skip 1st column
    return raw_data
