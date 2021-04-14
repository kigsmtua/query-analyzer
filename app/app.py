import csv
import multiprocessing
import psycopg2
import time
import os
import sys
import argparse
from dispatcher import Dispatcher
import pg_simple
from jinjasql import JinjaSql
import statistics

QUEUES = {}
RESULT_QUEUE = multiprocessing.Queue()

def ENV(val):
    return os.environ[val]

CONNECTION_POOL = pg_simple.config_pool(
    max_conn=50,
    expiration=60,
    host=ENV('DATABASE_HOST'),
    port=ENV('DATABASE_PORT'),
    database=ENV('DATABASE_NAME'),
    user=ENV('DATABASE_USER'),
    pool_manager=pg_simple.pool.ThreadedConnectionPool,
    password=ENV('DATABASE_PASSWORD')
)

def process_tasks(task_queue):
    while not task_queue.empty():
        host_params = task_queue.get()
        time_taken = query(host_params[0], host_params[1], host_params[2])
        RESULT_QUEUE.put(time_taken)
    return True

def buildquery (host, start_time, end_time):
    template = '''
    select
        time_bucket('1 minute', ts) AS period
        , min(usage) AS min_cpu_usage
        , max(usage) AS max_cpu_usage
    from
        cpu_usage
    where
        host = {{ host }}
        and ts >  {{ start_time }} and ts < {{ end_time }}
    group by
        period
    '''
    params = {
        "host": host,
        "start_time": start_time,
        "end_time" : end_time
    }
    j = JinjaSql()
    return j.prepare_query(template, params)

def query(host, start_time, end_time): 
    query,bind_params = buildquery(host, start_time, end_time)
    start = time.time()
    with pg_simple.PgSimple(CONNECTION_POOL) as db:
        db.execute(query,bind_params)
    return time.time() - start


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Query Analyzer',
        epilog='Enjoy :-)'
    )

    parser.add_argument(
        'Concurrency',
        metavar='concurrency',
        type=int,
        help='No of concurrent workers to run'
    )
      
    args = parser.parse_args()
    no_of_workers = args.Concurrency

    # Define the queues our application will utilize
    worker_queues = ["queue_" + str(x) for x in range(1, no_of_workers + 1)]

    # Instantiate the queues as a multiprocessing.Queue()
    for worker_queue in worker_queues:
        QUEUES[worker_queue] = multiprocessing.Queue()

    # Will pick queue to send task
    dispatcher = Dispatcher(worker_queues)  
    try:
        with open('../data/query_params.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    # Select worker responsible for current host
                    worker =  dispatcher.select_worker(row[0])
                    queue = QUEUES.get(worker)
                    queue.put(row)
    except Exception as e:
        print(e)
    
    processes = []
    # Start our processes to be ready to pick up tasks from the queue
    for worker_queue in worker_queues:
        p = multiprocessing.Process(target=process_tasks, args=(QUEUES.get(worker_queue),))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    query_times = []
    no_of_tasks_run = RESULT_QUEUE.qsize()
    while not RESULT_QUEUE.empty():
        query_times.append(RESULT_QUEUE.get())
    
    # Print out statistics we could obtain
    print('Total no of queries run:', no_of_tasks_run)
    print(f'Total Processing time across all queries is: {sum(query_times)} seconds')
    print(f'Minimum query time is :  { min(query_times)} seconds')
    print(f'Median query time is: { statistics.median(query_times)} seconds')
    print(f'Average query time is: { statistics.mean(query_times)} seconds')
    print(f'Maximum query time: { max(query_times)} seconds' )