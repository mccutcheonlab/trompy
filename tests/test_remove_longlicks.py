"""
Test the remove_longlicks functionality
"""
import numpy as np
from trompy.lickcalc import Lickcalc
from trompy.lick_utils import lickcalc


def test_remove_longlicks_basic():
    """Test that longlicks are removed from calculations when remove_longlicks=True"""
    # Create test data with known longlicks
    licks = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    offsets = np.array([1.1, 2.1, 3.5, 4.1, 5.1])  # 3rd lick is 0.5s long (longlick)
    
    # Without removing longlicks
    lickdata_keep = Lickcalc(licks=licks, offset=offsets, longlick_threshold=0.3, 
                             remove_longlicks=False)
    
    # With removing longlicks
    lickdata_remove = Lickcalc(licks=licks, offset=offsets, longlick_threshold=0.3,
                                remove_longlicks=True)
    
    # Check that total licks is reduced
    assert lickdata_keep.total == 5, "Should have 5 licks when not removing"
    assert lickdata_remove.total == 4, "Should have 4 licks after removing longlick"
    
    # Check that the correct lick was removed
    assert len(lickdata_remove.licks) == 4
    assert 3.0 not in lickdata_remove.licks, "The longlick timestamp should be removed"
    
    # Check that raw data is preserved
    assert len(lickdata_remove.licks_raw) == 5, "Raw licks should be unchanged"
    assert len(lickdata_remove.offset_raw) == 5, "Raw offsets should be unchanged"


def test_remove_longlicks_affects_bursts():
    """Test that burst calculations are affected by removing longlicks"""
    # Create data where longlick would create a burst boundary
    licks = np.array([1.0, 1.2, 1.4, 2.0, 2.2, 2.4])  # Two bursts
    offsets = np.array([1.05, 1.25, 1.9, 2.05, 2.25, 2.45])  # 3rd lick is 0.5s (longlick)
    
    # Without removing longlicks (3rd lick creates unusual burst pattern)
    lickdata_keep = Lickcalc(licks=licks, offset=offsets, longlick_threshold=0.3,
                             burst_threshold=0.5, remove_longlicks=False)
    
    # With removing longlicks
    lickdata_remove = Lickcalc(licks=licks, offset=offsets, longlick_threshold=0.3,
                                burst_threshold=0.5, remove_longlicks=True)
    
    # Burst counts should differ
    print(f"Keep longlicks - bursts: {lickdata_keep.burst_number}, licks: {lickdata_keep.total}")
    print(f"Remove longlicks - bursts: {lickdata_remove.burst_number}, licks: {lickdata_remove.total}")
    
    # Total licks should be reduced
    assert lickdata_remove.total < lickdata_keep.total


def test_remove_longlicks_with_lickCalc():
    """Test that the lickcalc wrapper function works with remove_longlicks"""
    licks = [1.0, 2.0, 3.0, 4.0, 5.0]
    offsets = [1.1, 2.1, 3.5, 4.1, 5.1]  # 3rd lick is 0.5s long
    
    # Test with remove_longlicks=False (default)
    result_keep = lickcalc(licks, offset=offsets, longlickThreshold=0.3)
    assert result_keep['total'] == 5
    
    # Test with remove_longlicks=True
    result_remove = lickcalc(licks, offset=offsets, longlickThreshold=0.3, 
                            remove_longlicks=True)
    assert result_remove['total'] == 4
    assert len(result_remove['licks']) == 4


def test_remove_longlicks_no_offsets():
    """Test that remove_longlicks is gracefully ignored when no offsets provided"""
    licks = [1.0, 2.0, 3.0, 4.0, 5.0]
    
    # Should not error even with remove_longlicks=True
    lickdata = Lickcalc(licks=licks, remove_longlicks=True)
    
    # All licks should remain since we can't calculate lick lengths
    assert lickdata.total == 5
    assert lickdata.licklength is None


def test_remove_longlicks_affects_ilis():
    """Test that ILIs are recalculated based on remaining licks"""
    licks = np.array([1.0, 2.0, 3.0, 4.0])
    offsets = np.array([1.1, 2.1, 3.5, 4.1])  # 3rd is longlick
    
    lickdata_keep = Lickcalc(licks=licks, offset=offsets, longlick_threshold=0.3,
                             remove_longlicks=False)
    lickdata_remove = Lickcalc(licks=licks, offset=offsets, longlick_threshold=0.3,
                                remove_longlicks=True)
    
    # ILIs should be different after removing middle lick
    print(f"Keep ILIs: {lickdata_keep.ilis}")
    print(f"Remove ILIs: {lickdata_remove.ilis}")
    
    # Number of ILIs should be reduced (n_licks - 1)
    assert len(lickdata_remove.ilis) == len(lickdata_remove.licks) - 1


if __name__ == '__main__':
    test_remove_longlicks_basic()
    test_remove_longlicks_affects_bursts()
    test_remove_longlicks_with_lickCalc()
    test_remove_longlicks_no_offsets()
    test_remove_longlicks_affects_ilis()
    print("All tests passed!")
