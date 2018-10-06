import argparse
import sys
import re
import numpy as np


def output(line):
    print(line)


def check(pattern, line):
    p = re.search(pattern, line)
    if p:
        return True
    else:
        return False


def notaccount(params):
    if params.after_context == 0 and params.before_context == 0 and params.context == 0 \
            and params.line_number == False and params.count == False:
        return True


def add_dict(dict, params, list, num):
    if not dict.get(num + 1):
        if params.line_number:
            dict[num + 1] = "-" + list[num]
        else:
            dict[num + 1] = list[num]


def grep(lines, params):
    params.pattern = re.sub("[*]", ".*", params.pattern)
    params.pattern = re.sub("[?]", ".", params.pattern)

    if params.count:
        count = 0
    elif not notaccount(params):
        dict = {}

    if params.ignore_case:
        params.pattern = params.pattern.lower()

    for i, line in enumerate(lines):
        line_m = line.rstrip()

        if params.ignore_case:
            line_m = line_m.lower()

        if params.invert and not check(params.pattern, line_m):
            if notaccount(params):
                output(line)
                continue

            if params.count:
                count = count + 1
                continue

            if params.line_number:
                dict[i + 1] = ":" + line

            if params.context != 0:
                if (len(lines) - i - 1 - params.context) > 0:
                    for num in range(i, i + params.context + 1):
                        add_dict(dict, params, lines, num)
                else:
                    for num in range(i, len(lines)):
                        add_dict(dict, params, lines, num)

                if i + 1 - params.context > 0:
                    for num in range(i - params.context, i + 1):
                        add_dict(dict, params, lines, num)
                else:
                    for num in range(0, i + 1):
                        add_dict(dict, params, lines, num)

            if params.after_context != 0:
                if (len(lines) - i - 1 - params.after_context) > 0:
                    for num in range(i, i + params.after_context + 1):
                        add_dict(dict, params, lines, num)
                else:
                    for num in range(i, len(lines)):
                        add_dict(dict, params, lines, num)

            if params.before_context != 0:
                if i + 1 - params.before_context > 0:
                    for num in range(i - params.before_context, i + 1):
                        add_dict(dict, params, lines, num)
                else:
                    for num in range(0, i + 1):
                        add_dict(dict, params, lines, num)


        elif not params.invert and check(params.pattern, line_m):
            if notaccount(params):
                output(line)
                continue

            if params.count:
                count = count + 1
                continue

            if params.line_number:
                dict[i + 1] = ":" + line

            if params.context != 0:
                if (len(lines) - i - 1 - params.context) > 0:
                    for num in range(i, i + params.context + 1):
                        add_dict(dict, params, lines, num)
                else:
                    for num in range(i, len(lines)):
                        add_dict(dict, params, lines, num)

                if i + 1 - params.context > 0:
                    for num in range(i - params.context, i + 1):
                        add_dict(dict, params, lines, num)
                else:
                    for num in range(0, i + 1):
                        add_dict(dict, params, lines, num)

            if params.after_context != 0:
                if (len(lines) - i - 1 - params.after_context) > 0:
                    for num in range(i, i + params.after_context + 1):
                        add_dict(dict, params, lines, num)
                else:
                    for num in range(i, len(lines)):
                        add_dict(dict, params, lines, num)

            if params.before_context != 0:
                if i + 1 - params.before_context > 0:
                    for num in range(i - params.before_context, i + 1):
                        add_dict(dict, params, lines, num)
                else:
                    for num in range(0, i + 1):
                        add_dict(dict, params, lines, num)

    if params.count:
        output(str(count))
    elif not notaccount(params):
        for i in sorted(dict.keys()):
            if params.line_number:
                output(str(i) + dict[i])
            else:
                output(dict[i])


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
    #   params = parse_args(sys.argv[1:])
    #  grep(sys.stdin.readlines(), params)
    lines = ['vr', 'baab', 'abbb', 'fc', 'bbb', 'cc']
    paramse = parse_args(['-C1', '-n', 'bbb'])
    grep(lines, paramse)
    print(lines)


if __name__ == '__main__':
    main()
