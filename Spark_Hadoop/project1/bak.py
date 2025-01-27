from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.compat import jobconf_from_env
import re
import heapq
import math
class Pair:
    def __init__(self,word,weight,year):
        self.word= word
        self.weight= weight
        self.year= year
    def __lt__(self, other):
        if self.weight!=other.weight:
            return self.weight<other.weight
        else:
            return self.word>other.word
class proj1(MRJob):
    def mapper(self,_,line):
        date,text=re.split(",",line)
        year=date[:4]
        st=set()
        for word in text.split():
            if word not in st:
                st.add(word)
                yield year+';'+word,1
            yield year+';#'+word,1
        yield year+';*',1
    def combiner(self, key, values):
        yield key,sum(values)
    def reducer_init(self):
        self.line=0
        self.words={}
        self.curYear=None
    def reducer(self,key,values):
        year,text=key.split(';',1)
        if year != self.curYear:
            self.curYear = year
            self.line = 0
            self.words = {}
        if text == '*':
            self.line += sum(values)
        elif text[0] == '#':
            word = text[1:]
            self.words[word] = sum(values)
        else:
            word = text
            tf = self.words[word]
            divide=self.line / sum(values)
            idf = math.log(divide, 10)
            weight = tf * idf
            yield year + ";" + word + ";" + str(weight), None
    def mapper2_init(self):
        self.k = int(jobconf_from_env('myjob.settings.k'))
        self.topk = []
        self.curYear=''
        heapq.heapify(self.topk)
    def mapper2(self, key, value):
        year,word,weight=key.split(';')
        weight=eval(weight)
        p = Pair(word, weight,year)
        if year==self.curYear:
            heapq.heappush(self.topk,p)
            if len(self.topk)>self.k:
                heapq.heappop(self.topk)
        else:
            if len(self.topk):
                for i in range(len(self.topk)):
                    yield self.topk[i].year + "#" + self.topk[i].word+"#"+str(self.topk[i].weight), None
            self.curYear=year
            self.topk.clear()
            heapq.heappush(self.topk, p)
    def mapper2_final(self):
        for i in range(len(self.topk)):
            yield self.topk[i].year + "#" + self.topk[i].word+"#"+str(self.topk[i].weight), None
    def reducer2_init(self):
        self.k = int(jobconf_from_env('myjob.settings.k'))
        self.curYear=''
        self.count=0
    def reducer2(self, key,values):
        year,word,weight=key.split("#")
        if year==self.curYear:
             if self.count < self.k:
                yield year, word+','+weight
                self.count += 1
        else:
            self.count = 0
            self.curYear =year
            if self.count < self.k:
               yield year, word+','+weight
               self.count += 1

    SORT_VALUES = True
    def steps(self):
        # using multiple reducers in the first step
        JOBCONF1 = {
            'mapreduce.job.reduces': 1
        }
        # using a single reducer in the second step
        JOBCONF2 = {
            'mapreduce.job.reduces': 3,
            'stream.num.map.output.key.fields': 3,
            'mapreduce.map.output.key.field.separator': '#',
            'mapreduce.job.output.key.comparator.class': 'org.apache.hadoop.mapreduce.lib.partition.KeyFieldBasedComparator',
            'mapreduce.partition.keycomparator.options': '-k1,1 -k3,3nr -k2,2',
            'mapreduce.partition.keypartitioner.options': '-k1,1'
        }
        return [
            MRStep(jobconf=JOBCONF1, mapper=self.mapper,reducer=self.reducer, reducer_init=self.reducer_init),
            MRStep(jobconf=JOBCONF2, mapper_init=self.mapper2_init, mapper=self.mapper2,
                   mapper_final=self.mapper2_final, reducer_init=self.reducer2_init, reducer=self.reducer2)
        ]
if __name__ == '__main__':
    proj1.run()

# python3 project1.py -r hadoop abcnews.txt -o hdfs:///user/lyt/output/ --jobconf myjob.settings.k=2