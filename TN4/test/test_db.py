import sqlite3

try:
    sqliteConnection = sqlite3.connect('gf_iot.db')
    cursor = sqliteConnection.cursor()
    print("Successfully Connected to SQLite")

    sqlite_insert_query = """INSERT INTO uv
                          (farm_name,iot_signal,reset,statusuv_1,statusuv_2,cb_cua1,cb_cua2) 
                           VALUES 
                          ('GF_TN2', 1, 0, 0, 0, 0, 0)"""

    count = cursor.execute(sqlite_insert_query)
    sqliteConnection.commit()
    print("Record inserted successfully into SqliteDb_developers table ", cursor.rowcount)
    cursor.close()

except sqlite3.Error as error:
    print("Failed to insert data into sqlite table", error)
finally:
    if sqliteConnection:
        sqliteConnection.close()
        print("The SQLite connection is closed")