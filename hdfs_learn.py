from hdfs import InsecureClient

client = InsecureClient('http://localhost:9870', user='drownedsnake')

# 1. 创建目录
client.makedirs('/user/drownedsnake/data')
print("✅ 我的目录创建成功")

# 2. 上传文件
with open('sample.csv', 'w', encoding='utf-8') as f:
    f.write("id,name,age\n1,张三,20\n2,李四,21\n3,王五,22\n")
client.upload('/user/drownedsnake/data/sample.csv', 'sample.csv', overwrite=True)
print("✅ 我的文件上传成功")

# 3. 查看文件列表
print("\n📁 HDFS 文件列表:")
print(client.list('/user/drownedsnake/data'))

# 4. 下载文件
client.download('/user/drownedsnake/data/sample.csv', 'downloaded.csv', overwrite=True)
print("✅ 我的文件下载成功")

# 5. 读取文件内容
with client.read('/user/drownedsnake/data/sample.csv', encoding='utf-8') as reader:
    print("\n📄 文件内容:")
    print(reader.read())

# 6. 删除文件
client.delete('/user/drownedsnake/data/sample.csv')
print("✅ 我的文件删除成功")
