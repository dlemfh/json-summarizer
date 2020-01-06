"""Summarizes the contents of a JSON file"""
# Created by Philip Guo on 2013-07-18 (https://github.com/pgbovine/json-summarizer)
# Updated by Jethro Lee on 2019-11-01 (https://github.com/dlemfh/json-summarizer)
from __future__ import print_function

import json
import sys
from collections import defaultdict, OrderedDict, Counter
from functools import reduce
from itertools import islice, starmap
from math import floor
from operator import add
from statistics import mean
from typing import Tuple, Optional

# Print up to M chars for strings
M_CHARS = 50
# Indent format
INDENT = '    '
# Comment format
COMMENT = '  # '


# Define how to format entry & count
def formatted(entry, count, shorten_to=None):
    if shorten_to:
        entry = entry[:shorten_to] + ('...' if entry[shorten_to:] else '')
    return '{}{{{}}}'.format(repr(entry), count)


# Define how to summarize list of numbers
def stats(lst, int_type=False, round_to=2, show_count=5, show_all=10):
    lst = list(lst)
    cnt = Counter(lst).most_common()
    if len(cnt) == 1:
        return lst[0]
    elif len(cnt) <= show_count and cnt[0][1] > 1:
        return ', '.join(starmap(formatted, cnt))
    elif len(lst) <= show_all:
        return ', '.join(map(str, sorted(lst)))
    else:
        lst_mean = mean(lst)
        if int_type and isinstance(lst_mean, float):
            lst_mean = '{}.x'.format(floor(lst_mean))
        else:
            lst_mean = round(lst_mean, round_to)
        return '[min: {}, max: {}, mode: {}, mean: {}, uniq: {}, total: {}]'.format(
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


def get_homogeneous_type(type_dict) -> Tuple[Optional[str], bool]:
    """
    Returns
    -------
    Optional[str]
        Homogeneous-type, if any.
        Ex) 'dict', 'list', 'str', 'int', 'float', 'bool', 'None', or None
    bool
        Whether optionally typed.
    """
    # completely homogeneous
    if len(type_dict) == 1:
        return next(iter(type_dict)), False
    # optionally homogeneous
    elif len(type_dict) == 2 and 'None' in type_dict:
        return next(t for t in type_dict if t != 'None'), True
    # heterogeneous
    return None, False


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
            print(indent + COMMENT + 'COUNT: {}'.format(len(v)))
            summarize_list(v, indent + INDENT, newline=True)
            print(indent + '],')
        else:
            print(repr(v) + ',')


def summarize_list(lst, indent, newline=False):
    type_dict = analyze_types(lst)
    ht, optional = get_homogeneous_type(type_dict)
    prefix = indent if newline else ''

    # Empty list
    if not lst:
        pass

    # Homogeneous list
    elif ht and not optional:
        if ht == 'dict':
            print(prefix + '{')
            summarize_list_of_dicts(lst, indent + INDENT)
            print(indent + '},')
        elif ht == 'list':
            if newline:
                print(indent + '# COUNT: {}'.format(stats(map(len, lst), int_type=True)))
            print(prefix + '[')
            if not newline:
                print(indent + COMMENT + 'COUNT: {}'.format(stats(map(len, lst), int_type=True)))
            summarize_list_of_lists(lst, indent + INDENT)
            print(indent + '],')
        elif ht == 'str':
            print(prefix + ht + ',')
            summarize_list_of_strings(lst, indent)
        elif ht == 'int':
            print(prefix + ht + ',')
            summarize_list_of_numbers(lst, indent, of_type=int)
        elif ht == 'float':
            print(prefix + ht + ',')
            summarize_list_of_numbers(lst, indent, of_type=float)
        elif ht == 'bool':
            print(prefix + ht + ',')
            summarize_list_of_bools(lst, indent)
        else:
            assert ht == 'None'
            print(prefix + ht + ',')
            # summarize_list_of_nulls(lst, indent)

    # Optionally homogeneous list
    elif ht and optional and ht in {'str', 'int', 'float', 'bool'}:
        lst = (e for e in lst if e is not None)
        print(prefix + 'Optional[{}]'.format(ht) + ',')
        if ht == 'str':
            summarize_list_of_strings(lst, indent)
        elif ht == 'int':
            summarize_list_of_numbers(lst, indent, of_type=int)
        elif ht == 'float':
            summarize_list_of_numbers(lst, indent, of_type=float)
        elif ht == 'bool':
            summarize_list_of_bools(lst, indent)
        print(indent + COMMENT + 'None: {}'.format(type_dict['None']))
        # TODO: summarize_list_of_nulls
        # TODO: heterogeneous list -> {types} + multiple-line summary
        # TODO: optional list -> Optional[List[type]]

    # Heterogeneous list
    else:
        print(prefix + '<heterogeneous-type: ' + ', '.join(
            '{} {}(s)'.format(c, t) for t, c in type_dict.items()) + '>,')


def summarize_list_of_dicts(lst, indent):
    field_counts = Counter(f for d in lst for f in d)
    total = len(list(lst))

    for f, c in field_counts.items():
        print(indent + repr(f), end='')
        if c < total:
            sublist = [d[f] for d in lst if f in d]
            print(' ({} of {} records):'.format(c, total), end=' ')
        else:
            sublist = [d[f] for d in lst]
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
    if all(i <= j for i, j in zip(lst, islice(lst, 1, None))):
        print(' *ASC*')
    elif all(i >= j for i, j in zip(islice(lst, 1, None), lst)):
        print(' *DESC*')
    else:
        print()


def summarize_list_of_strings(lst, indent):
    # count occurrences
    lst = list(lst)
    hist = Counter(lst).most_common()

    # ASCII strings? (sample first three words to find out)
    is_ascii = all(ord(letter) < 256 for word in lst[:3] for letter in word[::3])

    # max m chars for strings
    max_m = M_CHARS if is_ascii else M_CHARS // 2

    # if only 1 unique occurrence, print up to m chars
    if len(hist) == 1:
        occurrence, count = hist[0]
        summary = formatted(occurrence, count, shorten_to=max_m)
        print(indent + COMMENT + summary)

    # if only singletons, print first example (up to m chars)
    elif len(hist) == len(lst):
        example = lst[0]
        summary = formatted(example, 1, shorten_to=max_m)
        print(indent + COMMENT + summary, end='')
        print(', ...[{} singletons]'.format(len(hist)))

    # print n most common occurrences (up to total m chars)
    else:
        n, m = 0, 0
        for n, (occurrence, count) in enumerate(hist):
            m += len(occurrence) + 3
            if m > max_m:
                break
        else:
            n += 1
        if n > 0:
            summary = ', '.join(starmap(formatted, islice(hist, n)))
        else:
            occurrence, count = hist[0]
            summary = formatted(occurrence, count, shorten_to=max_m)
        if n < len(hist):
            summary += ', ...[{} uniq, {} total]'.format(len(hist), len(lst))
        print(indent + COMMENT + summary)


def summarize_list_of_bools(lst, indent):
    count = Counter(lst)
    print(indent + COMMENT + 'True: {}, False: {}'.format(count[True], count[False]))


def summarize_list_of_lists(lst, indent):
    if not lst:
        return

    # analyze types of each constituent sublist
    hts = set()
    for e in lst:
        type_dict = analyze_types(e)
        ht, optional = get_homogeneous_type(type_dict)
        if ht and not optional:
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

    # Check python version
    if sys.version_info < (3, 5):
        raise Exception('You need to run this with Python>=3.5')

    # Open & load json file
    with open(sys.argv[1], encoding='utf-8') as file:
        o = json.load(file, object_pairs_hook=OrderedDict)

    # Summarize recursively
    print('```py')
    if isinstance(o, dict):
        print('{')
        summarize_dict(o, INDENT)
        print('}')
    elif isinstance(o, list) and o:
        print('# COUNT: {}'.format(len(o)))
        print('[')
        summarize_list(o, INDENT, newline=True)
        print(']')
    else:
        print(repr(o))
    print('```')
