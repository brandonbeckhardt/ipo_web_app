
if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig
from gluon.contrib.heroku import get_db
import os

fake_migrate_val = False
fake_migrate_key = [key for key in os.environ.keys() if key == "fake_migrate"]
if fake_migrate_key:
	print os.environ[fake_migrate_key[0]]
	print type(os.environ[fake_migrate_key[0]])
	if os.environ[fake_migrate_key[0]] == "True":
		print 'yes'
		fake_migrate_val = True

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)
db = get_db(name='DATABASE_URL', pool_size=10, fake_migrate=fake_migrate_val)
