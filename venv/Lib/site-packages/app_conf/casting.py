from __future__ import absolute_import, print_function
from .common import nil, throw, Exc, is_str, PY2, breakpoint
from ast import literal_eval
from functools import partial
import attr


# --------------------------------------------------------- Casting From Strings

t_attr = type(attr.ib())


class _:
    def __(self):
        pass


# for PY2:
t_funcs = (type(lambda x: x), type(_.__), type(partial(_.__)))


def to_dict(s):
    if s.startswith('{'):
        return literal_eval(s)
    try:
        return dict(
            [
                (k.strip(), v.strip())
                for k, v in [kv.split(':', 1) for kv in s.split(',')]
            ]
        )
    except:
        throw(Exc.cannot_cast_to_dict, val=s)


def to_list(s):
    if s.startswith('['):
        return literal_eval(s)
    return [i.strip() for i in s.split(',')]


def to_tuple(s):
    return tuple(to_list(s))


attr_nothing = attr.ib()._default

# fmt: off
none = type(None)
casters = {
    int  : lambda s: int(s),
    bool : lambda s, truths=("True", "1", "true"),
                     falses=("False", "false", "0", "nil",):
           True if s in truths else False,
    none : lambda s, nones=("None", "nil", "none", "0"):
           None if s in nones else s,
    float: lambda s: float(s),
    dict : to_dict,
    list : to_list,
    tuple: to_tuple,
    str  : lambda s: str(s),
    type(attr_nothing): lambda s: str(s)
}
casters_by_name = dict([(c.__name__, c) for c in casters])
# fmt: on

deep_types = list, tuple, dict

cls_type = '\x02'


def cast(s, dflt, deep=True, strict=True):
    if s == 'i_no_dflt':
        breakpoint()
    if not s:
        return dflt
    if is_str(dflt) or dflt == nil:
        return s
    into_typ = dflt if isinstance(dflt, type) else type(dflt)
    if into_typ == str:
        return s
    caster = casters.get(into_typ)
    if not caster:
        if into_typ == dflt:
            # this is an inner class:
            return cls_type
    try:
        if not caster:
            raise
        res = caster(s)
        if res == nil:
            try:
                throw(Exc.cannot_cast, val=s, into_type=into_typ.__name__)
            except Exception as ex:
                breakpoint()
                i = 1
        return res
    except Exception as ex:
        breakpoint()
        raise Exception(
            'Type Error: Expected %s, got %s [%s]'
            % (type(dflt).__name__, s, str(ex))
        )


import attr

if PY2:

    def new_style(cls):
        return (
            cls
            if is_new(cls)
            else type(cls.__name__, (cls, object), vars(cls))
        )

    # attr.s needs new style classes:
    def attrcls(cls):
        return attr.s(new_style(cls))

    class a:
        pass

    class n(object):
        pass

    is_old = lambda o, a=type(a): type(o) == a
    is_new = lambda o, n=type(n): type(o) == n

    def to_new_style(cls):
        for k in [s for s in dir(cls) if not s.startswith('_')]:
            v = getattr(cls, k)
            if v in casters:
                continue
            if is_new(v):
                to_new_style(v)
            if is_old(v):
                setattr(cls, k, to_new_style(v))
        return new_style(cls)


else:
    attrcls = attr.s
    to_new_style = lambda cls: cls
