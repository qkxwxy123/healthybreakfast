from __future__ import absolute_import, print_function
import sys, os
from .func_sigs import signature
import textwrap
from inspect import getsource

PY2 = sys.version_info[0] < 3


def termsize():
    try:
        # that works in a pipe as well, get_terminal_size not. also not PY2:
        # windows we don't care.
        with os.popen('stty size 2>/dev/null', 'r') as fd:
            l = fd.read().split()
        r, c = [int(p) for p in l]
    except:
        if PY2:
            r, c = (25, 80)
        else:
            import shutil

            _ = shutil.get_terminal_size(fallback=(80, 25))
            r, c = _.lines, _.columns
    return r, c


def render_help(app, level=None, h=None):
    if level is None:
        level = 'h'
    sh_code = False
    if 'c' in level:
        sh_code = True
        level.replace('c', '')
    level = len(level)
    h = h or 1
    md = _show_help(app, termsize(), level, sh_code, h)
    return md


def wrap(s, size, lb='\n', ind=0):

    cols = size[-1]
    dt, wr = textwrap.dedent, textwrap.wrap
    res = [i for i in s.splitlines() if i.strip()]
    res = [lb.join(wr(l.strip(), width=cols - ind)) for l in res]
    if ind:
        i = ' ' * ind
        res = [i + l.replace('\n', '\n' + i) for l in res]
    res = lb.join(res)
    return res


ap = lambda l, a: l.append(a)

len_to_show_code_as_detail = 1000


def _show_help(app, size, level, sh_code, h):
    md, inner, ad = [], [], []

    def hl(s, lev, md=md):
        pre = '\n' if md and not md[-1].endswith('\n') else ''
        return pre + ('#' * lev + ' ' + s) + '\n'

    def docs(obj, md=md, size=size):
        d = getattr(obj, '__doc__', '')
        if d:
            ap(md, wrap(d, size=size))

    def header(app, h=h, md=md):
        p = '.'.join(app._path) if app._path else app.__class__.__name__
        ap(md, hl(p, h))
        docs(app)

    ad = ['Name Val F Dflt Descr Expl'.split(' ')]
    # fmt: off
    name      = lambda row: row[0]
    val       = lambda row: row[1]
    from_     = lambda row: row[2]
    deflt     = lambda row: row[3]
    descri    = lambda row: row[4]
    expl      = lambda row: row[5]
    # fmt: on

    def add_long_explanation(tbl):
        '''when long descr are not fitting we put under the table'''

        def f(r):
            e = expl(r)
            if not e.strip():
                return
            return '- %s: %s' % (name(r), e)

        l = [f(row) for row in tbl[1:]]

        return '\n'.join([k for k in l if k])

    def add_long_descr_and_expl(tbl):
        '''when long descr are not fitting we put under the table'''

        def f(r):
            d, e = descr[cold], expl[cole]
            if not d.strip() and not e.strip():
                return
            return '%s: %s\n%s\n' % (name(r), d, e)

        l = [f(row) for row in tbl[1:]]

        return '\n'.join([k for k in l if k])

    def params(L, size=size):
        cols = size[-1]
        l = L
        for line in L:
            line[-1] = wrap(line[-1], size, lb='<br>')

        def maxl(l, i):
            return max([len(line[i]) for line in l])

        sizes = [maxl(l, i) for i in range(len(l[0]))]
        lin = ['-' * s for s in sizes]
        # we have place for this?
        for cls in (len(sizes), len(sizes) - 1, len(sizes) - 2):
            for pre, post, mid in (('| ', ' |', ' | '), ('|', '|', '|')):
                width = pre + mid.join(lin[:cls]) + post
                if len(width) <= cols:
                    t = [
                        [line[col].ljust(sizes[col]) for col in range(cls)]
                        for line in l
                    ]
                    t.insert(1, lin[:cls])
                    t = [pre + mid.join(line) + post for line in t]
                    t = '\n'.join(t)
                    f = (
                        add_long_explanation
                        if cls == len(sizes) - 1
                        else add_long_descr_and_expl
                        if cls == len(sizes) - 2
                        else None
                    )
                    return t if not f else t + '\n\n' + f(l) + '\n'

        # classic format:
        def classic(row, sizes=sizes):
            v = val(row) or deflt(row)
            v = '[%s]' % v if v else ''
            d = descri(row)
            if d:
                v = ' ' + v
            l = '%s: %s%s' % (name(row).ljust(sizes[0]), d, v)
            e = expl(row)
            if e:
                e = e.replace('<br>', '\n')
                l += '\n'
                l += wrap(e, size, ind=sizes[0] + 2)
            return l

        return '\n'.join([classic(row) for row in l[1:]])

    header(app)
    for attr in app.__attrs_attrs__:
        n = attr.name
        m = attr.metadata
        descr = m.get('descr', '')
        long_descr = m.get('long_descr', '')
        prov, default = m.get('provider') or ' ', m.get('orig') or ''
        v = attr.default
        if str(v).startswith('req:<'):
            default = ('<%s' % v[5:]).upper()
            v = '!'
        if hasattr(v, 'factory'):
            inn = getattr(app, n)
            ap(inner, _show_help(inn, size, level - 1, sh_code, h=2))
        else:
            t = attr.type
            if n == 'xb_dflt_True':
                breakpoint()
            if type(default) == t_attr:
                default = default._default or default.type
            if type(default) == type:
                default = ''
            else:
                if str(default) == str(v):
                    default = ''
            ap(
                ad,
                [str(i) for i in (n, v, prov[0], default, descr, long_descr)],
            )

    if len(ad) > 1:
        ap(md, hl('Parameters', h + 1))
    ap(md, params(ad))
    # functions:
    funcs = [(f, getattr(app, f)) for f in dir(app)]
    funcs = [f for f in funcs if callable(f[1]) and f[0].startswith('do_')]

    def func(n, func, level=level, size=size, h=h, md=md, sh_code=sh_code):
        n = n[3:] if n.startswith('do_') else n
        ap(md, hl(n, h + 2))
        docs(func)
        sig = signature(func)
        if sh_code:

            try:
                src = getsource(func)
                ind = len(src) - len(src.lstrip())
                src = remove_doc(func, src, ind)
                src = '\n'.join([s[ind:] for s in src.splitlines()])
                src = '\n```python=\n%s\n```' % src
                if len(src) > len_to_show_code_as_detail:
                    s = func.__name__
                    s += str(sig)
                    src = as_details(s, src)
                ap(md, src)
            except:
                sh_code = False
        if not sh_code:
            ap(md, '')
            ap(md, '> %s%s' % (func.__name__, signature(func)))

        return n

    if funcs:
        ap(md, hl('Actions', h + 1))
        [func(*f) for f in funcs]

    [ap(md, '\n---\n' + p) for p in inner]
    pr, po = '', ''
    if h == 1:
        pr += '\n'
        po += '\n'
    return pr + '\n'.join(md) + po


def remove_doc(func, src, ind):
    '''docstrings already shown'''
    d, a1, a2 = func.__doc__ or 'xxx-xxx', "'''", '"""'
    for a in a1, a2:
        ads = '%s%s%s' % (a, d, a)
        k = src.split(ads, 1)
        if len(k) < 2:
            continue
        return k[0].rstrip() + '\n' + (' ' * ind + ' ' * 4) + k[1].strip()
    return src


def as_details(sum, body):
    return '''
<details>
    <summary>%s</summary>
%s
</details>
    ''' % (
        sum,
        body,
    )


import attr

t_attr = type(attr.ib())
