import os
import types
import numpy as np
import matplotlib


def pytest_configure(config):
    # Force a non-interactive backend for matplotlib for tests
    os.environ.setdefault('MPLBACKEND', 'Agg')
    matplotlib.use(os.environ['MPLBACKEND'])


import pytest


@pytest.fixture(autouse=True)
def isolate_rng_and_close_figs():
    """Fixture to isolate numpy RNG state and ensure figures are closed after each test.

    This reduces flaky interactions between tests that rely on randomness or
    create matplotlib figures.
    """
    # Save RNG state
    state = np.random.get_state()
    try:
        yield
    finally:
        # restore RNG state and close any open figures
        np.random.set_state(state)
        try:
            import matplotlib.pyplot as plt

            plt.close('all')
        except Exception:
            pass


@pytest.fixture(scope='session', autouse=True)
def audioop_shim():
    """Provide a minimal `audioop` module in sys.modules for tests that import it.

    This is a test-only shim; it is not intended as a full replacement for the
    real C-extension module. It provides a minimal `add` function so tests can
    import `from audioop import add` without requiring the system extension.
    """
    import sys

    created = False
    if 'audioop' not in sys.modules:
        mod = types.ModuleType('audioop')

        def add(a, b, width):
            try:
                import numpy as _np

                return _np.add(a, b)
            except Exception:
                return [x + y for x, y in zip(a, b)]

        mod.add = add
        sys.modules['audioop'] = mod
        created = True

    try:
        yield
    finally:
        if created:
            try:
                del sys.modules['audioop']
            except Exception:
                pass
