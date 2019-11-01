"""Summarizes the contents of a JSON file"""
# Created by Philip Guo on 2013-07-18
# Edited by Jethro Lee on 2019-11-01
from __future__ import print_function

import sys
import json
import operator
from statistics import mean
from functools import reduce
from collections import defaultdict, OrderedDict

# Print N most common occurrences
N_MOST_COMMON = 3
# Print up to M chars for strings
M_CHARS = 50
# Indent format
INDENT = '    '
# Comment format
COMMENT = '  # '


# Return summary-stats of given list of numbers
def stats(lst):
    lst = list(lst)
    st = set(lst)
    # if singleton
    if len(st) == 1:
        return lst[0]
    return '[min: {}, mean: {}, max: {}, uniq: {}, cnt: {}]'.format(
        min(lst), mean(lst), max(lst), len(st), len(lst))


# Return dict with keys as Python-types, values as counts
def analyze_types(lst):
    ret = defaultdict(int)
    for e in lst:
        if isinstance(e, dict):
            ret['dict'] += 1
        elif isinstance(e, list):
            ret['list'] += 1
        elif isinstance(e, bool):
            ret['bool'] += 1
        elif isinstance(e, str):
            ret['str'] += 1
        elif isinstance(e, int):
            ret['int'] += 1
        elif isinstance(e, float):
            ret['float'] += 1
        else:
            assert e is None
            ret['None'] += 1
    return ret


# Return 'dict', 'list', 'bool', 'str', 'int', 'float', or 'None'
# if type_dict is COMPLETELY HOMOGENEOUS, otherwise return None
def get_homogeneous_type(type_dict):
    non_zero = [t for t, c in type_dict.items() if c > 0]
    if len(non_zero) == 1:
        return non_zero[0]
    else:
        return None


def summarize_dict(d, indent):
    for k, v in d.items():
        # print key
        print(indent + repr(k) + ':', end=' ')

        # print value
        if isinstance(v, dict):
            print('{')
            summarize_dict(v, indent + INDENT)
            print(indent + '},')
        elif isinstance(v, list) and v:
            print('[')
            print(indent + COMMENT + 'LEN: {}'.format(len(v)))
            summarize_list(v, indent + INDENT, newline=True)
            print(indent + '],')
        else:
            print(repr(v) + ',')


def summarize_list(lst, indent, newline=False):
    type_dict = analyze_types(lst)
    ht = get_homogeneous_type(type_dict)
    prefix = indent if newline else ''

    # Empty list
    if not lst:
        pass

    # Homogeneous list
    elif ht:
        if ht == 'dict':
            print(prefix + '{')
            summarize_list_of_dicts(lst, indent + INDENT)
            print(indent + '},')
        elif ht == 'list':
            print(prefix + '[')
            print(indent + COMMENT + 'LEN: {}'.format(stats(map(len, lst))))
            summarize_list_of_lists(lst, indent + INDENT)
            print(indent + '],')
        elif ht == 'int':
            print(prefix + ht + ',')
            summarize_list_of_numbers(lst, indent)
        elif ht == 'float':
            print(prefix + ht + ',')
            summarize_list_of_numbers(lst, indent)
        elif ht == 'str':
            print(prefix + ht + ',')
            summarize_list_of_strings(lst, indent)
        elif ht == 'bool':
            print(prefix + ht + ',')
            summarize_list_of_bools(lst, indent)
        else:
            assert ht == 'None'
            print(prefix + ht + ',')
            # summarize_list_of_nulls(lst, indent)

    # Heterogeneous list
    else:
        print(prefix + 'heterogeneous: ' + ', '.join(
            '{} {}(s)'.format(c, t) for t, c in type_dict.items()))


def summarize_list_of_dicts(lst, indent):
    field_counts = defaultdict(int)
    total = len(lst)

    for e in lst:
        assert isinstance(e, dict)
        for k in e.keys():
            field_counts[k] += 1

    for f, c in field_counts.items():
        print(indent + repr(f), end='')
        if c < total:
            sublist = [e[f] for e in lst if f in e]
            print(' ({} of {} records):'.format(c, total), end=' ')
        else:
            sublist = [e[f] for e in lst]
            print(':', end=' ')

        summarize_list(sublist, indent)


def summarize_list_of_numbers(lst, indent):
    # summary-stats
    s = stats(lst)

    # singleton
    if isinstance(s, (int, float)):
        print(indent + COMMENT + str(s))
        return

    # multiple
    print(indent + COMMENT + s, end='')

    # test sorted or reverse-sorted
    if all(i <= j for i, j in zip(lst, lst[1:])):
        print(' *sorted*')
    elif all(i >= j for i, j in zip(lst[1:], lst)):
        print(' *reverse-sorted*')
    else:
        print()


def summarize_list_of_strings(lst, indent):
    hist = defaultdict(int)
    for e in lst:
        hist[e] += 1

    # if only singletons, print first example (up to M chars)
    if len(set(hist.values())) == 1 and list(hist.values())[0] == 1:
        ex = lst[0][:M_CHARS] + ('...' if lst[0][M_CHARS:] else '')
        print(indent + COMMENT + repr(ex) + ', ...')
        return

    # print N most common occurrences
    n_cmn = ('{} x {}'.format(repr(k), v) for (k, v), _ in zip(
        sorted(hist.items(), key=lambda x: x[1], reverse=True),
        range(N_MOST_COMMON)))
    more = ', ...' if len(hist) > N_MOST_COMMON else ''
    print(indent + COMMENT + ', '.join(n_cmn) + more)

    # print number of unique elements
    print(indent + COMMENT + '{} unique value(s)'.format(len(hist)))


def summarize_list_of_bools(lst, indent):
    num_t = num_f = 0
    for e in lst:
        if e is True:
            num_t += 1
        else:
            assert e is False
            num_f += 1
    print(indent + COMMENT + 'True: {}, False: {}'.format(num_t, num_f))


def summarize_list_of_lists(lst, indent):
    if not lst:
        return

    # analyze types of each constituent sublist
    hts = set()
    for e in lst:
        type_dict = analyze_types(e)
        ht = get_homogeneous_type(type_dict)
        if ht:
            hts.add(ht)

    if not hts:
        print(indent + '[heterogeneous sub-lists]')
    elif len(hts) == 1:
        # homogeneous_type = list(hts)[0]
        # flatten the list and recurse, tricky tricky!
        flattened_lst = reduce(operator.add, lst)
        if flattened_lst:
            summarize_list(flattened_lst, indent, newline=True)
        else:
            print(indent + 'empty lists')
    else:
        print(indent + ', '.join(sorted(hts)) + ' (heterogeneous)')


if __name__ == "__main__":
    # Check args
    if len(sys.argv) != 2:
        print('\n  Usage: python summarize_json.py <file.json>')
        sys.exit(0)

    # Check version
    if sys.version_info < (3, 5):
        raise Exception('You need to run this with Python>=3.5')

    # Open & load
    with open(sys.argv[1], encoding='utf-8') as file:
        o = json.load(file, object_pairs_hook=OrderedDict)

    # Print
    print('```py')
    if isinstance(o, dict):
        print('{')
        summarize_dict(o, INDENT)
        print('}')
    elif isinstance(o, list) and o:
        print('# TOTAL COUNT: {}'.format(len(o)))
        print('[')
        summarize_list(o, INDENT, newline=True)
        print(']')
    else:
        print(repr(o))
    print('```')
