import sys
import random, math, bisect

import matplotlib.pyplot as plt

cache_hits = 0
cache_requests = 0
queue_structure = ""
cache = []

#Class with methods used for sampling
class Sampler:
    def __init__(self, n):
        self.n = n

    #Sample a time for a given resource
    def calculate_time(self, resource):
        rand = random.uniform(0, 1)
        return -math.log(rand) / (1/(1+resource))


    #Populate a request schedule for all different resources
    def populate_diary(self, n):
        timings = []
        for resource in range(n):
            t = self.calculate_time(resource)
            timings.append((t, resource))
        return sorted(timings, key=lambda x: x[0])


#Process a cache hit
def hit(index):    
    global cache
    if queue_structure == "fifo":
        return
    else:
        if index == 0:
            return
        else:
            resource = cache[index]
            for i in range(index, 0,-1):
                cache[i] = cache[i-1]
            cache[0] = resource
        return

#Process a cache miss
def miss(resource):
    global cache
    if queue_structure == "fifo":
        for i in range(m-1):
            cache[i] = cache[i+1]
        cache[m-1] = resource
    else:
        for i in range(m-1,0,-1):
            cache[i] = cache[i-1]
        cache[0] = resource
    return

#Run the simulation
def simulate(n, m, t_max):
    global cache_hits, cache_requests, cache
    sampler = Sampler(n)
    for i in range(m):
        cache.append(-1)
    hit_rates = [0]
    times = [0]
    t = 0

    graph_data_rate = 1.0
    get_next_datum = graph_data_rate

    req_schedule = sampler.populate_diary(n)

    while t < t_max:
        request = req_schedule.pop(0)
        t = request[0]
        resource = request[1]
        cache_requests += 1

        # Check if hit or miss and respond accordingly
        if resource in cache:
            cache_hits += 1
            hit(cache.index(resource))
        else:
            miss(resource)
        new_time = t + sampler.calculate_time(resource)
        bisect.insort(req_schedule, (new_time, resource))

        # If enough time has passed, collect more graphing data
        if t // get_next_datum >= 1:
            times.append(t)
            hit_rates.append(cache_hits / (cache_requests))
            get_next_datum += graph_data_rate
        
        # Output the current cache hitrate
        print("%.2f percent complete - Current HR: %.4f" % (
            round(t / t_max * 100, 3), 
            round(cache_hits / (cache_requests), 5)
        ), end='\r')
        sys.stdout.flush()
    
    print("")
    plot_hitrate_graph(times, hit_rates)

# Plot and save hitrate graph
def plot_hitrate_graph(times, hit_rates):
    axes = plt.axes()
    axes.plot(times, hit_rates)
    plt.xlabel("Maximum Time (simulated ticks)")
    plt.ylabel("Hit Ratio")
    plt.title("Hit Ratio Graph for an {0}-Cache (m={1}, n={2})".format(queue_structure.upper(), m, n))
    plt.savefig("graphs_{0}_{1}_{2}_{3}.png".format(m, n, t_max, queue_structure.upper()))
    plt.show()



'''     
  Begin the simulation
          
        Command Line Arguments:
            - queue_structure: Replacement policy for the cache.
                               Either "fifo" or "lru"
            - m: Size of the cache.
                 Integer.
            - n: Number of resources to access.
                 Integer.
            - t_max: Amount of simulated time the simulation should run for.
                 Integer.
'''
if __name__ == "__main__":
    queue_structure = sys.argv[1]
    m = int(sys.argv[2])
    n = int(sys.argv[3])
    t_max = int(sys.argv[4])

    if queue_structure != "fifo" and queue_structure != "lru":
        raise ValueError('Unsupported cache structure provided.')
    if n < m:
        print("This seems like a pointless exercise...")    

    simulate(n, m, t_max)
