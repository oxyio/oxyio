# oxy.io

A stack & framework for building control panels. Built on:

+ Python/Gevent/uWSGI
+ MariaDB/Galera
+ Redis
+ Elasticsearch

Provides:

+ Object config autogenerates views/forms
+ Long/short tasks, with events
+ Websockets hooked up to events
+ Stackless servers & workers
+ Modular separation for objects/tasks/websockets/etc
