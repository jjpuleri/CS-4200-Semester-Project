#Test Case File
#CS4200 - Cache Replacement Policy Comparison
#Example cases demonstrate each memory trace type
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from cache_replacement import (
    LRUCache, FIFOCache, RandomCache,
    generate_memory_trace, generate_looping_trace,
    generate_random_trace, generate_mixed_trace
)

#------------------------------------------------------------
#Test 1: verifies LRU evicts correctly
#------------------------------------------------------------
print(f"{'='*56}")
print("Test 1: LRU Eviction")
print(f"{'='*56}")
lru = LRUCache(3)
for addr in [0, 1, 2, 0, 3]:
    lru.access(addr)
lru.stats()

#------------------------------------------------------------
#Test 2: verifies FIFO evicts the oldest entry
#------------------------------------------------------------
print(f"{'='*56}")
print("Test 2: FIFO Eviction")
print(f"{'='*56}")
fifo = FIFOCache(3)
for addr in [0, 1, 2,0, 3]:
    fifo.access(addr)
fifo.stats()   

#------------------------------------------------------------
#Test 3: verifies all policies on a small sequential trace
#------------------------------------------------------------
print(f"{'='*56}")
print("Test 3: Sequential Trace")
print(f"{'='*56}")
# 10 accesses, 5 unique addresses
trace = generate_memory_trace(10, 5)
print(f"Trace: {trace}")
for name, CacheClass in [("LRU", LRUCache), ("FIFO", FIFOCache), ("Random", RandomCache)]:
    print(f"\n{name} Cache:")
    cache = CacheClass(3)
    for addr in trace:
        cache.access(addr)
    cache.stats()

print(f"{'-'*56}")
print("end of test cases")
print(f"{'-'*56}")