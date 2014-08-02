graphite_scripts
================

Miscellaneous scripts to interact with various devices and feed the resulting information into graphite for monitoring/trending purposes.

Settings.cfg should go into the users home folder in their .config/graphite/ directory. Settings are True/False bool's expect serial where its false or a single serial number to query against.

All data is pushed to graphite in a single pickle push to port 2004(default) to reduce the load on the server for metrics added to the environment. The script pulls from both the nest api as well as the provided nest weather api to give both indoor and outdoor temperature, humidity and other information that looks interesting.
