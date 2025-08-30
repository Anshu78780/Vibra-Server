from ytmusicapi import YTMusic
import inspect
import json

# Initialize YTMusic
ytmusic = YTMusic()

# Get all public methods
methods = [method for method in dir(ytmusic) if callable(getattr(ytmusic, method)) and not method.startswith('_')]

print("Available public methods in YTMusic:")
for method in methods:
    try:
        # Get signature
        signature = str(inspect.signature(getattr(ytmusic, method)))
        print(f"- {method}{signature}")
    except ValueError:
        print(f"- {method} (signature unavailable)")

# Check if get_charts method exists
if 'get_charts' in methods:
    print("\nTrying get_charts method...")
    try:
        # Get charts for India (IN)
        charts = ytmusic.get_charts(country='IN')
        print(json.dumps(charts, indent=2)[:500] + "...")
    except Exception as e:
        print(f"Error with get_charts: {e}")
