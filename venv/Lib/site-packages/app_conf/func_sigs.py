
from __future__ import absolute_import, print_function
from .common import nil, PY2, breakpoint

if PY2:
    from funcsigs import signature
else:
    from inspect import signature
from .casting import cast


def map_args_to_func_sig(
    f, cli, map_from=-1, prefer_positional=True, deep=True, cast=cast
):
    '''
    inspect.signature based version.

    Py2: This WOULD work using the signature simulation for py2 (funcsigs)
    from https://funcsigs.readthedocs.io/en/0.4/
    but perf is lousy. See below, for 2 we do it in getargspec

    Maybe it can be done more effective, not sure yet:

    '''
    if map_from == -1:
        # signature does not deliver cls or self, so no effort here:
        map_from = 0
    sig_dict = signature(f).parameters
    va_pos, have_va, pos_params = 0, False, []
    i = 0
    for n, p in sig_dict.items():
        i += 1
        if i <= map_from:
            continue
        if p.kind == p.VAR_POSITIONAL:
            have_va = True
            break
        va_pos += 1
        pos_params.append(n)

    args = [nil for i in pos_params]
    kw = {}

    def default(n):
        d = sig_dict.get(n)
        if not d:
            return nil
        return d.default if d.default != d.empty else nil

    idx, leng = -1, len(cli) - 1
    while idx < leng:
        idx += 1
        n, v = cli[idx]
        if v != 'is_set':
            d = default(n)
            v = cast(v, d, deep)
            if have_va and n in pos_params:
                args[pos_params.index(n)] = v
                pos_params.remove(n)
            else:
                kw[n] = v
                pos_params.remove(n) if n in pos_params else None
        else:
            if pos_params:
                n = pos_params.pop(0)
                d = default(n)
                v = cast(v, d, deep)
            if have_va:
                app = True
                for i in range(0, len(args)):
                    if args[i] == nil:
                        args[i] = v
                        app = False
                        break
                if app:
                    args.append(v)
            else:
                kw[n] = v
    argt = ()
    for a in args:
        if a != nil:
            argt += (a,)
    if prefer_positional:
        for p in list(sig_dict.keys())[map_from:]:
            v = sig_dict[p]
            if v.kind != v.POSITIONAL_OR_KEYWORD:
                break
            vm = kw.pop(p, nil)
            if vm != nil:
                argt += (vm,)

    return argt, kw


def repl_func_defaults(func, dflts):
    orig = func.__defaults__
    pos = 0
    new = ()
    for n, p in signature(func).parameters.items():
        if p.default == p.empty:
            continue
        new += (dflts.pop(n, orig[pos]),)
        pos += 1
    if PY2:
        func.__func__.__defaults__ = new
    else:
        func.__defaults__ = new
