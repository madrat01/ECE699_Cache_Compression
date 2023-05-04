# -*- coding: utf-8 -*-
# Copyright (c) 2015 Jason Power
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" This file creates a single CPU and a two-level cache system.
This script takes a single parameter which specifies a binary to execute.
If none is provided it executes 'hello' by default (mostly used for testing)

See Part 1, Chapter 3: Adding cache to the configuration script in the
learning_gem5 book for more information about this script.
This file exports options for the LLC cache sizes.

IMPORTANT: If you modify this file, it's likely that the Learning gem5 book
           also needs to be updated. For now, email Jason <power.jg@gmail.com>

"""

# import the m5 (gem5) library created when gem5 is built
import m5

# import all of the SimObjects
from m5.objects import *
from gem5.runtime import get_runtime_isa

# Add the common scripts to our path
m5.util.addToPath("../")

# import the caches which we made
from caches import *

# import the SimpleOpts module
from common import SimpleOpts

import argparse

# Default to running 'hello', use the compiled ISA to find the binary
# grab the specific path to the binary
thispath = os.path.dirname(os.path.realpath(__file__))
default_binary = os.path.join(
    thispath,
    "../../",
    "tests/test-progs/hello/bin/x86/linux/hello",
)

# Binary to execute
SimpleOpts.add_option("binary", nargs="?", default=default_binary)
SimpleOpts.add_option("llc_size", nargs="?", default="256kB")
SimpleOpts.add_option("llc_assoc", nargs="?", default="8")
SimpleOpts.add_option("num_cores", nargs="?", default="4")

# Finalize the arguments and grab the args so we can pass it on to our objects
#args = parser.parse_args()
args = SimpleOpts.parse_args()

nc = int(args.num_cores)
# Set up the system
system = System(
    cpu=[X86TimingSimpleCPU(cpu_id=i) for i in range(nc)],
    mem_mode="timing",
    mem_ranges=[AddrRange("512MB")]
)

# Set the clock frequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# Create a memory bus, a coherent crossbar, in this case
system.llcbus = L2XBar()
# Create an L2 cache and connect it to the l2bus
system.llccache = LLCCache(args)
system.llccache.connectCPUSideBus(system.llcbus)

# Create a memory bus
system.membus = SystemXBar()
# Connect the L2 cache to the membus
system.llccache.connectMemSideBus(system.membus)

# All cpus belong to a common cpu_clk_domain, therefore running at a common
# frequency.
for cpu in system.cpu:
    cpu.clk_domain = system.clk_domain

# Create a simple CPU
for i in range(nc) :
    # Create an L1 instruction and data cache
    system.cpu[i].icache = L1ICache()
    system.cpu[i].dcache = L1DCache()

    # Connect the instruction and data caches to the CPU
    system.cpu[i].icache.connectCPU(system.cpu[i])
    system.cpu[i].dcache.connectCPU(system.cpu[i])

    # Hook the CPU ports up to the l2bus
    system.cpu[i].icache.connectBus(system.llcbus)
    system.cpu[i].dcache.connectBus(system.llcbus)

    # create the interrupt controller for the CPU
    system.cpu[i].createInterruptController()
    system.cpu[i].interrupts[0].pio = system.membus.mem_side_ports
    system.cpu[i].interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu[i].interrupts[0].int_responder = system.membus.mem_side_ports
    
    system.cpu[i].createThreads()

# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports

# Create a DDR3 memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

system.workload = SEWorkload.init_compatible(args.binary)

for i in range(nc) :
    # Create a process for a simple "Hello World" application
    process = Process(pid=100 + i)
    # Set the command
    # cmd is a list which begins with the executable (like argv)
    process.cmd = [args.binary]
    # Set the cpu to use the process as its workload and create thread contexts
    system.cpu[i].workload = process

# set up the root SimObject and start the simulation
root = Root(full_system=False, system=system)
# instantiate all of the objects we've created above
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print("Exiting @ tick %i because %s" % (m5.curTick(), exit_event.getCause()))
