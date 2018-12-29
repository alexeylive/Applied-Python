# -*- encoding: utf-8 -*-
import re
from collections import Counter
from collections import defaultdict
from urllib.parse import urlparse
from os.path import splitext
import datetime


def in_time(start_at, stop_at, log):
    log_datetime = datetime.datetime.strptime(log.group('request_date') + log.group('request_time'),
                                              '%d/%b/%Y%H:%M:%S')

    start = stop = False

    if start_at is None or log_datetime >= datetime.datetime.strptime(start_at,
                                                                      '%d/%b/%Y %H:%M:%S'):
        start = True

    if stop_at is None or log_datetime <= datetime.datetime.strptime(stop_at,
                                                                     '%d/%b/%Y %H:%M:%S'):
        stop = True

    if stop and start:
        return True
    else:
        return False


def add_dict(log, url, slow_queries, dict):
    if slow_queries:
        dict[url][0] += 1
        dict[url][1] += int(log.group('response_time'))
    else:
        dict[url] += 1


def parse(
        ignore_files=False,
        ignore_urls=[],
        start_at=None,
        stop_at=None,
        request_type=None,
        ignore_www=False,
        slow_queries=False
):
    pattern = re.compile('\[(?P<request_date>.*) (?P<request_time>.*)\] '
                         '\"(?P<request>.*) (?P<URL>.*) (?P<protocol>.*)\"'
                         ' (?P<response_code>.*) (?P<response_time>.*)')
    if slow_queries:
        dict = defaultdict(lambda: [0, 0])
    else:
        dict = Counter()

    file = open('log.log')
    for line in file:
        if pattern.match(line.rstrip()):
            log = pattern.match(line.rstrip())

            if request_type and log.group('request') != request_type:
                continue

            if not in_time(start_at, stop_at, log):
                continue

            url_parse = urlparse(log.group('URL'))

            name, form = splitext(url_parse.path)

            if ignore_files and form:
                continue

            if ignore_www and url_parse.netloc.startswith('www.'):
                url = url_parse.netloc[4:] + url_parse.path
            else:
                url = url_parse.netloc + url_parse.path

            if url in ignore_urls:
                continue

            add_dict(log, url, slow_queries, dict)

    file.close()
    top = []
    if slow_queries:
        for item in sorted(dict.items(), key=lambda x: (x[1][1] / x[1][0]), reverse=True)[:5]:
            top.append(int(item[1][1] / item[1][0]))
    else:
        for item in dict.most_common(5):
            top.append(item[1])

    return top
