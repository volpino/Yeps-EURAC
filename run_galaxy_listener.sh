#!/bin/sh

cd `dirname $0`
python scripts/galaxy_messaging/server/amqp_consumer.py universe_wsgi.ini >> galaxy_listener.log 2>&1