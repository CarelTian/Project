from pyspark import SparkContext, SparkConf

# 设置 Spark 配置
conf = SparkConf().setAppName("SimpleApp").setMaster("local")
sc = SparkContext(conf=conf)


# 读取文件并缓存
logData = sc.textFile("file:///Users/lyt/9313lab/week7/README.md", 2).cache()

# 统计包含 'a' 和 'b' 的行数
numAs = logData.filter(lambda line: "a" in line).count()
numBs = logData.filter(lambda line: "b" in line).count()

# 输出结果
print(f"Lines with a: {numAs}, Lines with b: {numBs}")

# 关闭 SparkContext
sc.stop()
