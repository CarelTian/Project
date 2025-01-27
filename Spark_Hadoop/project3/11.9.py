from pyspark import SparkContext, SparkConf
from pyspark.sql.session import SparkSession
import sys
import math
import time


class Project2:
    def run(self, inputPath, outputPath, d, s):
        sc = SparkContext.getOrCreate()
        sc.setLogLevel("ERROR")  # 设置日志级别为 ERROR
        spark = SparkSession(sc)

        start_time = time.time()  # 记录开始时间
        lines = sc.textFile(inputPath)
        records = lines.map(self.parseLine)

        index_terms_map = records.map(lambda x: (x[0], x[2])).collectAsMap()
        index_terms_broadcast = sc.broadcast(index_terms_map)

        grid_records = records.flatMap(lambda record: self.mapToNeighboringGrids(record, d))
        grid_index = grid_records.groupByKey().mapValues(list)
        candidate_pairs = grid_index.flatMap(lambda x: self.compute_similarities_in_grid(x[1], d, s, index_terms_broadcast.value))

        candidate_pairs = candidate_pairs.distinct().coalesce(1)
        candidate_pairs = candidate_pairs.sortBy(lambda x: (x[0], x[1]))
        candidate_pairs = candidate_pairs.map(lambda x: f"({x[0]},{x[1]}):{round(x[2], 6)}, {round(x[3], 6)}")
        candidate_pairs.saveAsTextFile(outputPath)

        sc.stop()

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
        neighboring_grids = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                neighboring_grids.append((grid_x + dx, grid_y + dy))
        return neighboring_grids

    def mapToNeighboringGrids(self, record, d):
        index, location, terms = record
        grid_cell = self.gridIndex(location, d)
        neighboring_cells = self.getNeighboringGrids(grid_cell)
        return [(tuple(cell), (index, location, terms)) for cell in neighboring_cells]

    def compute_similarities_in_grid(self, records, d_threshold, s_threshold, index_terms_map):
        from itertools import combinations

        candidate_pairs = []
        for rec1, rec2 in combinations(records, 2):
            idx1, loc1, terms1 = rec1
            idx2, loc2, terms2 = rec2

            distance = math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
            if distance > d_threshold:
                continue

            terms1 = index_terms_map[idx1]
            terms2 = index_terms_map[idx2]

            jaccard_similarity = self.calculate_jaccard_similarity(terms1, terms2)
            if jaccard_similarity >= s_threshold:
                candidate_pairs.append((idx1, idx2, distance, jaccard_similarity))

        return candidate_pairs

    def calculate_jaccard_similarity(self, set1, set2):
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Wrong arguments")
        sys.exit(-1)
    Project2().run(sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]))

# file:///home/Votes.csv
# spark-submit project3.py "file:///home/testcase.txt" "file:///home/output" 12 0.2