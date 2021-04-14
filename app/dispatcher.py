import hashlib
import time
from functools import wraps

"""
  This implements the rendevous hashing to implement 
  a way to loadbalance tasks across our queues and
  such that tasks belonging to the same host are sent to the same
  worker and the queue does not contains only tasks for one host in an 
  almost even manner such that we can distribute the load to our workers
"""
class Dispatcher(object):  
    def __init__(self, workers=None):
        if workers is None:
            workers = []
        self.workers = workers

    def add(self, worker):
        self.workers.append(worker)
    
    def hash(self, key):
        return int(hashlib.sha256(str(key).encode('utf-8')).hexdigest(), 16)
    
    def select_worker(self, key):
        high_score = -1
        winner = None
        for worker in self.workers:
            score = self.hash("%s-%s" % (str(worker), str(key)))
            if score > high_score:
                high_score, winner = score, worker

            elif score == high_score:
                high_score, winner = score, max(str(worker), str(winner))
        return winner