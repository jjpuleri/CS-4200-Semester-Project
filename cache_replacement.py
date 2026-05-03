#------------------------------------------------------------
#CS 4200 - Computer Architecture
# Jason Puleri
#Semester Project: Cache Replacement Policies Comparison

#This program simulates a cache and compares three replacement policies:
# - Least Recently Used (LRU)
# - First In First Out (FIFO)
# - and Random Replacement

#Based on lecture slides: Lectures 23 & 24 - Memory + Cache
#------------------------------------------------------------


#------------------------------------------------------------
import random
from collections import deque, OrderedDict
#------------------------------------------------------------


#------------------------------------------------------------
#Cache Base Class
#------------------------------------------------------------
class Cache:
    """
    Base class for a set associative cache simulator
    Each cache has a fixed number of blocks/ways
    All three policies (LRU, FIFO, Random) will share the same hit/miss tracking
    
    Slides Refernced:
    - slide 38: "Hit -> Data found in cache | Miss -> Data fetched from memory"
    - slide 44: Tag field stores upper address bits and is used for comparison
    - slide 45: Valid bit: 0 = inlvaid, 1 = valid
    """

    def __init__(self, cache_size):
        self.cache_size = cache_size
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def access(self, address):
        """
        To be implemented by subclasses to simulate cache access and update hit/miss counts
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def hit_rate(self):
        """
        Calculate and return the hit rate as a percentage
        """
        total_accesses = self.hits + self.misses
        if total_accesses == 0:
            return 0.0
        return (self.hits / total_accesses) * 100
    
    def miss_rate(self):
        """
        Calculate and return the miss rate as a percentage
        """
        total_accesses = self.hits + self.misses
        if total_accesses == 0:
            return 0.0
        return (self.misses / total_accesses) * 100
    
    def stats(self):
        """
        Print the cache statistics: hits, misses, evictions, hit rate, and miss rate
        """
        total_accesses = self.hits + self.misses
        print(f"Total Accesses: {total_accesses}")
        print(f"Hits: {self.hits}")
        print(f"Misses: {self.misses}")
        print(f"Evictions: {self.evictions}")
        print(f"Hit Rate: {self.hit_rate():.2f}%")
        print(f"Miss Rate: {self.miss_rate():.2f}%")


#------------------------------------------------------------
#LRU Cache
#------------------------------------------------------------
class LRUCache(Cache):
    """
    Least Recently Used (LRU) relacement policy implementation
    When the cache is full, the block that was used least recently will be evicted to make room for the new block

    this exploits temoral locality, as recently accessed data is more likely to be accessed again soon
    Slides Referenced:
    - slide 36: "Temporal -> reuse data"

    Implemntation uses an OrderedDict to maintain the order of access, where the most recently accessed item is moved to the end of the dictionary
    Moving an item to the end of the OrderedDict simulates it being the most recently used, while the least recently used item will be at the beginning of the dictionary
    """

    def __init__(self, cache_size):
        super().__init__(cache_size)
        self.cache = OrderedDict()

    def access(self, address):
        if address in self.cache:
            #Hit: Move the accessed address to the end to mark it as most recently used
            self.cache.move_to_end(address)
            self.hits += 1
        else:
            #Miss: Add the new address to the cache
            self.misses += 1
            if len(self.cache) >= self.cache_size:
                #Evict the least recently used item (the first item in the OrderedDict)
                self.cache.popitem(last=False)
                self.evictions += 1
            self.cache[address] = True


#------------------------------------------------------------
#FIFO Cache
#------------------------------------------------------------
class FIFOCache(Cache):
    """
    First In First Out (FIFO) replacement policy 
    the block that has been in the cache the longest (the first one added) will be evicted when the cache is full, regardless of how recently it was accessed
    FIFO does not give credit for re-use, unlike LRU. It simply evicts the oldest block in the cache when a new block needs to be added and the cache is full.
    This uses a deque (double-ended queue) in order to maintain the order of addresses in the cache, where new addresses are added to the end and evictions occur from the front of the deque
    """

    def __init__(self, cache_size):
        super().__init__(cache_size)
        self.cache = set()
        self.order = deque()

    def access(self, address):
        if address in self.cache:
            #Hit: FIFO does not update the order on a hit 
            self.hits += 1
        else:
            #Miss: Add the new address to the cache
            self.misses += 1
            if len(self.cache) >= self.cache_size:
                #Evict the oldest item (the first item in the deque)
                oldest_address = self.order.popleft()
                self.cache.remove(oldest_address)
                self.evictions += 1
            self.cache.add(address)
            self.order.append(address)


#------------------------------------------------------------
#Random Cache
#------------------------------------------------------------
class RandomCache(Cache):
    """
    Random Replacement policy
    When the cache is full, a random block will be evicted to make room for the new block
    """

    def __init__(self, cache_size, seed=42):
        super().__init__(cache_size)
        self.cache =[] 
        self.cache_set = set()
        random.seed(seed)  

    def access(self, address):
        if address in self.cache_set:
            #Hit: Address is already in the cache
            self.hits += 1
        else:
            #Miss: Add the new address to the cache
            self.misses += 1
            if len(self.cache) >= self.cache_size:
                evict_index = random.randint(0, self.cache_size - 1)
                evicted_address = self.cache[evict_index]
                self.cache_set.remove(evicted_address)
                self.cache[evict_index] = address
                self.evictions += 1
            else:
                self.cache.append(address)
            self.cache_set.add(address)


#------------------------------------------------------------
#Memory Access Trace Generator
#------------------------------------------------------------
def generate_memory_trace(num_accesses, address_space):
    """
    Generate a list of random memory addresses to simulate memory accesses
    num_accesses: number of memory accesses to generate
    address_space: the range of possible memory addresses
    """
    return [i % address_space for i in range(num_accesses)]

def generate_looping_trace(num_accesses, address_space, loop_size):
    """
    looping pattern: repeatedly access a small set of addresses to simulate temporal locality
    Slides Referenced:
    - slide 36: "Temporal -> reuse data"
    """
    trace = []
    for i in range(num_accesses):
        trace.append((i % loop_size) % address_space)
    return trace

def generate_random_trace(num_accesses, address_space):
    """
    random pattern: access addresses in a completely random order to simulate no locality
    """
    seed = 7
    random.seed(seed)
    return [random.randint(0, address_space - 1) for _ in range(num_accesses)]

def generate_mixed_trace(num_accesses, address_space, loop_size):
    """
    mixed pattern: combine looping and random patterns to simulate a more realistic access pattern with some locality
    """
    trace = []
    for i in range(num_accesses):
        if i % 10 < 7:  #70% of accesses are from the looping pattern
            trace.append((i % loop_size) % address_space)
        else:  #30% of accesses are random
            trace.append(random.randint(0, address_space - 1))
    return trace


#------------------------------------------------------------
#Run Simulation
#------------------------------------------------------------
def run_simulation(cache_size, trace, label=""):
    """
    Run all three replacement polices on the same trace and cache size, and print the results
    Slides Referenced:
    - slide 46: cache lookup: use index -> comapre tag -> check valid bit -> hit/miss
    - sldie 74: "Memory stall cycles = Miss Rate * Miss Penalty"
    """
    print(f"\n{'='*56}")
    print(f"Simulation: {label}")
    print(f"Cache Size: {cache_size} blocks")
    print(f"Trace size: {len(trace)} accesses")
    print(f"{'='*56}")

    policies = [
        ("LRU", LRUCache(cache_size)),
        ("FIFO", FIFOCache(cache_size)),
        ("Random", RandomCache(cache_size))
    ]

    for name, cache in policies:
        for address in trace:
            cache.access(address)
        print(f"\nPolicy: {name}")
        cache.stats()

    return policies

def print_summary(all_results):
    """
    Print a summary of the results for all simulations, comparing the hit rates and miss rates across different policies and traces
    """
    print(f"\n{'='*56}")
    print("Summary of Results")
    print(f"{'='*56}")
    header = f" {'Simulation':<28} {'Policy':<7} {'Hit Rate':<7} {'Miss Rate':<7}"
    print(header)
    print(f"{'-'*56}")

    for label, policies in all_results:
        lru_hr = f"{policies[0][1].hit_rate():.1f}%"
        fifo_hr = f"{policies[1][1].hit_rate():.1f}%"
        random_hr = f"{policies[2][1].hit_rate():.1f}%"
        print(f" {label: <28} {lru_hr:>7} {fifo_hr:>7} {random_hr:>7}")
    
    print (f"{'='*56}")


#------------------------------------------------------------
#Main
#------------------------------------------------------------
def main():
    print("\nCS 4200 - Computer Architecture")
    print("Jason Puleri")
    print("Semester Project: Cache Replacement Policies Comparison")

    #Simulation Parameters
    #number of blocks in the cache
    cache_size = 8
    #number of unique memory addresses
    address_space = 32
    #number of memory accesses in each trace
    num_accesses = 200

    #Define expierments
    experiments = [
        ("Sequential",
            generate_memory_trace(num_accesses, address_space)),
        ("Looping",
            generate_looping_trace(num_accesses, address_space, loop_size=6)),
        ("Random",
            generate_random_trace(num_accesses, address_space)),
        ("Mixed",
            generate_mixed_trace(num_accesses, address_space, loop_size=8))
    ]

    all_results = []

    for label, trace in experiments:
        policies = run_simulation(cache_size, trace, label)
        all_results.append((label, policies))

    label_small = "Mixed (cache size = 4)"
    trace_small = generate_mixed_trace(num_accesses, address_space, loop_size=8)
    policies_small = run_simulation(cache_size=4, trace=trace_small, label=label_small)
    all_results.append((label_small, policies_small))

    #Print summary of results
    print_summary(all_results)

    print("\nEnd of Simulation")

if __name__ == "__main__":
    main()
