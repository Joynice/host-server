#!D:\events\host-server\ven\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'celery==3.1.10','console_scripts','celerybeat'
__requires__ = 'celery==3.1.10'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('celery==3.1.10', 'console_scripts', 'celerybeat')()
    )
