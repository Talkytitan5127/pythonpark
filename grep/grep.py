#!/usr/bin/python3

import argparse
import sys
import re
from collections import deque


def find(string, pattern, ignore):
    pattern = pattern.replace('*', '.*')
    pattern = pattern.replace('?', '.')
    cursor = None
    if ignore:
        cursor = re.compile(pattern, re.IGNORECASE)
    else:
        cursor = re.compile(pattern)
    result = cursor.search(string)
    return result

def output(line):
    print(line)

def grep(lines, params):
    count = 0
    queue_before = deque()
    queue_after = deque()
    len_que = max(params.before_context, params.context)
    len_after = max(params.after_context, params.context)
    after = 0
    for index, line in enumerate(lines):
        line = line.rstrip()
        search = find(line, params.pattern, params.ignore_case)
        if search and not params.invert or not search and params.invert:
            if params.count:
                count += 1
                continue
            while queue_after:
                elem = queue_after.popleft()
                output(elem)
                if elem in queue_before:
                    queue_before.remove(elem)
            while queue_before:
                output(queue_before.popleft())
            if params.line_number:
                line = "{}:{}".format(index+1, line)
            output(line)
            after = len_after
            queue_after.clear()
        elif params.count:
            continue
        else:
            if params.line_number:
                line = "{}-{}".format(index+1, line)
            if len_que:
                if len_que == len(queue_before):
                    queue_before.popleft()
                    queue_before.append(line)
                else:
                    queue_before.append(line)
            if after:
                queue_after.append(line)
                after -= 1
    while queue_after:
        output(queue_after.popleft())
    if params.count:
        output(str(count))

def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()
