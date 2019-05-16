from __future__ import absolute_import, print_function
from .version import __version__
from .common import nil, PY2, Exc, throw, pdt, now, is_str, breakpoint
from .common import set_log, info, debug, warn, error
from .func_sigs import map_args_to_func_sig, repl_func_defaults
from .casting import cast, casters, to_new_style, attrcls
import time
import attr
import string
import sys
import os
import json
from ast import literal_eval
from collections import OrderedDict
from appdirs import user_config_dir
from functools import partial

# -------------------------------------------------------------- Key Shortening


def shorten(k):
    '''k an attrname like foo_bar_baz.
    We return fbb, fbbaz, which we'll match startswith style if exact match
    not unique.
    '''
    parts = k.split('_')
    r = ''.join([s[0] for s in parts if s])
    return r, r + parts[-1][1:]


def to_shorts(longs, shorten=shorten):
    '''build a dict of short forms pointing to their original forms

    Collisions: We'll complain for foo_bar_baz and foo_baz_baz attrs
    and don't try to be smart here. Thats why we need the 'have' list.
    '''
    m = dict()
    have = set()
    for k in longs:
        m[k] = k  # allowed match stsarts with also ok
        sh, sh_ending = shorten(k)
        if sh in have:
            # thats ok, colliding shorts
            m.pop(sh)
        else:
            m[sh] = k
            have.add(sh)
            if sh == sh_ending:
                continue
        if sh_ending in have:
            # developer has to rename the attribute if he wants the feature
            throw(
                Exc.cannot_build_unique_short_form,
                key=k,
                colliding=sh_ending,
                have=have,
            )
        m[sh_ending] = k
        have.add(sh_ending)
    return m


def get_long(short_key, shorts):
    try:
        return shorts[short_key]
    except KeyError as ex:
        r = [k for k in shorts if k.startswith(short_key)]
        if len(r) > 1:
            throw(Exc.non_unique, short=short_key, have=r)
        return None if len(r) == 0 else shorts[r[0]]


def short_to_long(provider, d, attrs, ctx):
    shorts = ctx.get('shorts')
    if not shorts:
        shorts = ctx['shorts'] = to_shorts([l[0] for l in attrs if l])
    nd = dict()
    for k in d:
        try:
            nd[shorts[k]] = d[k]
        except:
            h = [p for p in shorts if p.startswith(k)]
            if len(h) > 1:
                throw(Exc.non_unique, key=k, have=h)
            if len(h) == 1:
                nd[shorts[h[0]]] = d[k]
            else:
                nd[k] = d[k]
    return nd


# ------------------------------------------------------------------------- CLI
class Provider:
    # fmt: off
    str_only             = False
    allow_short_keys     = False
    set_runner_func      = False
    allow_unknown_attrs  = True
    show_help            = None
    # fmt: on

    def get_inner(cli, d, path, attrs, cfg):
        return d.get(path[-1])


@attrcls
class CLI(Provider):
    # fmt: off
    argvd                  = attr.ib(type= dict, converter = lambda x: CLI.pre_parse_cli(x))
    switches               = attr.ib(default={}, validator = lambda *x: CLI.set_switches(*x))
    allow_short_keys       = attr.ib(True)
    set_runner_func        = attr.ib(True)
    bool_reverse_on_no_val = attr.ib(True)
    str_only               = attr.ib(True)
    allow_unknown_attrs    = attr.ib(False)
    help_switch            = attr.ib('-h')
    # fmt: on

    @staticmethod
    def pre_parse_cli(argv):
        '''just take the command line appart, w/o knowledge of app vars yet
        What we do though is to build nested dicts for f.b=bar style vars
        '''
        r, _into = dict(), CLI.into
        idx, leng = -1, len(argv) - 1
        while idx < leng:
            idx += 1
            arg = argv[idx]
            if '=' in arg:
                k, v = arg.split('=', 1)
                _into(r, k, v)
                continue
            if idx == leng:
                if arg.startswith('-') and len(arg) > 2:
                    # -hhhc -> hhhc
                    _into(r, arg[:2], arg[1:])
                else:
                    _into(r, arg, 'is_set')
            elif argv[idx + 1].startswith('-') or '=' in argv[idx + 1]:
                # next one starts with - or is a key=val assignment -> this one is
                # bool:
                _into(r, arg, 'is_set')
            else:
                idx += 1
                _into(r, arg, argv[idx])
        return r

    @staticmethod
    def into(m, k, v):
        l = k.split('.')
        for p in l[:-1]:
            m = m.setdefault(p, {})
        m[l[-1]] = v

    @staticmethod
    def set_switches(cli, attr, switches):
        if not switches:
            return
        # must preserve the order of original, can't just replace:
        d = dict()
        for k, v in cli.argvd.items():
            if not k.startswith('-'):
                d[k] = v
            else:
                try:
                    d[switches[k]] = v
                except:
                    throw(Exc.not_a_switch, found=k, known=switches)
        cli.argvd = d

    @staticmethod
    def is_switch(_, __, s):
        ''' not in use '''
        if not s in string.ascii_letters:
            throw(Exc.not_a_switch, s)

    def cfg(cli):
        hs = cli.argvd.pop(cli.help_switch, None)
        if hs is not None:
            cli.show_help = hs
        return cli.argvd


# --------------------------------------------------------------------- Environ


@attrcls
class Env(Provider):
    prefix = attr.ib(default='', type=str, converter=lambda p: (p + '_'))
    str_only = attr.ib(True)

    def build_env_dict(env):
        e = os.environ
        l = len(env.prefix)
        return dict([(k[l:], e[k]) for k in e if k.startswith(env.prefix)])

    def cfg(env):
        return env.build_env_dict()

    def get_inner(env, d, path, attrs, cfg):
        p = path[-1] + '_'
        l = len(p)
        d = dict([(k[l:], v) for k, v in d.items() if k.startswith(p)])
        return d


# ------------------------------------------------------------------------ File


@attrcls
class File(Provider):
    filename = attr.ib(
        default='', type=str, validator=lambda file, a, v: file.load(v)
    )
    _cfg = attr.ib(default={})

    def cfg(file):
        return file._cfg

    def load(file, fn):
        if not fn:
            return
        die = False
        if is_str(fn):
            die = True
        try:
            if not os.path.exists(fn):
                fn = os.path.join(user_config_dir(), fn)
            fn = os.path.abspath(fn)
            with open(fn) as fd:
                s = fd.read()
            file._cfg = json.loads(s)
        except Exception as ex:
            args = dict(msg=Exc.file_not_found, exc=ex, fn=fn)
            if die:
                throw(**args)
            debug(**args)


# --------------------------------------------------------- Programmed Defaults
t_attr = type(attr.ib())


class _:
    def __(self):
        pass


# for PY2:
t_funcs = (type(lambda x: x), type(_.__), type(partial(_.__)))


@attrcls
class Defaults:
    cls = attr.ib()
    cfg = {}


have_func = '\x04'


def walk_attrs(cls, providers, ctx):
    '''
    here we burn startup time - recursively scanning all(!) cls attrs of the app.
    have to see if we should cache the scan results.
    '''
    path = cls._path

    def nfo(cls, k):
        v = getattr(cls, k)
        t = type(v)
        ft = t in t_funcs
        if ft:
            if not k.startswith('do_'):
                return
            k = k[3:]
        return k, v, t, ft

    attrs = [nfo(cls, k) for k in dir(cls) if not k.startswith('_')]
    if path:
        providers = list(
            filter(
                lambda p: p[1],
                [
                    [p, p.get_inner(cfg, path, attrs, ctx), cast]
                    for p, cfg, cast in providers
                ],
            )
        )
    else:
        h = [l for l in [p[0].show_help for p in providers] if l is not None]
        if h:
            ctx['show_help'] = h[0]
        ctx['funcs'] = {}
    sh_help = ctx.get('show_help')
    ctx['shorts'] = None
    # if path == ('inner', 'deep'):
    #    breakpoint()
    providers = [
        p
        if not p[0].allow_short_keys
        else [p[0], short_to_long(p, p[1], attrs, ctx), p[1]]
        for p in providers
    ]
    func, have_attrs = None, set()

    for l in attrs:
        if not l:
            continue
        k, v, t, ft = l

        v_orig = v
        have_attrs.add(k)
        # if k == 'b_dflt_False':
        #    breakpoint()
        have_cfg = False
        from_prov = None
        for p in providers:
            cfg_val = p[1].get(k, nil)
            if cfg_val != nil:
                have_cfg = True
                str_only = p[2]
                from_prov = p[0].__class__.__name__
                break

        # if k == 'b_dflt_True':
        #    breakpoint()

        if t != type:
            # an instance. Like: some_bool=True
            # or a function type?
            if ft:
                if have_cfg:
                    if isinstance(cfg_val, dict):
                        repl_func_defaults(func=v, dflts=cfg_val)
                    # (else we just have 'is_set' if its the function req. to
                    # run - then we do not change defaults)
                if have_cfg and p[0].set_runner_func:
                    # might be nested in cli dict, i.e. earlier attrs still to come
                    func = [path, v]
                continue

            if t == t_attr:
                if have_cfg:
                    typ = v.type or type(v._default)
                    v._default = casters[typ](cfg_val) if str_only else cfg_val
                    # already an attr.ib:
            else:
                if have_cfg:
                    v = casters[t](cfg_val) if str_only else cfg_val
                v = attr.ib(v)
        else:
            # a typ - no value. E.g. some_bool = bool
            caster = casters.get(v)
            if caster:
                if not have_cfg:
                    if sh_help:
                        # values not required then:
                        cfg_val = v.__name__
                        caster = lambda s: 'req:<%s>' % s
                    else:
                        throw(Exc.require_value, key=k)
                v = attr.ib(caster(cfg_val) if str_only else cfg_val)
            else:
                v._path = path + (k,)
                v, func = walk_attrs(v, providers, ctx)
                # v = attr.ib(factory=lambda cls=v: cls())
                v = attr.ib(factory=lambda cls=v: cls())

        v.metadata['orig'] = v_orig
        v.metadata['provider'] = from_prov
        setattr(cls, k, v)

    # now find unknown kvs:
    for p in providers:
        # cli is a provider which sets the runner func:
        if not path:
            h = ctx.get('show_help')
            if h is not None:
                return (attrcls(cls), ((), (show_help, (), {'level': h})))
            if p[0].set_runner_func:
                if not func:
                    dflt_func = getattr(cls, 'do_run', None)
                    if not dflt_func:
                        throw(Exc.cannot_determine_function)
                    func = [(), dflt_func]
                params = [
                    (k, v) for k, v in p[1].items() if not k in have_attrs
                ]
                path, func = func
                args = map_args_to_func_sig(func, params, map_from=1)
                return attrcls(cls), (path, (func,) + args)

        if not p[0].allow_unknown_attrs:
            unknown = [k for k in p[1] if not k in have_attrs]
            if unknown:
                throw(Exc.unmatched, unknown=unknown)
    return attrcls(cls), func


def show_help(app, level=None, h=None):
    from .help import render_help

    return render_help(app, level, h)


def inner(app, *pth):
    root = app
    app._root = app
    for p in pth:
        app = getattr(app, p)
    app._root = root
    return app


def get_func(app, pth, func_with_args):
    obj = inner(app, *pth)
    f = func_with_args
    return f[0](obj, *f[1], **f[2])


def root(obj):
    return obj._root


def parent(obj):
    r = root_ = root(obj)
    for p in obj._path[:-1]:
        r = getattr(r, p)
        r._root = root_
    return r


def configure(App, providers, log=None):
    if PY2:
        to_new_style(App)

    set_log(log)
    if not providers:
        n = App.__name__
        providers = (CLI(sys.argv[1:]), Env(n), File(n))
    if not isinstance(providers, (tuple, list)):
        providers = [providers]
    t0 = now()
    App._path = ()
    App, pth_func_with_args = walk_attrs(
        App, [[p, p.cfg(), p.str_only] for p in providers], {}
    )
    pdt(t0)
    if pth_func_with_args:
        pth, func_with_args = pth_func_with_args
        func = partial(get_func, pth=pth, func_with_args=func_with_args)
    else:
        func = None
    pdt(t0)
    return App, func


def run(*a, **kw):
    print('hello')
