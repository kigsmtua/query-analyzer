# Building a Query analyzing tool

The goal is to build a tool that benchmarks query perfomance across multiple workers/clients across a timescale instance.

Our tool, generates a query based on input from a csv file, runs the query and reports how long the query took for benchmarking.

Our tool has to run each query in a separate worker with the following restrictions
1. Queries from each host have to be run by the same worker
2. The worker does not only run queries from one host



# Implementation
I chose to build this in python(as I am more comfortable with python), using multiprocessing to spin up the separate workers as individual processes. We as well us pg-simple to maintain a connection pool to the database to avoid having to open and close a connection to the database every single time.




### Approach
We have a couple of problems solve
1. How to ensure queries for the same host are picked up by the same worker
2. Worker doesnt pick up the queries for same hosts only

**How to ensure queries for the same host are picked up by the same worker**

For this problem I chose to break up the tasks into a couple of queues based of the number of workers and have a worker per queue

So if I want to run 10 workers, I will spin up 10 queues and have a worker per  queue. Meaning, if I can send queries for the same worker to the same queue they will always be picked up by the same worker which solves the problem for us

This however leads to another question, how to enque queries for the same host to the same queue.

For this we implement `Rendezvous hashing` https://en.wikipedia.org/wiki/Rendezvous_hashing using sha256 algorithm. This means when we hash the queue and host, well always get the same queue to pick, and consistently send queries for the same worker to the same queue we also distribute the tasks evenly to the same queue meaning our workers dont pick tasks for same host only

Picking a worker could be a simple as
```python
 worker_queues = ["queue_" + str(x) for x in range(1, no_of_workers + 1)]
 dispatcher = Dispatcher(worker_queues)
 dispacther.select_worker(host) # Will always tell us where to enque our tasks such that they are picked up by the same worker
 ```



# Workflow
1. Instantiate an empty hash to hold our queues
2. Based of on the concurrency given, instantiate our queues and input them in the hash, we have a list of a queue names as well
3. Instatiate the dispacther

4. Loop through the file and use the dispatcher to select the queue we should enqueue our tasks and enque the tasks to the queue

5. Start a process per queue and meaning tasks enqued to a queue will always be picked up by the same worker
6. Run aggregations and output our query statistics after all the workers have finished running
Answer :


# App structure
All code is located in the app folder
1. App.py runs the application
2. Dispatcher.py imlements rendevous hashing to ensure consistent queuing
3. Tests.py implements tests to prove our queuing is consistent



# How to install and run the application

I have used docker and docker-compose to make this abit easier to run and use

1. To run the analyzer run the following steps.

a.) Start the database:
```bash
docker-compose up -d db
```

b.) Setup and migrate the database:

```bash
docker-compose run app migrate
```
c.) Run the analyzer

```bash
docker-compose run app cli 10
```
**The number 10 is the number of concurrent workers I need to run(specify the number you want to)**

This should run the analysis of the default dataset. Which is in the data folder


If you want to specify a custom dataset of query params to run against the analyzer, please run the following

```
docker-compose run -v {relative_path_to file}:/usr/app/data/{file_name} app cli 10 file_name
```

example:
```
docker-compose run -v /home/kiragu/Projects/python/tscale/app/query_params_2.csv:/usr/src/app/data/query_params_2.csv app cli 10 query_params_2.csv

```

We mount the file to run onto the container and run the app container, specifying we want to run the cli tool with 10 concurrent workers for the file name we specified

**N.B** The path to the file has to be the absolute path to the file not a relative path

2. Running test

We can run tests by running the following command

```bash
docker-compose run app test
```