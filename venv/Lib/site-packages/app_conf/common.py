from __future__ import absolute_import, print_function, unicode_literals
import sys, time

nil = '\x01'  # marker
PY2 = sys.version_info[0] < 3

# just for debug console output:
def get_add(ctx):
    ctx['pos'] += 1
    return ctx['pos']


pdt = lambda t0, ctx={'pos': 0}, *a: print(get_add(ctx), now() - t0, a)
now = lambda: time.time()
is_str = lambda s: isinstance(s, basestring if PY2 else str)

t0 = now()
if PY2:
    pass
import pdb

breakpoint = pdb.set_trace

pdt(t0)


def add_dt(_, __, ev, ts=time.time()):
    dt = time.time() - ts
    ev['timestamp'] = '{:014.8f}'.format(dt)
    return ev


class plain_logger:
    @classmethod
    def log(cls, msg, *a, **kw):
        try:
            txt = ' '.join(
                (
                    msg,
                    ' '.join([str(i).strip() for i in a]),
                    ' '.join(['%s=%s' % (k, v) for k, v in kw.items()]),
                )
            )
        except:
            breakpoint()

        sys.stderr.write(txt + '\n')

    info = debug = error = warn = log


def logger():
    return cfg['logger']


# fmt: off
info  = lambda *a, **kw: logger().info(*a, **kw)
debug = lambda *a, **kw: logger().debug(*a, **kw)
error = lambda *a, **kw: logger().error(*a, **kw)
warn  = lambda *a, **kw: logger().warn(*a, **kw)
# fmt: on


cfg = {'logger': plain_logger}


def set_log(log=None):
    if log is not None:
        cfg['logger'] = log
    else:
        cfg['logger'] = get_structlogger()
    return cfg['logger']


def get_structlogger():
    import structlog as sl

    log = sl.wrap_logger(
        sl.PrintLogger(file=sys.stderr),
        processors=[add_dt, sl.stdlib.add_log_level, sl.dev.ConsoleRenderer()],
        context_class=dict,
    ).bind()
    return log


# -------------------------------------------------------------- Error Handling
class Exc:
    # fmt: off
    cannot_cast                    = 'Cannot cast'
    cannot_cast_to_dict            = 'Cannot cast to dict'
    unmatched                      = 'Unmatched'
    non_unique                     = 'Non unique'
    file_not_found                 = 'File not found'
    cannot_determine_function      = 'Cannot determine function to run'
    cannot_build_unique_short_form = 'Cannot build unique short form'
    not_a_switch                   = 'Not a known switch'
    require_value                  = 'Value required'
    req_dict_to_setup_class        = 'Require dict to setup class'
    double_func_call               = 'TWO functions on CLI disallowed'
    # fmt: on


def throw(msg, *a, **kw):
    if a:
        kw['args'] = a
    error(msg, **kw)
    raise Exception(msg, kw)
