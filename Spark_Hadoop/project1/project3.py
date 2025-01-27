from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.compat import jobconf_from_env
import re
import math
import heapq

class Pair:
    def __init__(self,word,weight):
        self.word= word
        self.weight= weight
    def __lt__(self, other):
        if self.weight!=other.weight:
            return self.weight>other.weight
        else:
            return self.word<other.word
class proj1(MRJob):

    def mapper(self, _, line):
        date, text = re.split(",", line, maxsplit=1)
        year = date[:4]
        words_in_line = text.split()
        unique_words = set(words_in_line)
        yield year, ('YEAR', 1)
        for word in unique_words:
            yield year, ('COUNT', word, 1)
        for word in words_in_line:
            yield year, ('FRE', word, 1)

    def combiner(self, key, values):
        total_docs = 0
        doc_freq = {}
        term_freq = {}
        year=key
        for value in values:
            if value[0] == 'YEAR':
                total_docs += value[1]
            elif value[0] == 'COUNT':
                word = value[1]
                count = value[2]
                doc_freq[word] = doc_freq.get(word, 0) + count
            elif value[0] == 'FRE':
                word = value[1]
                count = value[2]
                term_freq[word] = term_freq.get(word, 0) + count
        if total_docs > 0:
            yield year, ('YEAR', total_docs)
        for word, count in doc_freq.items():
            yield year, ('COUNT', word, count)
        for word, count in term_freq.items():
            yield year, ('FRE', word, count)
    def reducer_init(self):
        self.k = int(jobconf_from_env('myjob.settings.k'))
        self.shit=[]
        heapq.heapify(self.shit)


    def reducer(self, key, values):
        total_docs = 0
        doc_freq = {}
        term_freq = {}
        year=key
        for value in values:
            if value[0] == 'YEAR':
                total_docs += value[1]
            elif value[0] == 'COUNT':
                word = value[1]
                count = value[2]
                doc_freq[word] = doc_freq.get(word, 0) + count
            elif value[0] == 'FRE':
                word = value[1]
                count = value[2]
                term_freq[word] = term_freq.get(word, 0) + count
        for word in term_freq:
            tf = term_freq[word]
            df = doc_freq.get(word, 1)
            idf = math.log(total_docs / df, 10)
            weight = tf * idf
            heapq.heappush(self.shit,Pair(word,weight))
        size=len(self.shit)
        for i in range(min(self.k, size)):
            p=heapq.heappop(self.shit)
            weight, word = str(p.weight), p.word
            yield year, word+','+weight

    def steps(self):
        return [
            MRStep(
                mapper=self.mapper,
                combiner=self.combiner,
                reducer_init=self.reducer_init,
                reducer=self.reducer
            )
        ]

if __name__ == '__main__':
    proj1.run()

# python3 project3.py -r hadoop test.txt -o hdfs:///user/user/output/ --jobconf myjob.settings.k=3