from pyspark import SparkContext, SparkConf
from pyspark.sql.session import SparkSession
import sys
import math

class Project2:
    def run(self, inputPath, outputPath, stopwords, k):
        spark = SparkSession.builder.master("local").appName("project2_rdd").getOrCreate()
        sc = spark.sparkContext
        # Read input file and parse lines
        lines = sc.textFile(inputPath)
        parsed = lines.map(lambda line: self.parse_line(line))
        # RDD(year,[word1,word2...])
        yearCount = parsed.map(lambda x:(x[0],1)).reduceByKey(lambda a,b:a+b)
        word_counts = parsed.flatMap(lambda x: [((x[0], word), 1) for word in x[1]])   \
                    .reduceByKey(lambda a, b: a + b)
        # RDD((year,word),value)
        occur_lines=parsed.flatMap(lambda x: [((x[0], word), 1) for word in set(x[1])]) \
                    .reduceByKey(lambda a,b:a+b)
        # RDD((year,word),value)
        tf=word_counts.map(lambda x:(x[0][0],x[0][1],math.log10(x[1])))
        # RDD(year,word,tf)
        idf = occur_lines.map(lambda x: (x[0][0], (x[0][1], x[1]))).join(yearCount)     \
            .map(lambda x: (x[0], x[1][0][0], math.log10(x[1][1]/x[1][0][1])))
        # RDD(year,word,idf)
        weight= tf.map(lambda x: ((x[0],x[1]), x[2]))   \
                .join(idf.map(lambda x:((x[0],x[1]), x[2])))    \
                .map(lambda x:(x[0][0],x[0][1],x[1][0]*x[1][1]))
        # RDD(year, word, weight)
        avg=weight.map(lambda x:(x[1],(x[2],1)))    \
            .reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1]))   \
            .map(lambda x: (x[0], x[1][0] / x[1][1]))
        # RDD(word,weight)
        freq=word_counts.map(lambda x:(x[0][1],x[1])) \
            .reduceByKey(lambda a,b:a+b)          \
            .sortBy(lambda x:(-x[1],x[0]))  \
            .map(lambda x: (x[0]))  \
            .take(stopwords)
    # RDD(word)
        result = avg.sortBy(lambda x: (-x[1], x[0]))   \
                .take(k+stopwords)
        result=[x for x in result if x[0] not in freq]
        result=result[:k]
        result=sc.parallelize(result)
        result= result.map(lambda x: f'"{x[0]}"\t{x[1]}')
        result=result.coalesce(1)
        result.saveAsTextFile(outputPath)
        spark.stop()

    def parse_line(self, line):
        date, headline = line.split(',', 1)
        year = int(date[:4])
        words = headline.split()
        return (year, words)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Wrong arguments")
        sys.exit(-1)
    Project2().run(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))

# spark-submit project2_rdd.py "file:///Users/lyt/9313lab/project2/abcnews.txt" "file:///Users/lyt/9313lab/project2/output" 1 5
