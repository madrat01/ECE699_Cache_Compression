# ECE699_Cache_Compression

https://gem5.googlesource.com/public/gem5

Usage of cache compression scripts :

build/X86/gem5.opt configs/cache_compression/cache_compression.py <binary> <--llc_size> <--llc_asssoc> <--num_cores>>

Required:
  <binary>
Optional:
  <--llc_size>
  <--llc_assoc>
  <--num_cores>

NOTE: The default cache compression strategy is BDI()
    
Directory structure :

configs/cache_compression/ - Config files
├── cache_compression.py - Config file to simulate binary on gem5
├── caches.py - LLCCache() definition to enable compression and configuration
    
tests/cache_compression/ - Basic test which reads to/writes from an array
├── bin
│   └── small_test
└── src
    └── small_test.c
    
tests/microbench/ - Microbench from https://github.com/darchr/microbench
├── *
│   ├── bench.c
│   ├── desc.txt
│   └── Makefile
    
The above method can be used to run any simple benchmark with cache compression.
    
To run PARSEC:
Follow README gem5-resources/src/parsec/README.md of https://github.com/gem5/gem5-resources
TODO: For cache compression of PARSEC, would need to update gem5-resources/src/parsec/gem5/src/python/gem5/components/cachehierarchies/ruby/ to enable cache compression in ruby caches.
    
