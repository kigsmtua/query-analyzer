
# Benchmarking

The goal is to benchmark the perfomance of select queries

Each query has to be run on a separate `worker` with a condition that each hosts query needs to be run by the same worker.

# Technologies Used
1. Python (pg-simple for connection pooling)
2. Docker and docker-compose to run the application

## Design

I choose a multiprocessing angle as this is implemented in python which makes it a bit easier to do

We have a couple of challenges that we need to think

1. How do we ensure that queries for the same host are always run by the same `worker`, without the `worker` running queries for only one host


Answer :

We need to build our task queue in a manner such that a queue is processed by one process.

This means that if I have 10 processes(workers) running, I need to have 10 queues so I can run a worker per queue

Which solves the problem, but leads to another question,

How to distribute the tasks in the Queues, in a manner such that tasks with the same host are send to the same queue ?


We need to implement some sort of hashing that will help us pick the queue that we need to send the tasks to and that distributes the tasks among the queues almost evenly

I choose to iplementRendezvous hashing
 https://en.wikipedia.org/wiki/Rendezvous_hashing#:~:text=Rendezvous%20or%20highest%20random%20weight,proxies)
 which enables me to compute a hash and decide which queue to send the tasks





 # How to run
 This run can be as simple as using docker

 docker-compose run app 10 1001
