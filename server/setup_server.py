import subprocess
import pymysql as mysql

# it takes 3 required parameters 'host', 'user', 'passwd'
db = mysql.connect(
    host="la_acs_mysql_container",  # "localhost",
    user="root",
    passwd="root"
)
if(db):
    cursor = db.cursor()

    try:
        status_code = cursor.execute("USE LA_ACS_dev;")
        print("created database used..")
        # subprocess.call(["python", "manage.py", "migrate", "--fake", "appserver", "0006"])
        subprocess.call(["python", "manage.py", "makemigrations"])
        subprocess.call(["python", "manage.py", "migrate"])

    except mysql.err.InternalError as e:
        code, msg = e.args
        # unknown database error code
        if code == 1049:
            cursor.execute("CREATE DATABASE IF NOT EXISTS LA_ACS_dev;")
            print("new database created..")

            # works only when this is run from inside server directory
            # creates super user if sqlite database is not found
            subprocess.call(["python", "manage.py", "makemigrations"])
            subprocess.call(["python", "manage.py", "migrate"])
            subprocess.call(["python", "manage.py", "createsuperuser2",
                             "--username", "admin",
                             "--password", "adminadmin",
                             "--noinput",
                             "--email", "p.shanthakumar@spi-global.com"
                             ])
