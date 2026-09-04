from pyhive import hive

conn = hive.Connection(host='localhost', port=10000, username='drownedsnake', auth='NOSASL')
cursor = conn.cursor()

# 1. 创建数据库
cursor.execute('CREATE DATABASE IF NOT EXISTS school')
print("✅ 数据库创建成功")

# 2. 使用数据库
cursor.execute('USE school')

# 3. 创建学生表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INT,
        name STRING,
        age INT,
        score DOUBLE
    )
''')
print("✅ 表创建成功")

# 4. 查看表结构
cursor.execute('DESC students')
print("\n📋 表结构:")
for row in cursor.fetchall():
    print(row)

# 5. 查看数据库列表
cursor.execute('SHOW DATABASES')
print("\n📁 数据库列表:", cursor.fetchall())

# 6. 查看表列表
cursor.execute('SHOW TABLES')
print("\n📋 表列表:", cursor.fetchall())

# 7. 删除表（清理）
cursor.execute('DROP TABLE IF EXISTS students')
cursor.execute('DROP DATABASE IF EXISTS school')
print("\n✅ 清理完成")

cursor.close()
conn.close()