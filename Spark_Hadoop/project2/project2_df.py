from pyspark.sql import SparkSession
from pyspark.sql.functions import *


class Project2:
    def run(self, inputPath, outputPath, stopwords, k):
        spark = SparkSession.builder.master("local").appName("project2_df").getOrCreate()
        df = spark.read.text(inputPath)
        df = df.withColumn('split_value', split(col('value'), ',', 2)) \
            .withColumn('year', substring(col('split_value')[0], 1, 4).cast('int')) \
            .withColumn('words', split(col('split_value')[1], ' ')) \
            .select('year', 'words')
        result = df.select(concat_ws('\t', df.year, df.words).alias('output'))
        result.coalesce(1).write.mode('overwrite').text(outputPath)

        yearCount = df.groupBy('year').agg(count('*').alias('year_count'))
        df_words = df.select('year', explode('words').alias('word'))
        word_counts = df_words.groupBy('year', 'word').agg(count('*').alias('count'))
        df_unique_words = df.select('year', array_distinct('words').alias('unique_words'))
        df_occur_lines = df_unique_words.select('year', explode('unique_words').alias('word'))
        occur_lines = df_occur_lines.groupBy('year', 'word').agg(count('*').alias('doc_count'))

        tf = word_counts.withColumn('tf_value', log10(col('count'))) \
                        .select('year', 'word', 'tf_value')

        idf = occur_lines.join(yearCount, on='year') \
                         .withColumn('idf_value', log10(col('year_count') / col('doc_count'))) \
                         .select('year', 'word', 'idf_value')

        weight = tf.join(idf, on=['year', 'word']) \
                   .withColumn('weight', col('tf_value') * col('idf_value')) \
                   .select('year', 'word', 'weight')    \

        avg = weight.groupBy('word').agg({'weight':'avg'}) \
                   .withColumnRenamed('avg(weight)', 'average_weight')

        total_word_counts = word_counts.groupBy('word').agg(sum('count').alias('total_count'))
        freq = total_word_counts.orderBy(desc('total_count'), asc('word')) \
                                .select('word') \
                                .limit(stopwords)
        freq_list = [row['word'] for row in freq.collect()]
        avg_ordered = avg.orderBy(desc('average_weight'), asc('word')) \
                         .limit(k + stopwords)
        avg_filtered = avg_ordered.filter(~col('word').isin(freq_list)) \
                                  .limit(k)
        result = avg_filtered.select(format_string('"%s"\t%f', col('word'), col('average_weight')).alias('output'))
        result.coalesce(1).write.mode('overwrite').text(outputPath)
        spark.stop()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 5:
        print("Wrong arguments")
        sys.exit(-1)
    Project2().run(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
# spark-submit project2_df.py "file:///Users/lyt/9313lab/project2/abcnews.txt" "file:///Users/lyt/9313lab/project2/output" 1 5