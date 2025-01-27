from mrjob.job import MRJob

class Job(MRJob):
    def mapper(self, key, value):
        for word in value.strip().split():
            c=word[0]
            if c.isalpha():
                c=c.lower()
                yield c,1
    def combiner(self, key, values):
        yield key,sum(values)
    def reducer(self, key, values):
        yield key,sum(values)

if __name__ == '__main__':
    Job.run()
