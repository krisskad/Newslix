def vacuum_db():
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("VACUUM")
    connection.close()