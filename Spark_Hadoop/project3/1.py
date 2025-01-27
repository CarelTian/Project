from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split, udf, collect_list
from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StringType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Filtered Jaccard Similarity Join") \
    .getOrCreate()

# Sample input data
data = [
    "13660#(-43.098726,-42.966175)#roman quaedvlieg sacked australian border force job",
    "13661#(-77.554255,34.542368)#cambodian shooting range",
    "13662#(38.734736,-22.431879)#rural women stories hardship survival",
    "13663#(41.390992,-61.055212)#hundreds gather protest human rights abuses southeast asia",
    "13664#(-87.131193,-24.957161)#egypt presidential elections sisi geared victory",
    "13665#(89.601003,73.941375)#bbys day court",
    "13666#(32.713019,81.290379)#stem cells eye lenses babies cataracts",
    "13667#(-92.590241,34.511494)#giant pumpkin bumblebe"
]

# Create DataFrame
df = spark.createDataFrame([(i,) for i in data], ["raw"])
df = df.withColumn("index", split(col("raw"), "#").getItem(0)) \
       .withColumn("coordinates", split(col("raw"), "#").getItem(1)) \
       .withColumn("terms", split(split(col("raw"), "#").getItem(2), " ")) \
       .select("index", "coordinates", "terms")

# Tokenization and calculating token frequencies for prefix filtering
df_tokens = df.withColumn("token", explode(col("terms"))) \
              .groupBy("token") \
              .count() \
              .orderBy("count")

# Collect token frequency for prefix ordering
token_order = {row['token']: i for i, row in enumerate(df_tokens.collect())}
broadcast_order = spark.sparkContext.broadcast(token_order)

# UDF to sort tokens by frequency
def sort_by_frequency(terms):
    return sorted(terms, key=lambda x: broadcast_order.value.get(x, float('inf')))

sort_udf = udf(sort_by_frequency, ArrayType(StringType()))
df = df.withColumn("sorted_terms", sort_udf(col("terms")))

# UDF to extract prefix
def get_prefix(terms, threshold=0.5):
    prefix_length = max(1, int(len(terms) * threshold))
    return terms[:prefix_length]

prefix_udf = udf(get_prefix, ArrayType(StringType()))
df = df.withColumn("prefix", prefix_udf(col("sorted_terms")))

# Generate candidate pairs using prefix-based filtering
df_pairs = df.alias("a").join(df.alias("b"), F.array_intersect(col("a.prefix"), col("b.prefix")).isNotNull()) \
                       .filter(col("a.index") < col("b.index")) \
                       .select(col("a.index").alias("index1"), col("b.index").alias("index2"),
                               col("a.terms").alias("terms1"), col("b.terms").alias("terms2"))

# UDF to compute Jaccard similarity
def jaccard_similarity(terms1, terms2):
    set1, set2 = set(terms1), set(terms2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return float(intersection) / union

jaccard_udf = udf(jaccard_similarity)

# Compute similarity for candidate pairs and filter based on threshold
df_result = df_pairs.withColumn("jaccard_similarity", jaccard_udf(col("terms1"), col("terms2"))) \
                    .filter(col("jaccard_similarity") > 0.5) \
                    .select("index1", "index2", "jaccard_similarity")

# Show results
df_result.show(truncate=False)

spark.stop()
