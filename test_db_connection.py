from pyhive import hive

conn = hive.Connection(host='localhost', port=10000, username='drownedsnake')
cur = conn.cursor()
cur.execute('SHOW DATABASES')
print('连接成功，数据库列表:', cur.fetchall())
cur.close()
conn.close()
