#! /bin/sh

# sudo sysctl -w net.inet.udp.maxdgram=65535
mv logs/* celery-logs
python manage.py collectstatic --noinput
python manage.py migrate
nohup python manage.py celery worker -l INFO -f /usr/src/service-bus/celery-logs/worker.log > /dev/null 2>&1 &
nohup python manage.py celery beat -l INFO -f /usr/src/service-bus/celery-logs/beat.log > /dev/null 2>&1 &
uwsgi --ini /usr/src/service-bus/uwsgi.ini --processes $UWSGI_PROCESSES --threads $UWSGI_THREADS -w wsgi.wsgi:application > /dev/null 2>&1
