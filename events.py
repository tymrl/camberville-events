import argparse
import arrow
import json
import requests
from bs4 import BeautifulSoup

now = arrow.now()

def get_porch_events():
    print('Getting events at The Porch...')
    porch_events = BeautifulSoup(
        requests.get('http://theporchsouthern.com/listen-1').text,
        features='html.parser'
    ).find_all(class_='eventlist-column-info')

    events = []
    for event in porch_events:
        date = event.find(class_='event-date')['datetime']
        time = event.find(class_='event-time-12hr-start')
        if not time:
            continue
        datetime = arrow.get(date + time.text, 'YYYY-MM-DDh:mm A', tzinfo='US/Eastern')
        events.append({
            'location': 'The Porch',
            'name': event.find(class_='eventlist-title').text,
            'datetime': datetime,
        })

    return events

def get_city_winery_events():
    print('Getting events at City Winery...')
    city_winery_search_results = BeautifulSoup(
        requests.get('https://www.citywinery.com/boston/Online/default.asp?BOparam::WScontent::loadArticle::permalink=boston-buy-tickets').text,
        features='html.parser'
    ).find_all('script')[25]

    city_winery_events = json.loads(city_winery_search_results.string.replace('\n', '').replace('\r', '').replace('\t', '').split('searchResults : ')[1].split(',  searchFilters')[0].replace('\\n', ' ').replace('\\/', '/').replace('\\"', '').replace("\\\'", ""))

    events = []
    for event in city_winery_events:
        # 'Wednesday, August 11, 2021 8:00 PM',
        datetime = arrow.get(event[7], 'dddd, MMMM D, YYYY h:mm A', tzinfo='US/Eastern')
        events.append({
            'location': 'City Winery',
            'name': event[6],
            'datetime': datetime
        })

    return events

def get_sinclair_events():
    print('Getting events at The Sinclair...')
    sinclair_events = BeautifulSoup(
        requests.get('https://www.sinclaircambridge.com/events').text,
        features='html.parser'
    ).find_all(class_='info')

    events = []
    for event in sinclair_events:
        datestring = event.find(class_='date').text.strip()
        timestring = event.find(class_='time').text.split('Doors')[1].strip()
        datetime = arrow.get(datestring + timestring, 'ddd, MMM D, YYYYh:mm A', tzinfo='US/Eastern')
        
        name = event.find(class_='carousel_item_title_small').text.strip()
        opener = event.find(class_='supporting').text.strip()
        if opener:
            name += ' w/ ' + opener

        events.append({
            'location': 'The Sinclair',
            'name': name,
            'datetime': datetime
        })
    return events


def get_burren_events():
    print('Getting events at The Burren...')
    burren_evenings = [
        date_header.find_parent('table').find_parent('table') for date_header in 
            BeautifulSoup(
                requests.get('http://www.burren.com/music.html').text,
                features='html.parser'
    ).find_all(class_='HEADER')]

    events = []
    for evening in burren_evenings:
        # Ugly hack to get the year
        datestring = evening.find(class_='HEADER').text
        if ',' not in datestring:
            datestring += now.format(', YYYY')
        
        evening_events = [
            room_header.find_parent('table').find_parent('table')
            for room_header in evening.find_all(class_='Room')
        ]

        for event in evening_events:
            timestring = event.find(class_='Time').text.split('-')[0].replace('pm:', '').split(' & ')[0]
            if ':' not in timestring:
                timestring += ':00'
            timestring += ' PM'
            try:
                datetime = arrow.get(datestring + timestring, 'dddd MMMM D, YYYYh:mm A', tzinfo='US/Eastern')
            except arrow.parser.ParserMatchError as e:
                print(e)
                continue

            events.append({
                'location': 'The Burren',
                'name': ' '.join([name.capitalize() for name in event.find(class_='BAND').text.split()]),
                'datetime': datetime,
            })

    return events
def get_brattle_events(days):
    print('Getting events at Brattle Theater...')
    url_base = 'https://brattlefilm.org/'
    events = []
    for day_shift in range(days):
        date = now.shift(days=day_shift).format('YYYY-MM-DD')
        brattle_events = BeautifulSoup(
            requests.get('https://brattlefilm.org/' + date).text,
            features='html.parser'
        ).find_all(class_='showtime')

        for event in brattle_events:
            events.append({
                'location': 'Brattle Theater',
                'name': event.find_parent(class_='showtimes-description').find(class_='show-title').text.strip(),
                'datetime': arrow.get(date + event.text.split('m')[0].strip() + 'm', 'YYYY-MM-DDh:mm A', tzinfo='US/Eastern')
            })
    
    return events

def get_plough_events():
    print('Getting events at Plough & Stars...')
    url_base = 'https://calendar.ploughandstars.com/events/calendar?month={}&year={}'
    month_tuples = [(now.month, now.year), (now.shift(months=1).month, now.shift(months=1).year)]
    
    events = []
    for month_tuple in month_tuples:
        plough_days = BeautifulSoup(
            requests.get(url_base.format(*month_tuple)).text,
            features='html.parser'
        ).find_all(class_='day-block')

        for day_block in plough_days:
            day = day_block.find(class_='number').text
            day_events = day_block.find(class_='row')
            if not day_events:
                continue
            for event in day_events:
                time = event.find(class_='flex_item_left').text
                if not time:
                    continue
                time = time.split('pm')[0]
                if '-' in time:
                    time = time.split('-')[0]
                if ':' not in time:
                    time += ':00'
                time += 'pm'
                
                events.append({
                    'location': 'Plough & Stars',
                    'name': event.find(class_='event').text,
                    'datetime': arrow.get(str(month_tuple[1]) + ' ' + day + ' ' + time, 'YYYY ddd MMM D h:mmA', tzinfo='US/Eastern')
                })

    return events

def get_crystal_ballroom_events():
    print('Getting events at Crystal Ballroom...')
    crystal_events = BeautifulSoup(
        requests.get('https://www.crystalballroomboston.com/').text,
        features='html.parser'
    ).find_all(class_='event-details')

    events = []
    for event in crystal_events:
        meta_entries = event.find(class_='event-meta').find_all('span')
        time = meta_entries[1].text.split('Show')[1].strip()
        if not time:
            continue
        datetime_string = meta_entries[0].text.strip() + ' ' + time
        events.append({
            'location': 'Crystal Ballroom',
            'name': ' '.join([word.capitalize() for word in event.find('h2').text.split()]),
            'datetime': arrow.get(datetime_string, 'ddd, MMM D, YYYY h:mm A', tzinfo='US/Eastern')
        })

    return events

def get_lilypad_events():
    print('Getting events at Lily Pad...')
    lilypad_events = BeautifulSoup(
        requests.get('https://www.lilypadinman.com/home').text,
        features='html.parser'
    ).find_all('article')

    events = []
    for event in lilypad_events:
        datetime = arrow.get(
            event.find(class_='eventlist-datetag-inner').text.strip().replace('\n', ' ')[:-5],
            'MMM D h:mm a', tzinfo='US/Eastern'
        )
        if datetime.month >= now.month:
            datetime = datetime.replace(year=now.year)
        else:
            datetime = datetime.replace(year=now.year + 1)
        
        events.append({
            'location': 'Lily Pad',
            'name': event.find(class_='eventlist-title').text,
            'datetime': datetime
        })

    return events

def get_aeronaut_events():
    print('Getting events at Aeronaut...')
    aeronaut_events_script = BeautifulSoup(
        requests.get('https://www.aeronautbrewing.com/events/').text,
        features='html.parser'
    ).find_all('script')[7]

    aeronaut_events = json.loads(aeronaut_events_script.string.split('var EVENTS = ')[1].split(';var EVENTS_CURRENT=true')[0])

    events = []
    for event in aeronaut_events:
        if event['category'] != 'music':
            continue
        events.append({
            'name': event['name'],
            'location': 'Aeronaut ' + ('Brewery' if event['venue_slug'] == 'somerville' else 'Cannery'),
            'datetime': arrow.get(
                event['date'] + ' ' + event['start'],
                'YYYY-MM-DD H:mm', tzinfo='US/Eastern')
        })

    return events

def get_toad_events():
    print('Getting events at Toad...')

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}

    toad_calendar = BeautifulSoup(
        requests.get('https://toadcambridge.com/calendar/', headers=headers).text,
        features='html.parser'
    )

    # There's currently a bug in the Toad website where the first time you hit "next" you get the same month
    toad_calendar_next_month = BeautifulSoup(
        requests.get(
            BeautifulSoup(
                requests.get(toad_calendar.find(class_='ai1ec-next-month').attrs['href'], headers=headers).text,
                features='html.parser'
            ).find(class_='ai1ec-next-month').attrs['href'],
            headers=headers
        ).text,
        features='html.parser'
    )
    toad_events = toad_calendar.find_all(class_='ai1ec-day') + toad_calendar_next_month.find_all(class_='ai1ec-day')
    events = []

    for event in toad_events:
        popover_tag = event.find(class_='ai1ec-popover')
        if popover_tag is None:
            continue

        datetime = arrow.get(
            now.format('YYYY') + ' ' + popover_tag.find(class_='ai1ec-event-time').text.strip(),
            'YYYY MMM D @ h:mm a', tzinfo='US/Eastern'
        )

        if datetime.month >= now.month:
            datetime = datetime.replace(year=now.year)
        else:
            datetime = datetime.replace(year=now.year + 1)

        events.append({
            'location': 'Toad',
            'name': popover_tag.find(class_='ai1ec-load-event').text.strip(),
            'datetime': datetime
        })

    return events


parser = argparse.ArgumentParser()
parser.add_argument('-d', '--days', type=int, default=3,
                    help='Number of days to show events for, including today')
args = parser.parse_args()

print()
events = (
    get_toad_events() +
    get_porch_events() + 
    get_city_winery_events() + 
    get_sinclair_events() + 
    get_burren_events() + 
    get_brattle_events(args.days) +
    get_plough_events() +
    get_crystal_ballroom_events() +
    get_lilypad_events() +
    get_aeronaut_events()
)
print()

evening = ''
for event in sorted(events, key=lambda event: event['datetime']):
    if event['datetime'] < now.floor('day') or event['datetime'] > now.shift(days=args.days).ceil('day'):
        continue
    if 'Livestream' in event['name'] or 'Trivia' in event['name']:
        continue

    event_evening = event['datetime'].format('MMMM D')
    if evening != event_evening:
        evening = event_evening
        print(evening)
    print('{:>10}   {:16}   {}'.format(event['datetime'].format('h:mm A'), event['location'], event['name']))
