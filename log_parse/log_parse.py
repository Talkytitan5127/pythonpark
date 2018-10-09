# -*- encoding: utf-8 -*-

import pdb
import re
from collections import Counter
from datetime import datetime

def to_datetime(timestring):
    timestring = timestring.strip('[]')
    time = datetime.strptime(timestring, '%d/%b/%Y %H:%M:%S')
    return time

def compare_date(date1, date2):
    time1 = to_datetime(date1)
    time2 = to_datetime(date2)
    return time1 <= time2

def check_file(url):
    pattern = re.compile(r'\/.+\..+$')
    return pattern.search(url)

def parse_url(string, scheme, ignore_www, ignore_files):  
    result = scheme.search(string)
    host = result.group('host')
    if result.group('port') is not None:
        host += ':' + result.group('port')
    url = result.group('url')
    if ignore_www:
        host = host.lstrip('www.')
    url = url.split('?')[0]
    url = url.split('#')[0]
    if ignore_files and check_file(url) is not None:
        return None
    return host + url


def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False
):
    log = open('log.log', 'r')
    
    pattern_string = r'\[(?P<datetime>\d{,2}\/\w+\/\d{,4} \d{,2}:\d{,2}:\d{,2})\] \"(?P<type>\w+) (?P<req>.+) (?P<proto>.+)\" (?P<code>\d{3}) (?P<reqtime>\d+)'
    parser = re.compile(pattern_string)
    
#   <схема>:[//[<логин>:<пароль>@]<хост>[:<порт>]][/]<URL‐путь>[?<параметры>][#<якорь>] 
    scheme_url = r'(?P<sch>.+?):(?://(?:(?P<log>\w+?):(?P<pass>\w+?)@)?(?P<host>[a-zA-Z0-9.]+)(?::(?P<port>\d+))?)?(?P<url>\/?.+)'
    url_parser = re.compile(scheme_url)

    count = Counter()
    for string in log:
        string = string.strip()
        result = parser.search(string)
        
        if result is None:
            continue
        if request_type is not None and result.group('type') != request_type:
            continue
        if start_at is not None and not compare_date(start_at, result.group('datetime')):
            continue
        if stop_at is not None and not compare_date(result.group('datetime'), stop_at):
            continue

        url = parse_url(result.group('req'), url_parser, ignore_www, ignore_files)
        if url is None or url in ignore_urls:
            continue

        if slow_queries:
            reqtime = int(result.group('reqtime'))
            if url in count:
                count[url]['quant'] += 1
                count[url]['time'] += reqtime
            else:
                count[url] = {'quant': 1, 'time': reqtime}
        else:
            count[url] = count.get(url, 0) + 1
    
    if slow_queries:
        func = lambda el: int(count[el]['time']/count[el]['quant'])
        arr = list(map(func, sorted(count.keys(), reverse=True, key=func)))[:5]
    else:
        arr = list(map(lambda el: el[1], count.most_common(5)))
    
    log.close()
    return arr


if __name__ == '__main__':
    parse()