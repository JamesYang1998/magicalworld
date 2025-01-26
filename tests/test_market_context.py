"""Tests for market context functionality."""

import sys
import os
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.market_context import MarketContextManager

def test_market_context_initialization():
    """Test market context manager initialization."""
    manager = MarketContextManager()
    assert manager.context_cache == {}
    assert isinstance(manager.cache_timestamp, datetime)

def test_context_formatting():
    """Test context string formatting."""
    manager = MarketContextManager()
    manager.context_cache = {
        "btc_price": "40000",
        "eth_price": "2500",
        "market_phase": "alt season",
        "recent_events": ["Event 1", "Event 2"]
    }
    
    context_str = manager._format_context()
    assert "BTC=$40000" in context_str
    assert "ETH=$2500" in context_str
    assert "Phase: alt season" in context_str
    assert "Events: Event 1, Event 2" in context_str

def test_cache_refresh_check():
    """Test cache refresh timing logic."""
    manager = MarketContextManager()
    
    # Set cache timestamp to 6 minutes ago
    manager.cache_timestamp = datetime.now() - timedelta(minutes=6)
    assert manager._should_refresh_cache() is True
    
    # Set cache timestamp to 4 minutes ago
    manager.cache_timestamp = datetime.now() - timedelta(minutes=4)
    assert manager._should_refresh_cache() is False

def test_empty_context_handling():
    """Test handling of empty/error context cases."""
    manager = MarketContextManager()
    
    # Test with empty cache
    assert manager._format_context() == ""
    
    # Test with partial data
    manager.context_cache = {"btc_price": "40000"}
    context_str = manager._format_context()
    assert context_str == "BTC=$40000"
