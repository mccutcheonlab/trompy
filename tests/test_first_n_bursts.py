"""
Tests for only_return_first_n_bursts parameter in Lickcalc and lickCalc
"""
import numpy as np
import pytest
from trompy.lickcalc import Lickcalc
from trompy.lick_utils import lickcalc


def test_first_n_bursts_basic():
    """Test that only_return_first_n_bursts correctly limits burst analysis to first N bursts"""
    # Create lick train with 5 clear bursts (0.3s ILIs within bursts, 1s ILIs between bursts)
    licks = [1.0, 1.3, 1.6, 1.9,  # Burst 1: 4 licks
             3.0, 3.3, 3.6,  # Burst 2: 3 licks
             5.0, 5.3,  # Burst 3: 2 licks
             7.0, 7.3, 7.6, 7.9, 8.2,  # Burst 4: 5 licks
             10.0, 10.3, 10.6]  # Burst 5: 3 licks
    
    # Calculate with all bursts
    all_bursts = Lickcalc(licks=licks, burst_threshold=0.5)
    assert all_bursts.burst_number == 5
    assert len(all_bursts.burst_licks) == 5
    
    # Calculate with only first 3 bursts
    first_3 = Lickcalc(licks=licks, burst_threshold=0.5, only_return_first_n_bursts=3)
    assert first_3.burst_number == 3
    assert len(first_3.burst_licks) == 3
    assert first_3.burst_licks == [4, 3, 2]  # Should be first 3 bursts only
    

def test_first_n_bursts_more_than_exist():
    """Test that requesting more bursts than exist returns all bursts without error"""
    # Create lick train with only 3 bursts
    licks = [1.0, 1.3, 1.6,  # Burst 1: 3 licks
             3.0, 3.3,  # Burst 2: 2 licks
             5.0, 5.3, 5.6, 5.9]  # Burst 3: 4 licks
    
    # Request 10 bursts when only 3 exist - should return all 3
    result = Lickcalc(licks=licks, burst_threshold=0.5, only_return_first_n_bursts=10)
    assert result.burst_number == 3
    assert result.burst_licks == [3, 2, 4]
    

def test_first_n_bursts_zero_or_negative():
    """Test that N=0 or negative N doesn't break anything"""
    licks = [1.0, 1.3, 1.6,
             3.0, 3.3,
             5.0, 5.3, 5.6]
    
    # N=0 should do nothing (return all bursts)
    result_zero = Lickcalc(licks=licks, burst_threshold=0.5, only_return_first_n_bursts=0)
    assert result_zero.burst_number == 3  # Should have all bursts still
    

def test_first_n_bursts_statistics():
    """Test that burst statistics reflect only the first N bursts"""
    # Create lick train where burst 1-2 have different properties than burst 3-4
    licks = [1.0, 1.2, 1.4, 1.6, 1.8,  # Burst 1: 5 licks
             3.0, 3.2, 3.4, 3.6, 3.8,  # Burst 2: 5 licks
             5.0, 5.2,  # Burst 3: 2 licks
             7.0, 7.2]  # Burst 4: 2 licks
    
    all_bursts = Lickcalc(licks=licks, burst_threshold=0.5)
    first_2 = Lickcalc(licks=licks, burst_threshold=0.5, only_return_first_n_bursts=2)
    
    # Burst mean should differ
    assert all_bursts.burst_mean == 3.5  # (5+5+2+2)/4
    assert first_2.burst_mean == 5.0  # (5+5)/2
    
    # Number of bursts should differ
    assert all_bursts.burst_number == 4
    assert first_2.burst_number == 2
    

def test_first_n_bursts_with_lickCalc():
    """Test that only_return_first_n_bursts works with lickcalc wrapper function"""
    licks = [1.0, 1.3, 1.6,  # Burst 1
             3.0, 3.3, 3.6, 3.9,  # Burst 2
             5.0, 5.3,  # Burst 3
             7.0, 7.3, 7.6]  # Burst 4
    
    # Using lickcalc wrapper
    result = lickcalc(licks, burstThreshold=0.5, only_return_first_n_bursts=2)
    
    assert result['bNum'] == 2
    assert len(result['bLicks']) == 2
    assert result['bLicks'] == [3, 4]  # First 2 bursts only
    

def test_first_n_bursts_interaction_with_minburstlength():
    """Test that only_return_first_n_bursts works correctly with min_burst_length filtering"""
    # Create data with some short bursts that will be filtered
    licks = [1.0, 1.3,  # Burst 1: 2 licks (will be filtered if min=3)
             3.0, 3.3, 3.6, 3.9,  # Burst 2: 4 licks
             5.0, 5.3, 5.6,  # Burst 3: 3 licks
             7.0, 7.3, 7.6, 7.9, 8.2,  # Burst 4: 5 licks
             10.0, 10.3]  # Burst 5: 2 licks (will be filtered if min=3)
    
    # With min_burst_length=3, should have 3 bursts (bursts 2, 3, 4)
    # Then only_return_first_n_bursts=2 should return first 2 of those (bursts 2 and 3)
    result = Lickcalc(licks=licks, burst_threshold=0.5, 
                      min_burst_length=3, only_return_first_n_bursts=2)
    
    assert result.burst_number == 2
    assert result.burst_licks == [4, 3]  # First 2 bursts after short burst removal
    

def test_first_n_bursts_interaction_with_remove_longlicks():
    """Test that only_return_first_n_bursts works correctly with remove_longlicks"""
    licks = [1.0, 1.3, 1.6,  # Burst 1
             3.0, 3.3, 3.6,  # Burst 2
             5.0, 5.3, 5.6]  # Burst 3
    offsets = [1.1, 1.4, 1.7,  # Normal durations (0.1, 0.1, 0.1)
               3.1, 3.5, 3.7,  # One longlick (0.2s, 0.1s)
               5.1, 5.4, 5.7]
    
    # With remove_longlicks=True (threshold=0.15), burst 2 should have one longlick removed
    result_with_removal = Lickcalc(licks=licks, offset=offsets, burst_threshold=0.5,
                                   remove_longlicks=True, longlick_threshold=0.15,
                                   only_return_first_n_bursts=2)
    
    result_without_removal = Lickcalc(licks=licks, offset=offsets, burst_threshold=0.5,
                                      remove_longlicks=False,
                                      only_return_first_n_bursts=2)
    
    # Should get first 2 bursts in both cases
    assert result_with_removal.burst_number == 2
    assert result_without_removal.burst_number == 2
    
    # With longlick removal, should have fewer total licks
    assert result_with_removal.total < result_without_removal.total


def test_first_n_bursts_false_default():
    """Test that default value (False) doesn't filter any bursts"""
    licks = [1.0, 1.3, 1.6,
             3.0, 3.3, 3.6,
             5.0, 5.3, 5.6]
    
    # Default should be False and should not filter
    default_result = Lickcalc(licks=licks, burst_threshold=0.5)
    explicit_false = Lickcalc(licks=licks, burst_threshold=0.5, only_return_first_n_bursts=False)
    
    assert default_result.burst_number == explicit_false.burst_number == 3
    assert default_result.burst_licks == explicit_false.burst_licks


def test_lickCalc_deprecated_warning():
    """Test that the deprecated lickCalc (uppercase C) produces a deprecation warning"""
    import warnings
    from trompy.lick_utils import lickCalc
    
    licks = [1.0, 1.3, 1.6, 3.0, 3.3]
    
    # Should produce a DeprecationWarning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = lickCalc(licks, burstThreshold=0.5)
        
        # Check that a warning was raised
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "lickCalc is deprecated" in str(w[0].message)
        assert "lickcalc" in str(w[0].message)
    
    # But should still return correct results
    assert result['total'] == 5
