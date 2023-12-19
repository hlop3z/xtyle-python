
# sass
try:
    import sass
    sass_available = True
except ImportError:
    sass = None
    sass_available = False

# MiniRacer
try:
    from py_mini_racer import MiniRacer
    mini_racer_available = True
except ImportError:
    MiniRacer = None
    mini_racer_available = False


# Request
try:
    import requests
    requests_available = True
except ImportError:
    requests = None
    requests_available = False

# SQLow
try:
    from sqlow import sqlow
    sqlow_available = True
except ImportError:
    sqlow = None
    sqlow_available = False

