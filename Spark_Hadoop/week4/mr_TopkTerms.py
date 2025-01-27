from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.compat import jobconf_from_env
import heapq
import re

# Try to find the difference between the two solutions
# You can also compare the time and resources used by the two solutions.

class Pair:
    def __init__(self, term, count):
        self.term = term
        self.count = count
    def __lt__(self, other):
        if self.count != other.count:
            return self.count < other.count
        else:
            return self.term < other.term

class Job(MRJob):

    def mapper(self, key, value):
        value = value.strip()
        words = re.split("[ *$&#/\t\n\f\"\'\\,.:;?!\[\](){}<>~\-_]", value.lower())
        for word in words:
            if len(word):
                yield word, 1

    #this version each reducer saved it's own topk frequent terms before next step
    def reducer_init(self):
        self.k = 2
        self.topk = []
        heapq.heapify(self.topk)

    def reducer(self, key, values):
        count = sum(values)
        p = Pair(key, count)
        heapq.heappush(self.topk,p)
        if len(self.topk)>self.k:
            heapq.heappop(self.topk)

    def reducer_final(self):
        for i in range(0,self.k):
            yield self.topk[i].term, self.topk[i].count



    def mapper2_init(self):
        self.k = int(jobconf_from_env('myjob.settings.topk'))
        self.topk = []
        #use a heap to get the local top k from each mapper
        heapq.heapify(self.topk)
        
    def mapper2(self, key, value):
        p = Pair(key, value)
        
        heapq.heappush(self.topk,p)
        if len(self.topk)>self.k:
            heapq.heappop(self.topk)
        
    def mapper2_final(self):
        for i in range(0,min(self.k,len(self.topk))):
            yield self.topk[i].term + "#" + str(self.topk[i].count), None

    def reducer2_init(self):
        self.k = int(jobconf_from_env('myjob.settings.topk'))
        self.counter = 0
    
    def reducer2(self, key, values):
        if self.counter<self.k:
            output_key, output_value = key.split("#")
            yield output_key, output_value
            self.counter +=1

    SORT_VALUES = True

    def steps(self):
        #using multiple reducers in the first step
        JOBCONF1 = {
            'mapreduce.job.reduces':3
        }

        #using a single reducer in the second step
        JOBCONF2 = {
            'stream.num.map.output.key.fields':2,
            'mapreduce.map.output.key.field.separator':'#',
            'mapreduce.job.output.key.comparator.class':'org.apache.hadoop.mapreduce.lib.partition.KeyFieldBasedComparator',
            'mapreduce.partition.keycomparator.options':'-k2,2nr -k1,1'
        }
        return [
            MRStep(jobconf=JOBCONF1, mapper=self.mapper, reducer=self.reducer,reducer_init=self.reducer_init,reducer_final=self.reducer_final),
            MRStep(jobconf=JOBCONF2, mapper_init = self.mapper2_init, mapper=self.mapper2, mapper_final=self.mapper2_final, reducer_init=self.reducer2_init, reducer=self.reducer2)
        ]

if __name__ == '__main__':
    Job.run()
