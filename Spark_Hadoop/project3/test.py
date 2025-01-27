from pyspark import SparkContext, SparkConf
from pyspark.sql.session import SparkSession
import sys
import math
import random
from collections import defaultdict

class Project2:
    def run(self, inputPath, outputPath, d, s):
        spark = SparkSession.builder.appName("project3").getOrCreate()
        sc = spark.sparkContext

        # 读取输入文件并解析行
        lines = sc.textFile(inputPath)
        records = lines.map(self.parseLine)

        # 广播索引到术语的映射
        index_terms_map = records.map(lambda x: (x[0], x[2])).collectAsMap()
        index_terms_broadcast = sc.broadcast(index_terms_map)

        # 设置 MinHash 和 LSH 的参数
        num_hashes = 25  # 总的哈希函数数量
        num_bands = 5   # 分成的带数
        rows_per_band = 5  # 每个带的行数
        threshold = s     # 相似度阈值

        # 生成用于 MinHash 的哈希函数
        max_hash =2**32-1
        hash_functions = []
        for _ in range(num_hashes):
            a = random.randint(1, max_hash)
            b = random.randint(0, max_hash)
            hash_functions.append((a, b))
        hash_functions_broadcast = sc.broadcast(hash_functions)

        # 计算所有记录的 MinHash 签名
        records_with_signature = records.map(
            lambda record: self.add_signature(record, hash_functions_broadcast.value, max_hash)
        )

        # 将每个记录映射到其所在的网格单元和相邻单元
        grid_records = records_with_signature.flatMap(lambda record: self.mapToNeighboringGrids(record, d))

        # 按网格单元分组记录
        grid_index = grid_records.groupByKey().mapValues(list)

        # 使用 LSH 在每个网格单元内找到候选对
        candidate_pairs = grid_index.flatMap(lambda x: self.lsh_in_grid_cell(x[1], num_bands, rows_per_band))

        # 删除重复的对
        candidate_pairs = candidate_pairs.distinct()

        # 根据距离和相似度阈值过滤候选对
        result = candidate_pairs.map(
            lambda x: self.filter_pairs_with_jaccard(x, d, threshold, index_terms_broadcast.value)
        ).filter(lambda x: x is not None)

        # 再次删除重复的对
        result = result.distinct()

        # 将结果合并到一个分区并排序
        result = result.coalesce(1).sortBy(lambda x: (x[0], x[1]))

        # 格式化并保存结果
        result = result.map(lambda x: f"({x[0]},{x[1]}):{round(x[2],6):.6f},{round(x[3],6):.6f}")
        result.saveAsTextFile(outputPath)

        spark.stop()

    def parseLine(self, line):
        parts = line.strip().split("#")
        index = int(parts[0])  # 确保索引为整数
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
        index, location, signature = record  # 这里不包括 'terms'
        grid_cell = self.gridIndex(location, d)
        neighboring_cells = self.getNeighboringGrids(grid_cell)
        # 将记录映射到所有相邻的网格单元
        return [(tuple(cell), (index, location, signature)) for cell in neighboring_cells]

    def add_signature(self, record, hash_functions, max_hash):
        index, location, terms = record
        signature = []
        if terms:
            for a, b in hash_functions:
                min_hash = min(((a * hash(term) + b) % max_hash) for term in terms)
                signature.append(min_hash)
        else:
            # 如果术语集为空，使用最大哈希值填充签名
            signature = [max_hash] * len(hash_functions)
        return (index, location, tuple(signature))  # 确保签名是元组

    def lsh_in_grid_cell(self, records, num_bands, rows_per_band):
        import itertools

        # 为每个带创建桶
        buckets = defaultdict(list)
        for record in records:
            index, location, signature = record
            for band_idx in range(num_bands):
                start = band_idx * rows_per_band
                end = start + rows_per_band
                band_signature = signature[start:end]
                # 使用带索引和带签名作为键
                buckets[(band_idx, tuple(band_signature))].append((index, location, signature))

        # 从桶中生成候选对
        candidate_pairs = []
        for bucket_records in buckets.values():
            if len(bucket_records) > 1:
                # 在桶内生成所有可能的对
                for rec1, rec2 in itertools.combinations(bucket_records, 2):
                    idx1, loc1, _ = rec1
                    idx2, loc2, _ = rec2
                    # 为了保持一致性，对索引进行排序
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

        # 计算欧氏距离
        distance = math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
        if distance > d_threshold:
            return None

        # 从广播的映射中获取 'terms'
        terms1 = index_terms_map[idx1]
        terms2 = index_terms_map[idx2]

        # 使用术语集计算实际的 Jaccard 相似度
        jaccard_similarity = self.calculate_jaccard_similarity(terms1, terms2)

        if jaccard_similarity < s_threshold:
            return None

        # 返回包含距离和相似度的对
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
# spark-submit test.py "file:///Users/lyt/9313lab/project3/testcase.txt" "file:///Users/lyt/9313lab/project3/output" 150 0.6