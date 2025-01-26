"""Market context manager for enhancing GPT responses with current market awareness."""

import os
from datetime import datetime, timedelta
import logging
from typing import Dict, Optional

from src.logger import setup_logger

logger = setup_logger('market_context')

class MarketContextManager:
    """Manages market context for enhancing GPT responses."""
    
    def __init__(self):
        """Initialize the market context manager."""
        self.context_cache: Dict[str, any] = {}
        self.cache_timestamp = datetime.now()
        self.cache_ttl = timedelta(minutes=5)  # Refresh context every 5 minutes
    
    def get_context(self) -> str:
        """
        Get current market context as a concise string.
        Returns a formatted string with relevant market information.
        """
        try:
            if self._should_refresh_cache():
                self._refresh_context()
            
            # Format context into a concise string
            context_str = self._format_context()
            return context_str
            
        except Exception as e:
            logger.error(f"Error getting market context: {e}", exc_info=True)
            return ""  # Return empty string on error to not block response generation
    
    def _should_refresh_cache(self) -> bool:
        """Check if cache needs refreshing based on TTL."""
        return datetime.now() - self.cache_timestamp > self.cache_ttl
    
    def _refresh_context(self):
        """Refresh market context data."""
        try:
            # TODO: Implement API calls to fetch:
            # - BTC/ETH prices and 24h change
            # - Current market phase (e.g., "alt season", "DeFi summer")
            # - Recent significant events
            # For now, using mock data
            self.context_cache = {
                "btc_price": "40000",
                "eth_price": "2500",
                "market_phase": "alt season",
                "recent_events": ["BTC ETF approval", "Layer 2 momentum"]
            }
            self.cache_timestamp = datetime.now()
            
        except Exception as e:
            logger.error(f"Error refreshing market context: {e}", exc_info=True)
            self.context_cache = {}  # Reset cache on error
    
    def _format_context(self) -> str:
        """Format cached context data into a concise string."""
        if not self.context_cache:
            return ""
            
        try:
            context_parts = []
            
            if "btc_price" in self.context_cache:
                context_parts.append(f"BTC=${self.context_cache['btc_price']}")
            
            if "eth_price" in self.context_cache:
                context_parts.append(f"ETH=${self.context_cache['eth_price']}")
            
            if "market_phase" in self.context_cache:
                context_parts.append(f"Phase: {self.context_cache['market_phase']}")
            
            if "recent_events" in self.context_cache:
                events = ", ".join(self.context_cache["recent_events"][:2])  # Limit to 2 events
                context_parts.append(f"Events: {events}")
            
            return " | ".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error formatting context: {e}", exc_info=True)
            return ""

# Singleton instance for global use
market_context = MarketContextManager()
