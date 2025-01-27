from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.compat import jobconf_from_env
import re
import math

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
        # Aggregate counts locally
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
        word_weights = []
        for word in term_freq:
            tf = term_freq[word]
            df = doc_freq.get(word, 1)
            idf = math.log(total_docs / df, 10)
            weight = tf * idf
            word_weights.append((weight, word))

        word_weights.sort(key=lambda x: (-x[0], x[1]))
        for i in range(min(self.k, len(word_weights))):
            weight, word = word_weights[i]
            weight=str(weight)
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
