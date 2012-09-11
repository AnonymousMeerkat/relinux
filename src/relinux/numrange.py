# -*- coding: utf-8 -*-
'''
Number range generator
@author: Anonymous Meerkat <meerkatanonymous@gmail.com>
'''

import re

def _get_first_digit_and_rest(nums):
    num = str(nums)
    if len(num) > 1:
        return (num[0], num[1:])
    elif len(num) == 1:
        return (num[0], "")
    else:
        return ("", "")


def _generate_head(first, zeros, rest, bound):
    parts = []
    for reg in generate_to_bound(rest, bound).split('|'):
        parts.append("%s%s%s" % (first, zeros, reg))
    return "|".join(parts)


def _strip_left_repeated_digit(num, digit):
    for i, ch in enumerate(num):
        if ch != digit:
            return (digit * i, num[i:])
    return (num, "")


def generate_to_bound(num, bound):
    if bound not in ["upper", "lower"]:
        raise ValueError("bound not in ['upper', 'lower']")
    if isinstance(num, int):
        num_ = str(num)
        num = num_
    if num == "":
        return ""
    no_range_exit = "0" if bound == "lower" else "9"
    if len(num) == 1 and int(num) == int(no_range_exit):
        return no_range_exit
    if len(num) == 1 and 0 <= int(num) < 10:
        return "[0-%s]" % num if bound == "lower" else "[%s-9]" % num

    first_digit, rest = _get_first_digit_and_rest(num)
    repeated, rest = _strip_left_repeated_digit(rest, no_range_exit)
    head = _generate_head(first_digit, repeated, rest, bound)
    tail = ""
    if bound == "lower":
        if int(first_digit) > 1:
            tail = "[0-%d]" % (int(first_digit) - 1)
            tail += "[0-9]" * (len(num) - 1)
        elif int(first_digit) == 1:
            tail = "0" + "[0-9]" * (len(num) - 1)
    else:
        if int(first_digit) < 8:
            tail = "[%d-9]" % (int(first_digit) + 1)
            tail += "[0-9]" * (len(num) - 1)
        elif int(first_digit) == 8:
            tail = "9" + "[0-9]" * (len(num) - 1)
    return "|".join([head, tail]) if tail else head


def _extract_common(min_, max_):
    fd_min, rest_min = _get_first_digit_and_rest(min_)
    fd_max, rest_max = _get_first_digit_and_rest(max_)
    common = ""
    while fd_min == fd_max and fd_min != "":
        common += fd_min
        fd_min, rest_min = _get_first_digit_and_rest(rest_min)
        fd_max, rest_max = _get_first_digit_and_rest(rest_max)

    return (common, fd_min, rest_min, fd_max, rest_max)


def _generate_for_same_len_nr(min_, max_):
    assert len(str(min_)) == len(str(max_))
    common, fd_min, rest_min, fd_max, rest_max = _extract_common(min_, max_)
    starting = ending = ""
    if rest_min:
        starting = "|".join(
            "%s%s%s" % (common, fd_min, x)
            for x in generate_to_bound(rest_min, "upper").split("|"))
    else:
        starting = "%s%s" % (common, fd_min)

    if rest_max:
        ending = "|".join(
            "%s%s%s" % (common, fd_max, x)
            for x in generate_to_bound(rest_max, "lower").split("|"))
    else:
        ending = "%s%s" % (common, fd_max)
    if fd_min and fd_max and int(fd_min) + 1 > int(fd_max) - 1:
        assert starting and ending
        return "|".join([starting, ending])

    if fd_min and fd_max and int(fd_min) + 1 == int(fd_max) - 1:
        middle = "%s%d" % (common, int(fd_min) + 1)
    elif fd_min and fd_max:
        middle = common + "[%d-%d]" % (int(fd_min) + 1, int(fd_max) - 1)
    else:
        middle = common

    middle += "[0-9]" * len(rest_min)
    return "|".join([starting, middle, ending])

def gen_num_range(min_, max_, capturing=False):
    if isinstance(min_, int):
        min__ = str(min_)
        min_ = min__
    if isinstance(max_, int):
        max__ = str(max_)
        max_ = max__
    template = r"\b(?:%s)\b"
    if capturing:
        template = r"\b(%s)\b"
    nr_dig_min = len(str(min_))
    nr_dig_max = len(str(max_))
    if nr_dig_min != nr_dig_max:
        middle = ""
        for i in range(nr_dig_min, nr_dig_max - 1):
            middle += "|[1-9]"
            for x in range(i):
                middle += "[0-9]"
        starting = generate_to_bound(min_, "upper")
        ending = _generate_for_same_len_nr("1" + "0" * (len(max_) - 1), max_)
        if middle:
            return template % "|".join([starting, middle, ending])
        else:
            return template % "|".join([starting, ending])
    else:
        return template % _generate_for_same_len_nr(min_, max_)
