"""Runs one script and saves any matplotlib figures as PNGs for the Bench output panel."""
import os
import runpy
import sys

target, fig_dir = sys.argv[1], sys.argv[2]
sys.argv = [target]
sys.path.insert(0, os.getcwd())

_saved = [0]


def _save_figures():
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return
    for num in plt.get_fignums():
        fig = plt.figure(num)
        _saved[0] += 1
        fig.savefig(os.path.join(fig_dir, f"fig_{_saved[0]:03d}.png"), dpi=110, bbox_inches="tight")
    plt.close("all")


try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.show = lambda *a, **k: _save_figures()
except ImportError:
    pass

try:
    runpy.run_path(target, run_name="__main__")
except SystemExit:
    raise
except BaseException:
    import traceback

    etype, err, tb = sys.exc_info()
    user_tb = tb
    while user_tb is not None and user_tb.tb_frame.f_code.co_filename != target:
        user_tb = user_tb.tb_next
    traceback.print_exception(etype, err, user_tb or tb)
    sys.exit(1)
finally:
    _save_figures()
