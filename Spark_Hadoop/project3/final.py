from pyspark import SparkContext, SparkConf
from pyspark.sql.session import SparkSession
import sys
import math
import random
from collections import defaultdict

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

        # Broadcast the parameters needed for MinHash and LSH
        num_hashes = 100  # Total number of hash functions
        num_bands = 20  # Number of bands
        rows_per_band =5  # Rows per band
        threshold = s     # Similarity threshold

        # Generate hash functions for MinHashing
        max_hash = 2 ** 32 - 1
        hash_functions = []
        for i in range(num_hashes):
            a = random.randint(1, max_hash)
            b = random.randint(0, max_hash)
            hash_functions.append((a, b))
        hash_functions_broadcast = sc.broadcast(hash_functions)

        # Compute MinHash signatures for all records
        records_with_signature = records.map(
            lambda record: self.add_signature(record, hash_functions_broadcast.value, num_hashes, max_hash)
        )

        # Map each record to its grid cell and neighboring cells
        grid_records = records_with_signature.flatMap(lambda record: self.mapToNeighboringGrids(record, d))

        # Group records by grid cell
        grid_index = grid_records.groupByKey().mapValues(list)

        # Find candidate pairs within each grid cell using LSH
        candidate_pairs = grid_index.flatMap(lambda x: self.lsh_in_grid_cell(x[1], num_bands, rows_per_band))

        # Remove duplicate pairs
        candidate_pairs = candidate_pairs.distinct()

        # Filter candidate pairs based on distance and real Jaccard similarity thresholds
        result = candidate_pairs.map(
            lambda x: self.filter_pairs_with_jaccard(x, d, threshold, index_terms_broadcast.value)
        ).filter(lambda x: x is not None)

        # Remove duplicates again if necessary
        result = result.distinct()
        result = result.coalesce(1)
        # Sort the final results
        result = result.sortBy(lambda x: (x[0], x[1]))

        # Format and save results
        result = result.map(lambda x: f"({x[0]},{x[1]}):{x[2]:.6f}, {x[3]:.6f}")
        result.saveAsTextFile(outputPath)

        spark.stop()

    def parseLine(self, line):
        parts = line.strip().split("#")
        index = int(parts[0])
        location = eval(parts[1])
        terms = set(parts[2].split())
        return (index, location, terms)

    def gridIndex(self, location, d):
        x, y = location
        grid_x = int(x // d)
        grid_y = int(y // d)
        return (grid_x, grid_y)

    def getNeighboringGrids(self, grid_cell):
        grid_x, grid_y = grid_cell
        neighboring_grids=[]
        for dx in range(-1,2):
            for dy in range(-1,2):
                neighboring_grids.append((grid_x + dx, grid_y + dy))

        return neighboring_grids

    def mapToNeighboringGrids(self, record, d):
        index, location, signature = record  # Exclude 'terms' here
        grid_cell = self.gridIndex(location, d)
        neighboring_cells = self.getNeighboringGrids(grid_cell)
        # Map the record to all neighboring grid cells
        return [(tuple(cell), (index, location, signature)) for cell in neighboring_cells]

    def add_signature(self, record, hash_functions, num_hashes, max_hash):
        index, location, terms = record
        signature = []
        if terms:
            for a, b in hash_functions:
                min_hash = min(((a * hash(term) + b) % max_hash) for term in terms)
                signature.append(min_hash)
        else:
            signature = [max_hash] * num_hashes
        return (index, location, tuple(signature))

    def lsh_in_grid_cell(self, records, num_bands, rows_per_band):
        """
        Apply LSH within a grid cell to find candidate pairs based on signature bands.
        """
        from collections import defaultdict
        import itertools

        # Create buckets for each band
        buckets = defaultdict(list)
        for record in records:
            index, location, signature = record
            for band_idx in range(num_bands):
                start = band_idx * rows_per_band
                end = start + rows_per_band
                band_signature = tuple(signature[start:end])
                # Use band index and band signature as key
                buckets[(band_idx, band_signature)].append((index, location, signature))

        # Generate candidate pairs from buckets
        candidate_pairs = []
        for bucket_records in buckets.values():
            if len(bucket_records) > 1:
                # Generate all possible pairs within the bucket
                for rec1, rec2 in itertools.combinations(bucket_records, 2):
                    idx1, loc1, sig1 = rec1
                    idx2, loc2, sig2 = rec2
                    # Order indices to ensure consistency
                    if idx1 <= idx2:
                        candidate_pairs.append((idx1, idx2, loc1, loc2))
                    else:
                        candidate_pairs.append((idx2, idx1, loc2, loc1))
        return candidate_pairs

    def calculate_jaccard_similarity(self, set1, set2):
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union

    def filter_pairs_with_jaccard(self, pair_data, d_threshold, s_threshold, index_terms_map):
        idx1, idx2, loc1, loc2 = pair_data

        # Compute Euclidean distance
        distance = math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
        if distance > d_threshold:
            return None

        # Retrieve 'terms' from the broadcasted index_terms_map
        terms1 = index_terms_map[idx1]
        terms2 = index_terms_map[idx2]

        # Calculate real Jaccard similarity using term sets
        jaccard_similarity = self.calculate_jaccard_similarity(terms1, terms2)

        if jaccard_similarity < s_threshold:
            return None

        # Return the pair with their distance and real Jaccard similarity
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

# spark-submit final.py "file:///Users/lyt/9313lab/project3/testcase.txt" "file:///Users/lyt/9313lab/project3/output" 150 0.6