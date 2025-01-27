import os
os.environ['PYSPARK_PYTHON'] = '/usr/bin/python3.9'
os.environ['PYSPARK_DRIVER_PYTHON'] = '/usr/bin/python3.9'
from pyspark import SparkContext

# 1. 创建 SparkContext
sc = SparkContext("local", "Simple MapReduce Example")
# 2. 读取数据
lines = sc.textFile("./input/pg100.txt")  # 替换为实际文件路径
# 3. 执行 Map 操作
words = lines.flatMap(lambda line: line.split())
# 4. 映射每个单词为 (word, 1)
word_pairs = words.map(lambda word: (word, 1))
# 5. 执行 Reduce 操作（聚合）
word_counts = word_pairs.reduceByKey(lambda a, b: a + b)
# 6. 收集并显示结果
for word, count in word_counts.collect():
    print(f"{word}: {count}")
# 7. 停止 SparkContext
sc.stop()
