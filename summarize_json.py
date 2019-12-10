"""Summarizes the contents of a JSON file"""
# Created by Philip Guo on 2013-07-18 (https://github.com/pgbovine/json-summarizer)
# Edited by Jethro Lee on 2019-11-01 (https://github.com/dlemfh/json-summarizer)
from __future__ import print_function

import json
import sys
from collections import defaultdict, OrderedDict, Counter
from functools import reduce
from math import floor
from operator import add
from statistics import mean
from typing import List

# Print up to M chars for strings
M_CHARS = 50
# Indent format
INDENT = '    '
# Comment format
COMMENT = '  # '


# Define how to summarize list of numbers
def stats(lst: List, int_type=False, round_to=2, show_count=5, show_all=10):
    cnt = Counter(lst).most_common()
    if len(cnt) == 1:
        return lst[0]
    elif len(cnt) <= show_count and cnt[0][1] > 1:
        return ', '.join('{}{{{}}}'.format(*c) for c in cnt)
    elif len(lst) <= show_all:
        return ', '.join(map(str, sorted(lst)))
    else:
        lst_mean = mean(lst)
        if int_type and isinstance(lst_mean, float):
            lst_mean = '{}.x'.format(floor(lst_mean))
        else:
            lst_mean = round(lst_mean, round_to)
        return '[min: {}, max: {}, mode: {}, mean: {}, uniq: {}, cnt: {}]'.format(
            min(lst), max(lst), cnt[0][0], lst_mean, len(cnt), len(lst))


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
            lens_lst = list(map(len, lst))
            if newline:
                print(indent + '# LEN: {}'.format(stats(lens_lst, int_type=True)))
            print(prefix + '[')
            if not newline:
                print(indent + COMMENT + 'LEN: {}'.format(stats(lens_lst, int_type=True)))
            summarize_list_of_lists(lst, indent + INDENT)
            print(indent + '],')
        elif ht == 'int':
            print(prefix + ht + ',')
            summarize_list_of_numbers(lst, indent, of_type=int)
        elif ht == 'float':
            print(prefix + ht + ',')
            summarize_list_of_numbers(lst, indent, of_type=float)
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
        print(prefix + '<heterogeneous-type: ' + ', '.join(
            '{} {}(s)'.format(c, t) for t, c in type_dict.items()) + '>,')


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


def summarize_list_of_numbers(lst, indent, of_type=None):
    # summary-stats
    s = stats(lst, int_type=(of_type is int))

    # singleton
    if isinstance(s, (int, float)):
        print(indent + COMMENT + str(s))
        return

    # else
    print(indent + COMMENT + s, end='')

    # check if sorted
    if all(i <= j for i, j in zip(lst, lst[1:])):
        print(' *ascending*')
    elif all(i >= j for i, j in zip(lst[1:], lst)):
        print(' *descending*')
    else:
        print()


def summarize_list_of_strings(lst, indent):
    # count occurrences
    hist = Counter(lst).most_common()

    # ASCII strings? (sample first three words to find out)
    is_ascii = all(ord(letter) < 256 for word in lst[:3] for letter in word[::3])

    # max m chars for strings
    max_m = M_CHARS if is_ascii else M_CHARS // 2

    # if only singletons, print first example (up to m chars)
    if len(hist) == len(lst):
        example = lst[0][:max_m] + ('...' if lst[0][max_m:] else '')
        print(indent + COMMENT + repr(example) + '{1}, ...', end='')
        print('[{} singleton(s)]'.format(len(hist)))

    # print n common occurrences (up to total m chars)
    else:
        n_common = []
        total_chars = 0
        for occurrence, count in hist:
            formatted = '{}{{{}}}'.format(repr(occurrence), count)
            n_common.append(formatted)
            total_chars += len(formatted)
            if total_chars > max_m:
                break
        more = ', ...' if len(n_common) < len(hist) else ' '
        print(indent + COMMENT + ', '.join(n_common) + more, end='')
        print('[{} uniq val(s)]'.format(len(hist)))


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
        flattened_lst = reduce(add, lst)
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
        print('# LEN: {}'.format(len(o)))
        print('[')
        summarize_list(o, INDENT, newline=True)
        print(']')
    else:
        print(repr(o))
    print('```')
