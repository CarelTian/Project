from pyspark import SparkContext
from pyspark.sql import SparkSession
import math
from itertools import product

class Project2:
    def run(self, inputPath, outputPath, d, s):
        sc = SparkContext.getOrCreate()
        spark = SparkSession(sc)

        # 读取数据并解析为 (index, location, terms)
        def parse_line(line):
            parts = line.strip().split("#")
            index = int(parts[0])  # 确保索引为整数
            location = eval(parts[1])
            terms = set(parts[2].split())
            return (index, location, terms)

        parsed_rdd = sc.textFile(inputPath).map(parse_line)

        # 为每条记录生成前缀
        def generate_prefix(record):
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

        prefixed_rdd = parsed_rdd.map(generate_prefix)

        # 计算网格索引
        def grid_index(record):
            index, location, terms, prefix = record
            x, y = location
            grid_x = int(x // d)
            grid_y = int(y // d)
            return (index, location, terms, prefix, (grid_x, grid_y))

        indexed_rdd = prefixed_rdd.map(grid_index)

        # 将记录分配到其所属的网格单元
        cells_rdd = indexed_rdd.map(lambda record: (record[-1], record[:-1]))

        # 获取所有的网格单元
        unique_cells = cells_rdd.keys().distinct()

        # 生成每个网格单元与其邻居单元的组合
        neighbor_offsets = list(product([-1, 0, 1], repeat=2))

        def generate_neighbor_cells(cell):
            x, y = cell
            neighbors = []
            for dx, dy in neighbor_offsets:
                neighbor_cell = (x + dx, y + dy)
                neighbors.append((cell, neighbor_cell))
            return neighbors

        cell_pairs = unique_cells.flatMap(generate_neighbor_cells)

        # 准备将记录按照网格单元分区，以便进行连接操作
        partitioned_cells_rdd = cells_rdd

        # 将网格单元与其记录进行连接
        cell_records = partitioned_cells_rdd

        # 为了连接邻居单元的记录，首先将cell_pairs与cell_records进行连接
        # 需要准备两个版本的cell_records，一个用于左侧，一个用于右侧
        cell_records_left = cell_records.map(lambda x: (x[0], ('L', x[1])))
        cell_records_right = cell_records.map(lambda x: (x[0], ('R', x[1])))

        # 将cell_pairs与cell_records_left连接
        cell_pairs_left = cell_pairs.map(lambda x: (x[0], x[1]))
        joined_left = cell_pairs_left.join(cell_records_left)

        # 将结果转换为 (neighbor_cell, (cell, 'L', record))
        joined_left = joined_left.map(lambda x: (x[1][0], (x[0], x[1][1][0], x[1][1][1])))

        # 将joined_left与cell_records_right连接
        joined = joined_left.join(cell_records_right)

        # 现在，我们有了 (neighbor_cell, ((cell, 'L', record_left), ('R', record_right)))
        # 我们需要过滤掉非邻居单元的组合，并生成候选对

        def generate_candidate_pairs(data):
            neighbor_cell, ((cell_left, tag_left, record_left), (tag_right, record_right)) = data
            # 检查单元是否是邻居关系
            if tag_left != 'L' or tag_right != 'R':
                return []

            idx1, loc1, terms1, prefix1 = record_left
            idx2, loc2, terms2, prefix2 = record_right

            # 确保不重复计算相同的对
            if idx1 >= idx2:
                return []

            # 位置过滤（仅在邻居单元内的记录才进行比较）
            # 已经确保是邻居单元，无需再次检查

            # 前缀过滤
            if not set(prefix1).intersection(set(prefix2)):
                return []

            # 长度过滤
            len1 = len(terms1)
            len2 = len(terms2)
            max_len = max(len1, len2)
            min_overlap = int(math.ceil(s * max_len))
            if min(len1, len2) < min_overlap:
                return []

            # 距离过滤
            distance = math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
            if distance > d:
                return []

            # 计算Jaccard相似度
            intersection = len(terms1 & terms2)
            union = len(terms1 | terms2)
            jaccard_similarity = intersection / union if union > 0 else 0

            if jaccard_similarity >= s:
                return [((idx1, idx2), (round(distance, 6), round(jaccard_similarity, 6)))]
            else:
                return []

        candidate_pairs_rdd = joined.flatMap(generate_candidate_pairs).distinct().coalesce(1)

        # 排序
        sorted_pairs_rdd = candidate_pairs_rdd.sortBy(lambda x: (x[0][0], x[0][1]))

        # 格式化输出
        formatted_output_rdd = sorted_pairs_rdd.map(lambda x: f"({x[0][0]},{x[0][1]}):{x[1][0]}, {x[1][1]}")

        # 保存结果
        formatted_output_rdd.saveAsTextFile(outputPath)

        sc.stop()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 5:
        print("Usage: Project2 <inputPath> <outputPath> <d> <s>")
        sys.exit(-1)
    Project2().run(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
