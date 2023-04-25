"""Indexes and logs pages used in the underscores Wallsocket ARG.
"""

from time import perf_counter, time, sleep
from concurrent.futures import ThreadPoolExecutor
import json
import os
import requests
from lxml.html import fromstring

def get_status(site) -> tuple:
    """Gets the status, as well as other information about a given site.

    Args:
        site (str): The site to check

    Returns:
        tuple: A tuple of site name, status, title, and content.
    """
    try:
        req = requests.get(site,timeout=20)
        content = str(req.content)
        if 'data-cfemail' in content:
            content = content.split('data-cfemail')
            content = content[0] + content[1][52:]

        return (site,req.status_code,fromstring(req.content).find('.//title').text,content)
    except:
        return (site,419,'Could not fetch page.','')

def page_iter(site:str,breadth:range) -> iter:
    """Returns an iterator of strings combining the string `site` and the range `breadth`.

    Args:
        site (str): The domain of the site.
        breadth (breadth): A range of numbers to iterate over.

    Returns:
        iter: An iterable of the combination of site and breadth.

    Yields:
        Iterator[iter]: concatenates 'https://', site, '/?p=' and ascending values of breadth.
    """
    for i in breadth:
        yield f'https://{site}/?p={i}'

def index_url(site) -> list:
    """Check for the status of site.

    Iterate over get_status with the returned values from page_iter.

    Args:
        site (str): The domain of the site to check.

    Returns:
        list: A list of all of the responses from the iteration.
    """
    
    try:
        init_r = requests.get(f'https://{site}/',timeout=20)
    except:
        return None
    
    if init_r.status_code != 200:
        return None

    with ThreadPoolExecutor() as executor:
        p_iter = executor.map(get_status,page_iter(site,range(0,257)))
        return [*p_iter]

def log(ctx) -> None:
    """Logs data grabbed by index_url().

    Args:
        ctx (list): A list returned by index_url
    """
    # ctx : [(https://.../, status_code, A Web Page, <body>...</body>), ...]

    with open('src/log/log.json','r',encoding='utf-8') as log_:
        log_ = json.loads(log_.read())

    with open('src/log/sum_log.txt','r',encoding='utf-8') as log_2:
        log_2 = log_2.read()

    log_2_out = f'{int(time())} changes:\n\n'

    for i in [y for x in [z for z in ctx if not z is None] for y in x]:
        if i[0] in log_.keys():

            # Log page title
            if i[2] in log_[i[0]]["title"].keys():
                log_[i[0]]["title"][i[2]].append(int(time()))
            else:
                log_[i[0]]["title"][i[2]] = [int(time())]

            # Log page content
            for file in os.scandir('src/archive/'):
                with open(file.path,'r') as check:
                    check = check.read()

                if str(i[3]) == check:
                    log_[i[0]]["content"][str(int(time()))] = file.path
                    break
            else:
                try:
                    new_id = max(int(x.path.split('/')[-1][7:-4]) for x in os.scandir('src/archive')) + 1
                except:
                    new_id = 0

                log_2_out += f'New archive file created! src/archive/archive{new_id}.txt. This might mean that the urls linking here were updated?\n'

                with open(f'src/archive/archive{new_id}.txt','w',encoding='utf-8') as c_new:
                    c_new.write(str(i[3]))

                log_[i[0]]["content"][str(int(time()))] = f'src/archive/archive{new_id}.txt'

            # Log status_code
            log_[i[0]]["code"][str(int(time()))] = i[1]

        else:
            log_[i[0]] = {
                "first_detected": int(time()),
                "site": i[0],
                "title": {i[2]: [int(time())]},
                "code": {str(int(time())): i[1]}}

            for file in os.scandir('src/archive/'):
                with open(file.path,'r') as check:
                    check = check.read()

                if str(i[3]) == check:
                    log_[i[0]]["content"] = {str(int(time())): file.path}
                    break
            else:
                try:
                    new_id = max(int(x.path.split('/')[-1][7:-4]) for x in os.scandir('src/archive')) + 1
                except:
                    new_id = 0

                log_2_out += f'New archive file created! src/archive/archive{new_id}.txt. This might mean that the urls linking here were updated?\n'

                with open(f'src/archive/archive{new_id}.txt','w',encoding='utf-8') as c_new:
                    c_new.write(str(i[3]))

                log_[i[0]]["content"] = {
                    str(int(time())): f'src/archive/archive{new_id}.txt'
                    }

    with open('src/log/log.json','w',encoding='utf-8') as n_log:
        n_log.write(json.dumps(log_, indent=2))

    with open('src/log/sum_log.txt','w',encoding='utf-8') as sum_log:
        sum_log.write(log_2 + log_2_out + '\nEnd logging.\n')


def main() -> None:
    """The function used to initiate indexing and logging. 
    Asynchronously runs index_url for each domain in domains.
    """

    print('Executing hourly index.')

    with open('src/domains.txt','r',encoding='utf-8') as domains:
        domains = [x.split('\n')[0] for x in domains.readlines()]

    time_ = perf_counter()
    with ThreadPoolExecutor(max_workers=len(domains)) as executor:
        d_iter = executor.map(index_url,domains)

    print(f'Hourly index finished.\n\nTime to run: {perf_counter() - time_} seconds.')
    log([*d_iter])


def runner():
    """Run main() once per hour.
    """

    while 1:
        sleep(3600 - (time.time() % 3600))
        main()

runner()
