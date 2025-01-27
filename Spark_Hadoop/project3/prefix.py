from pyspark import SparkContext
from pyspark.sql.session import SparkSession
import sys
import math

class Project2:
    def run(self, inputPath, outputPath, d, s):
        spark = SparkSession.builder.appName("project3").getOrCreate()
        sc = spark.sparkContext

        # 读取输入文件并解析行
        lines = sc.textFile(inputPath)
        records = lines.map(self.parseLine)

        # 将每个记录映射到其所在的网格单元和相邻单元
        grid_records = records.flatMap(lambda record: self.mapToNeighboringGrids(record, d))

        # 按网格单元分组记录
        grid_index = grid_records.groupByKey().mapValues(list)

        # 在每个网格单元内生成候选对
        candidate_pairs = grid_index.flatMap(lambda x: self.generate_candidate_pairs(x[1]))

        # 删除重复的对
        candidate_pairs = candidate_pairs.distinct()

        # 计算距离和相似度，过滤符合条件的对
        result = candidate_pairs.map(
            lambda x: self.filter_pairs_with_jaccard(x, d, s)
        ).filter(lambda x: x is not None)

        # 删除重复的对
        result = result.distinct()

        # 排序并保存结果
        result = result.coalesce(1).sortBy(lambda x: (x[0], x[1]))
        result = result.map(lambda x: f"({x[0]},{x[1]}):{round(x[2],6):.6f},{round(x[3],6):.6f}")
        result.saveAsTextFile(outputPath)

        spark.stop()

    def parseLine(self, line):
        parts = line.strip().split("#")
        index = int(parts[0])
        location = eval(parts[1])
        terms = tuple(parts[2].split())  # 改为 tuple 而不是 list
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
        # 将所有记录映射到相邻网格单元，且将 terms 转为 tuple 以便可哈希
        return [(tuple(cell), (index, location, tuple(terms))) for cell in neighboring_cells]

    def generate_candidate_pairs(self, records):
        candidate_pairs = []
        records_list = list(records)
        for i in range(len(records_list)):
            idx1, loc1, terms1 = records_list[i]
            for j in range(i + 1, len(records_list)):
                idx2, loc2, terms2 = records_list[j]
                # terms1 和 terms2 现在是 tuple，可以安全使用
                candidate_pairs.append((idx1, idx2, loc1, loc2, terms1, terms2))
        return candidate_pairs

    def calculate_jaccard_similarity(self, list1, list2):
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        set1 = set(list1)
        set2 = set(list2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union

    def filter_pairs_with_jaccard(self, data, d_threshold, s_threshold):
        idx1, idx2, loc1, loc2, terms1, terms2 = data

        # 计算欧氏距离
        distance = math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
        if distance > d_threshold:
            return None

        # 计算 Jaccard 相似度
        jaccard_similarity = self.calculate_jaccard_similarity(terms1, terms2)
        if jaccard_similarity < s_threshold:
            return None

        if idx1 <= idx2:
            return (idx1, idx2, distance, jaccard_similarity)
        else:
            return (idx2, idx1, distance, jaccard_similarity)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: project2.py <inputPath> <outputPath> <distance_threshold> <similarity_threshold>")
        sys.exit(-1)
    inputPath = sys.argv[1]
    outputPath = sys.argv[2]
    d = float(sys.argv[3])
    s = float(sys.argv[4])
    Project2().run(inputPath, outputPath, d, s)
#精确度很高，但是慢