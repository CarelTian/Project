from pyspark import SparkContext
from pyspark.sql import SparkSession
import math
from itertools import product
import sys

class Project2:
    def run(self, inputPath, outputPath, d, s):
        sc = SparkContext.getOrCreate()
        spark = SparkSession(sc)
        parsed_rdd = sc.textFile(inputPath).map(self.parse_line)
        prefixed_rdd = parsed_rdd.map(lambda record:self.generate_prefix(record,s))

        indexed_rdd = prefixed_rdd.map(lambda record: self.grid_index(record, d))

        # Assign records to their respective grid cells
        cells_rdd = indexed_rdd.map(lambda record: (record[-1], record[:-1]))
        unique_cells = cells_rdd.keys().distinct()

        cell_pairs = unique_cells.flatMap(self.generate_neighbor_cells)
        # Prepare to join neighboring cell records
        cell_records = cells_rdd

        # Create two versions of cell_records, one for left and one for right joins
        cell_records_left = cell_records.map(lambda x: (x[0], ('L', x[1])))
        cell_records_right = cell_records.map(lambda x: (x[0], ('R', x[1])))

        # Join cell_pairs with cell_records_left
        cell_pairs_left = cell_pairs.map(lambda x: (x[0], x[1]))
        joined_left = cell_pairs_left.join(cell_records_left)

        # Convert result to (neighbor_cell, (cell, 'L', record))
        joined_left = joined_left.map(lambda x: (x[1][0], (x[0], x[1][1][0], x[1][1][1])))

        joined = joined_left.join(cell_records_right)

        candidate_pairs_rdd = joined.flatMap(lambda data: self.generate_candidate_pairs(data, d, s)).distinct().coalesce(1)
        sorted_pairs_rdd = candidate_pairs_rdd.sortBy(lambda x: (x[0][0], x[0][1]))
        formatted_output_rdd = sorted_pairs_rdd.map(lambda x: f"({x[0][0]},{x[0][1]}):{x[1][0]}, {x[1][1]}")
        formatted_output_rdd.saveAsTextFile(outputPath)
        spark.stop()

    def parse_line(self,line):
        parts = line.strip().split("#")
        index = int(parts[0])  # Ensure index is an integer
        location = eval(parts[1])
        terms = set(parts[2].split())
        return (index, location, terms)

    # Generate prefixes for each record
    def generate_prefix(self,record,s):
        index, location, terms = record
        sorted_terms = sorted(terms)
        num_terms = len(sorted_terms)
        if num_terms == 0:
            prefix = []
        else:
            min_overlap = int(math.ceil(s * num_terms))
            prefix_length = num_terms - min_overlap + 1
            prefix_length = max(1, prefix_length)
            prefix = sorted_terms[:prefix_length]
        return (index, location, terms, prefix)

    # Compute grid index
    def grid_index(self,record,d):
        index, location, terms, prefix = record
        x, y = location
        grid_x = int(x // d)
        grid_y = int(y // d)
        return (index, location, terms, prefix, (grid_x, grid_y))

    def generate_neighbor_cells(self,cell):
        x, y = cell
        # Generate combinations of each grid cell with its neighboring cells
        neighbor_offsets = list(product([-1, 0, 1], repeat=2))
        neighbors = []
        for dx, dy in neighbor_offsets:
            neighbor_cell = (x + dx, y + dy)
            neighbors.append((cell, neighbor_cell))
        return neighbors

    def generate_candidate_pairs(self,data,d,s):
        neighbor_cell, ((cell_left, tag_left, record_left), (tag_right, record_right)) = data
        ret=[]
        # Check if the cells are neighbors
        if tag_left != 'L' or tag_right != 'R':
            return ret
        idx1, loc1, terms1, prefix1 = record_left
        idx2, loc2, terms2, prefix2 = record_right
        if idx1 >= idx2:
            return ret
        # Prefix filtering
        if not set(prefix1).intersection(set(prefix2)):
            return ret
        # Length filtering
        len1 = len(terms1)
        len2 = len(terms2)
        max_len = max(len1, len2)
        min_overlap = int(math.ceil(s * max_len))
        if min(len1, len2) < min_overlap:
            return ret
        # Distance filtering
        distance = math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
        if distance > d:
            return ret
        # Calculate Jaccard similarity
        intersection = len(terms1 & terms2)
        union = len(terms1 | terms2)
        jaccard_similarity = intersection / union if union > 0 else 0

        if jaccard_similarity < s:
            return ret
        ret.append(((idx1, idx2), (round(distance, 6), round(jaccard_similarity, 6))))
        return ret
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Wrong arguments")
        sys.exit(-1)
    Project2().run(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
# spark-submit project3.py "file:///Users/lyt/9313lab/project3/testcase.txt" "file:///Users/lyt/9313lab/project3/output" 12 0.2