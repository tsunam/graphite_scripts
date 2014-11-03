Graphite Nest
================

Settings.cfg should go into the users home folder in their .config/graphite/ directory. Settings are True/False bool's expect serial where its false or a single serial number to query against.

All data is pushed to graphite in a single pickle push to port 2004(default) to reduce the load on the server for metrics added to the environment. The script pulls from both the nest api as well as the provided nest weather api to give both indoor and outdoor temperature, humidity and other information that looks interesting.

![time_to_temp](https://cloud.githubusercontent.com/assets/6295724/4877809/9c55e3a8-62f7-11e4-8bd6-7db4be9cba66.png)
![battery](https://cloud.githubusercontent.com/assets/6295724/4877808/9c5556ae-62f7-11e4-99c4-606bb07090b8.png)
![learning](https://cloud.githubusercontent.com/assets/6295724/4877807/9c54969c-62f7-11e4-8d4a-6b454be41d29.png)
![temperature](https://cloud.githubusercontent.com/assets/6295724/4877806/9c516594-62f7-11e4-85c6-936d5a7291e6.png)

