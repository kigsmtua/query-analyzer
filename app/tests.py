import unittest
from dispatcher import Dispatcher
from collections import defaultdict


class DispatcherTests(unittest.TestCase):
    def test_tasks_with_same_hosts_are_sent_to_same_queue(self):
        workers = ['hosts_'+ str(x) for x in range(5)]
        dispatcher = Dispatcher(workers)
        host = "host_000006"
        first_pick = dispatcher.select_worker(host)
        second_pick = dispatcher.select_worker(host)
        self.assertEqual(first_pick,second_pick,"Dispatcher should pick same worker for same host")
    
    def tests_worker_doesnt_pick_tasks_for_only_one_host(self):
        workers = ['worker_'+ str(x) for x in range(5)]
        hosts = ["host_00000"+str(x) for x in range(100)]
        dispatcher =  Dispatcher(workers)
        selection = defaultdict(list)
        for host in hosts:
            worker = dispatcher.select_worker(host)
            selection[worker].append(host)
        
        worker_1 = selection['worker_1']
        duplicate_check = {}
        for i in worker_1:
            self.assertEqual(None, duplicate_check.get(i))
            duplicate_check[i] = 1

if __name__ == "__main__":
    unittest.main()
