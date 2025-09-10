"""Cache setup module for managing disk-based caching and background callbacks"""

import diskcache
from dash import DiskcacheManager

# Initialize disk-based cache for temporary data storage
cache = diskcache.Cache("./.cache")

# Background callback manager for long-running operations
background_callback_manager = DiskcacheManager(cache)
