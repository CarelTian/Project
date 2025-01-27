from pyspark import SparkContext, SparkConf
from pyspark.sql.session import SparkSession
import sys
import math

class Project2:
    def run(self, inputPath, outputPath, d, s):
        spark = SparkSession.builder.master("local").appName("project3").getOrCreate()
        sc = spark.sparkContext

        # Read input file and parse lines
        lines = sc.textFile(inputPath)
        records = lines.map(self.parseLine)

        # Broadcast the mapping from index to terms to avoid including 'terms' in RDDs
        index_terms_map = records.map(lambda x: (x[0], x[2])).collectAsMap()
        index_terms_broadcast = sc.broadcast(index_terms_map)

        # Generate candidate pairs using Cartesian product and filter by distance threshold
        candidate_pairs = records.cartesian(records) \
            .filter(lambda x: x[0][0] < x[1][0]) \
            .filter(lambda x: self.filter_by_distance(x, d))

        # Calculate Jaccard similarity for each candidate pair
        result = candidate_pairs.map(
            lambda x: self.filter_pairs_with_jaccard(x, s, index_terms_broadcast.value)
        ).filter(lambda x: x is not None)

        # Remove duplicate pairs
        result = result.distinct()
        result = result.coalesce(1)
        # Sort the final results
        result = result.sortBy(lambda x: (x[0], x[1]))


        # Format and save results
        result = result.map(lambda x: f"({x[0]},{x[1]}):{x[2]:.6f},{x[3]:.6f}")
        result.saveAsTextFile(outputPath)

        spark.stop()

    def parseLine(self, line):
        parts = line.strip().split("#")
        index = int(parts[0])  # 确保索引为整数
        location = eval(parts[1])
        terms = set(parts[2].split())
        return (index, location, terms)

    def filter_by_distance(self, pair, d_threshold):
        """
        Filter pairs by Euclidean distance threshold.
        """
        (_, loc1, _), (_, loc2, _) = pair
        distance = math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
        return distance <= d_threshold

    def calculate_jaccard_similarity(self, set1, set2):
        """
        Calculate Jaccard similarity between two sets of terms.
        """
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union

    def filter_pairs_with_jaccard(self, pair_data, s_threshold, index_terms_map):
        """
        Calculate the Jaccard similarity for a given pair of records and filter by similarity threshold.
        """
        (idx1, loc1, _), (idx2, loc2, _) = pair_data

        # Retrieve 'terms' from the broadcasted index_terms_map
        terms1 = index_terms_map[idx1]
        terms2 = index_terms_map[idx2]

        # Calculate real Jaccard similarity using term sets
        jaccard_similarity = self.calculate_jaccard_similarity(terms1, terms2)

        if jaccard_similarity < s_threshold:
            return None

        # Return the pair with their distance and real Jaccard similarity
        distance = math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
        return (idx1, idx2, distance, jaccard_similarity)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: project2.py <inputPath> <outputPath> <distance_threshold> <similarity_threshold>")
        sys.exit(-1)
    inputPath = sys.argv[1]
    outputPath = sys.argv[2]
    d = float(sys.argv[3])
    s = float(sys.argv[4])
    Project2().run(inputPath, outputPath, d, s)