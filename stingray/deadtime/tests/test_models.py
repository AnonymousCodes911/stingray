import os
import pytest
import numpy as np
from scipy.interpolate import interp1d

from stingray.lightcurve import Lightcurve
from stingray.powerspectrum import AveragedPowerspectrum
from stingray.deadtime.model import r_det, r_in, pds_model_zhang
from stingray.deadtime.model import check_A, check_B, heaviside, A, B
from stingray.filters import filter_for_deadtime


pytestmark = pytest.mark.slow


def test_heaviside():
    assert heaviside(2) == 1
    assert heaviside(0) == 1
    assert heaviside(-1) == 0


def simulate_events(rate, length, deadtime=2.5e-3, **filter_kwargs):
    events = np.random.uniform(0, length, int(rate * length))
    events = np.sort(events)
    events_dt = filter_for_deadtime(events, deadtime, **filter_kwargs)
    return events, events_dt


def test_deadtime_conversion():
    """Test the functions for count rate conversion."""
    original_rate = np.arange(1, 1000, 10)
    deadtime = 2.5e-3
    rdet = r_det(deadtime, original_rate)
    rin = r_in(deadtime, rdet)
    np.testing.assert_almost_equal(rin, original_rate)


@pytest.mark.parametrize("rate", [1.0, 1000.0])
def test_zhang_model_accurate(rate):
    bintime = 0.0002
    deadtime = 2.5e-3
    length = 2000
    fftlen = 10

    _, events_dt = simulate_events(rate, length, deadtime=deadtime)
    lc_dt = Lightcurve.make_lightcurve(events_dt, bintime, tstart=0, tseg=length)
    pds = AveragedPowerspectrum(lc_dt, fftlen, norm="leahy")

    zh_f, zh_p = pds_model_zhang(1000, rate, deadtime, bintime, limit_k=600)

    deadtime_fun = interp1d(zh_f, zh_p, bounds_error=False, fill_value="extrapolate")
    ratio = pds.power / deadtime_fun(pds.freq)
    assert np.isclose(np.mean(ratio), 1, rtol=0.01)
    assert np.isclose(np.std(ratio), 1 / np.sqrt(pds.m), rtol=0.1)


def test_checkA():
    check_A(300, 2.5e-3, 0.001, max_k=100, save_to="check_A.png")
    assert os.path.exists("check_A.png")
    os.unlink("check_A.png")


def test_checkB():
    check_B(300, 2.5e-3, 0.001, max_k=100, save_to="check_B.png")
    assert os.path.exists("check_B.png")
    os.unlink("check_B.png")


@pytest.mark.parametrize("rate", [0.1, 1000.0])
@pytest.mark.parametrize("tb", [0.0001, 0.1])
def test_A_and_B_array(rate, tb):
    td = 2.5e-3
    ks = np.array([1, 5, 20, 60])
    tau = 1 / rate
    r0 = r_det(td, rate)
    assert np.array_equal(np.array([A(k, r0, td, tb, tau) for k in ks]), A(ks, r0, td, tb, tau))
    assert np.array_equal(np.array([B(k, r0, td, tb, tau) for k in ks]), B(ks, r0, td, tb, tau))


def test_pds_model_warns():
    with pytest.warns(UserWarning, match="The bin time is much larger than the "):
        pds_model_zhang(10, 100.0, 2.5e-3, 1, limit_k=10)
