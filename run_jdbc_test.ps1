param([string]$Host_ = "localhost")
$cp = ".;C:\Users\drownedsnake\AppData\Roaming\JetBrains\PyCharm2025.3\jdbc-drivers\Hive\3.1.3\hive-jdbc-3.1.3-standalone.jar"
Set-Location "C:\Users\drownedsnake\PycharmProjects\PythonProject1"
& java -cp $cp TestHiveJdbc $Host_
