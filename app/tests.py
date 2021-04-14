import unittest
from dispatcher import Dispatcher

class DispatcherTests(unittest.TestCase):
    def test_tasks_with_same_hosts_are_sent_to_same_queue(self):
        workers = ['hosts_'+ str(x) for x in range(5)]
        dispatcher = Dispatcher(workers)
        host = "host_000006"
        first_pick = dispatcher.select_worker(host)
        second_pick = dispatcher.select_worker(host)
        print(first_pick)

        self.assertEqual(first_pick,second_pick,"Dispatcher should pick same worker for same host")

if __name__ == "__main__":
    unittest.main()
