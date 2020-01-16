"""Summarizes the contents of a JSON file"""
# Created by Philip Guo on 2013-07-18 (https://github.com/pgbovine/json-summarizer)
# Updated by Jethro Lee on 2019-11-01 (https://github.com/dlemfh/json-summarizer)
from __future__ import print_function

import json
import sys
from collections import defaultdict, OrderedDict, Counter
from itertools import islice, starmap, chain
from math import floor
from operator import itemgetter
from statistics import mean
from typing import Tuple, Optional

# Print up to M chars for strings
M_CHARS = 50
# Indent format
INDENT = '    '
# Comment format
COMMENT = '  # '

# TODO: Make as program argument
DEPTH = 0


# Trim string
def trim(string, to):
    string = str(string)
    return string[:to] + (string[to:] and '...')


# Lessen list
def lessen(lst, to, using=lambda x: x):
    n, m = 0, 0
    for n, element in enumerate(lst):
        m += len(str(using(element))) + 3
        if m > to:
            break
    else:
        n += 1
    return islice(lst, n), n


# Stringify list
def stringify(lst, to):
    string = '['
    if lst:
        lessened, n = lessen(lst, to)
        if n > 0:
            string += ', '.join(map(repr, lessened))
        else:
            if isinstance(lst[0], str):
                string += repr(trim(lst[0], to))
            else:
                string += trim(lst[0], to)
        if n < len(lst):
            string += ', ...'
    string += ']'
    return string


# Return formatted string
def formatted(entry, count):
    return '{}{{{}}}'.format(entry, count)


# Custom printing function
def pprint(string, indent=0, comment=False, **kwargs):
    prefix = indent * INDENT
    if comment:
        prefix += COMMENT
    print(prefix + string, **kwargs)


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
        return '(min: {}, max: {}, mode: {}, mean: {}, uniq: {}, total: {})'.format(
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


# TODO: deprecate and allow heterogeneous types by default
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
        pprint('{}:'.format(repr(k)), indent=indent, end=' ')

        # print value
        if isinstance(v, dict):
            pprint('{')
            summarize_dict(v, indent + 1)
            pprint('},', indent=indent)
        elif isinstance(v, list) and v:
            pprint('[')
            pprint('COUNT: {}'.format(len(v)), indent=indent, comment=True)
            summarize_list(v, indent + 1, newline=True)
            pprint('],', indent=indent)
        else:
            pprint('{},'.format(repr(v)))


def summarize_list(lst, indent, newline=False):
    type_dict = analyze_types(lst)
    ht, optional = get_homogeneous_type(type_dict)
    # optional = 'None' in type_dict

    # Empty list
    if not lst:
        pass

    # Homogeneous list
    elif ht and not optional:
        if ht == 'dict':
            pprint('{', indent=(indent if newline else 0))
            summarize_list_of_dicts(lst, indent + 1)
            pprint('},', indent=indent)
        elif ht == 'list':
            # TODO: group into separate function
            types = set(chain.from_iterable(map(analyze_types, lst)))
            if types == {'dict'} or types == {'list'}:
                if newline:
                    pprint('# COUNT: {}'.format(stats(map(len, lst), int_type=True)), indent=indent)
                pprint('[', indent=(indent if newline else 0))
                if not newline:
                    pprint('COUNT: {}'.format(stats(map(len, lst), int_type=True)), indent=indent, comment=True)
                flatten_list_of_lists(lst, indent + 1)
                pprint('],', indent=indent)
            else:
                types = set(chain.from_iterable(map(analyze_types, lst)))
                if len(types) == 0:
                    pprint('List,', indent=(indent if newline else 0))
                elif len(types) == 1:
                    pprint('List[{}],'.format(next(iter(types))), indent=(indent if newline else 0))
                else:
                    pprint('List[Union[{}]],'.format(', '.join(types)), indent=(indent if newline else 0))
                pprint('LEN: {}'.format(stats(map(len, lst), int_type=True)), indent=indent, comment=True)
                summarize_list_of_lists(lst, indent)
        elif ht == 'str':
            pprint('{},'.format(ht), indent=(indent if newline else 0))
            summarize_list_of_strings(lst, indent)
        elif ht == 'int':
            pprint('{},'.format(ht), indent=(indent if newline else 0))
            summarize_list_of_numbers(lst, indent, of_type=int)
        elif ht == 'float':
            pprint('{},'.format(ht), indent=(indent if newline else 0))
            summarize_list_of_numbers(lst, indent, of_type=float)
        elif ht == 'bool':
            pprint('{},'.format(ht), indent=(indent if newline else 0))
            summarize_list_of_bools(lst, indent)
        else:
            assert ht == 'None'
            pprint('{},'.format(ht), indent=(indent if newline else 0))
            summarize_list_of_nulls(lst, indent)

    # # Optionally homogeneous list of lists
    # elif ht and optional and ht == 'list':
    #     lst = (e for e in lst if e is not None)
    #     types = set(chain.from_iterable(map(analyze_types, lst)))
    #     if len(types) == 0:
    #         print(prefix + 'Optional[List],')
    #     elif len(types) == 1:
    #         print(prefix + 'Optional[List[{}]],'.format(next(iter(types))))
    #     else:
    #         print(prefix + 'Optional[List[Union[{}]]],'.format(', '.join(types)))
    #     print(indent + COMMENT + 'LEN: {}'.format(stats(map(len, lst), int_type=True)))
    #     summarize_list_of_lists(lst, indent)

    # Optionally homogeneous list
    elif ht and optional and ht in {'str', 'int', 'float', 'bool'}:
        lst = (e for e in lst if e is not None)
        pprint('Optional[{}],'.format(ht), indent=(indent if newline else 0))
        if ht == 'str':
            summarize_list_of_strings(lst, indent)
        elif ht == 'int':
            summarize_list_of_numbers(lst, indent, of_type=int)
        elif ht == 'float':
            summarize_list_of_numbers(lst, indent, of_type=float)
        elif ht == 'bool':
            summarize_list_of_bools(lst, indent)
        pprint('None: {}'.format(type_dict['None']), indent=indent, comment=True)
        # TODO: heterogeneous list -> {types} + multiple-line summary
        # TODO: optional list -> Optional[List[type]]

    # Heterogeneous list
    else:
        pprint('<heterogeneous-type: {}>,'.format(
                   ', '.join('{} {}(s)'.format(c, t) for t, c in type_dict.items())
               ), indent=(indent if newline else 0))


def summarize_list_of_dicts(lst, indent):
    field_counts = Counter(f for d in lst for f in d)
    total = len(list(lst))

    for f, c in field_counts.items():
        pprint(repr(f), indent=indent, end='')
        if c < total:
            sublist = [d[f] for d in lst if f in d]
            pprint(' ({} of {} records):'.format(c, total), end=' ')
        else:
            sublist = [d[f] for d in lst]
            pprint(':', end=' ')

        summarize_list(sublist, indent)


def summarize_list_of_nulls(lst, indent):
    pprint('None: {}'.format(len(lst)), indent=indent, comment=True)


def summarize_list_of_bools(lst, indent):
    count = Counter(lst)
    pprint('True: {}, False: {}'.format(count[True], count[False]), indent=indent, comment=True)


def summarize_list_of_numbers(lst, indent, of_type=None):
    # summary-stats
    summary = stats(lst, int_type=(of_type is int))

    # singleton
    if isinstance(summary, (int, float)):
        pprint(str(summary), indent=indent, comment=True)

    # else
    else:
        pprint(summary, indent=indent, comment=True, end='')

        # check if sorted
        if all(i <= j for i, j in zip(lst, islice(lst, 1, None))):
            pprint(' *ASC*')
        elif all(i >= j for i, j in zip(lst, islice(lst, 1, None))):
            pprint(' *DESC*')
        else:
            pprint('')


def summarize_list_of_strings(lst, indent):
    # count occurrences
    lst = list(lst)
    hist = Counter(lst).most_common()

    # ASCII? (sample first three to find out)
    is_ascii = all(ord(letter) < 256 for word in lst[:3] for letter in word[::3])

    # summarize using max m chars
    max_m = M_CHARS if is_ascii else M_CHARS // 2

    # if only 1 unique occurrence, print up to m chars
    if len(hist) == 1:
        occurrence, count = hist[0]
        summary = formatted(repr(trim(occurrence, to=max_m)), count)
        pprint(summary, indent=indent, comment=True)

    # if only singletons, print first example (up to m chars)
    elif len(hist) == len(lst):
        example = lst[0]
        summary = formatted(repr(trim(example, to=max_m)), 1)
        pprint(summary, indent=indent, comment=True, end='')
        pprint(', ...({} singletons)'.format(len(hist)))

    # print n most common occurrences (up to total m chars)
    else:
        n_common, n = lessen(hist, to=max_m, using=itemgetter(0))
        if n > 0:
            summary = ', '.join(
                formatted(repr(occurrence), count)
                for occurrence, count in n_common)
        else:
            occurrence, count = hist[0]
            summary = formatted(repr(trim(occurrence, to=max_m)), count)
        if n < len(hist):
            summary += ', ...({} uniq, {} total)'.format(len(hist), len(lst))
        pprint(summary, indent=indent, comment=True)


def summarize_list_of_lists(lst, indent):
    # count sublists
    lst = list(map(tuple, lst))
    hist = Counter(lst).most_common()

    # ASCII? (sample first three to find out)
    is_ascii = all(
        ord(letter) < 256
        for word in islice(map(str, lst), 3)
        for letter in islice(word, None, None, 3))

    # summarize using max m chars
    max_m = M_CHARS if is_ascii else M_CHARS // 2

    # if only 1 unique occurrence, print up to m chars
    if len(hist) == 1:
        sublist, count = hist[0]
        summary = formatted(stringify(sublist, to=max_m), count)
        pprint(summary, indent=indent, comment=True)

    # if only singletons, print first example (up to m chars)
    elif len(hist) == len(lst):
        sublist = lst[0]
        summary = formatted(stringify(sublist, to=max_m), 1)
        pprint(summary, indent=indent, comment=True, end='')
        pprint(', ...({} singletons)'.format(len(hist)))

    # print n most common occurrences (up to total m chars)
    else:
        n_common, n = lessen(hist, to=max_m, using=itemgetter(0))
        if n > 0:
            summary = ', '.join(
                formatted(list(sublist), count)
                for sublist, count in n_common)
        else:
            sublist, count = hist[0]
            summary = formatted(stringify(sublist, to=max_m), count)
        if n < len(hist):
            summary += ', ...({} uniq, {} total)'.format(len(hist), len(lst))
        pprint(summary, indent=indent, comment=True)


def flatten_list_of_lists(lst, indent):
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
        pprint('(heterogeneous sub-lists)', indent=indent)
    elif len(hts) == 1:
        # homogeneous_type = list(hts)[0]
        # flatten the list and recurse, tricky tricky!
        flattened_lst = list(chain.from_iterable(lst))
        if flattened_lst:
            summarize_list(flattened_lst, indent, newline=True)
        else:
            pprint('empty lists', indent=indent)
    else:
        pprint('{} (heterogeneous)'.format(', '.join(sorted(hts))), indent=indent)


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
    pprint('```py')
    if isinstance(o, dict):
        pprint('{')
        summarize_dict(o, 1)
        pprint('}')
    elif isinstance(o, list) and o:
        pprint('# COUNT: {}'.format(len(o)))
        pprint('[')
        summarize_list(o, 1, newline=True)
        pprint(']')
    else:
        pprint(repr(o))
    pprint('```')
