start ./ven/Scripts/activate
celery -A web_scan_task worker -l info -P eventlet -c 20
celery -A host_scan_task worker -l info -P eventlet -c 20