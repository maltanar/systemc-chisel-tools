#!/usr/bin/python

# A simple Python script for extracting input and output ports from a SystemC
# module definition.
# The intended use case for the script is to be part of an automated testbench
# skeleton generator for testing Chisel components in SystemC.
# Since there currently is no Chisel SystemC backend, Verilog is generated via
# the Chisel Verilog backend, which is then passed through Verilator to 
# generate SystemC code. The module header file (VSomething.h) is the target
# for this particular script.

# There is also some preliminary support for extracting Decoupled interfaces,
# e.g those that consist of ready-valid-bits signals. These can be connected
# to SystemC FIFO types (sc_fifo<x>) through simple adapters.

# Contact: Yaman Umuroglu <yamanu@idi.ntnu.no>

import re

# TODO get module filename from command line
moduleheader="VFrontendController.h"

with open(moduleheader, "r") as myfile:
    moduledata=myfile.read()

# extract lines containin sc_in and sc_out expressions    
inputSignalMatches = re.findall( r'sc_in<.*>.*;', moduledata, re.M)
outputSignalMatches = re.findall( r'sc_out<.*>.*;', moduledata, re.M)

inputSignals = []
outputSignals = []

# extract the port names and types from the lines
for s in inputSignalMatches:
    match = re.match( r'sc_in<(.*)>\s(.*);', s)
    inputSignals += [(match.group(2), match.group(1))]

for s in outputSignalMatches:
    match = re.match( r'sc_out<(.*)>\s(.*);', s)
    outputSignals += [(match.group(2), match.group(1))]


inputSignals = dict(inputSignals)
outputSignals = dict(outputSignals)

# TODO fill in SystemC testbench template for
# - instantiating the component
# - instantiating the signals to drive I/O
# - connecting the I/O ports to the instantiated signals
# - add main testbench SystemC thread code that inits outputs to 0

# extract candidates for decoupled interfaces
inputValidMatches = re.findall( r'sc_in<bool>.*valid;', moduledata, re.M)
outputValidMatches = re.findall( r'sc_out<bool>.*valid;', moduledata, re.M)

# see if all three decoupled signal types are present
inputFIFONames = []
outputFIFONames = []

for s in inputValidMatches:
    match = re.match( r'sc_in<bool>\s(.*)_valid;', s)
    fifoName = match.group(1)
    if fifoName+"_bits" in inputSignals and fifoName+"_ready" in outputSignals:
        inputFIFONames += [fifoName]
    else:
        print "some FIFO signals for " + fifoName + " not found!"


for s in outputValidMatches:
    match = re.match( r'sc_out<bool>\s(.*)_valid;', s)
    fifoName = match.group(1)
    if fifoName+"_bits" in outputSignals and fifoName+"_ready" in inputSignals:
        outputFIFONames += [fifoName]
    else:
        print "some FIFO signals for " + fifoName + " not found!"

# TODO fill in SystemC testbench code that instantiates sc_fifo's and
# appropriate adapters for connecting to a ready/valid/bits interface