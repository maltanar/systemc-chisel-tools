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

import re, sys

def getSignals(templateType, headerData):
    signals = []
    signalMatches = re.findall( templateType + r'<.*>.*;', headerData, re.M)
    for s in signalMatches:
        match = re.match( templateType + r'<(.*)>\s(.*);', s)
        signals += [(match.group(2), match.group(1))]
    signals = dict(signals)
    return signals
    
def getInputSignals(headerData):
    return getSignals(r'sc_in', headerData)

def getOutputSignals(headerData):
    return getSignals(r'sc_out', headerData)

def getInputFIFONames(headerData):
    inputValidMatches = re.findall( r'sc_in<bool>.*valid;', headerData, re.M)
    inputFIFONames = []
    inputSignals=getInputSignals(headerData)
    outputSignals=getOutputSignals(headerData)
    for s in inputValidMatches:
        match = re.match( r'sc_in<bool>\s(.*)_valid;', s)
        fifoName = match.group(1)
        if fifoName+"_bits" in inputSignals and fifoName+"_ready" in outputSignals:
            inputFIFONames += [fifoName]
        else:
            print >> sys.stderr, "some FIFO signals for " + fifoName + " not found!"
    return inputFIFONames

def getOutputFIFONames(headerData):
    outputValidMatches = re.findall( r'sc_out<bool>.*valid;', headerData, re.M)
    outputFIFONames = []
    inputSignals=getInputSignals(headerData)
    outputSignals=getOutputSignals(headerData)
    for s in outputValidMatches:
        match = re.match( r'sc_out<bool>\s(.*)_valid;', s)
        fifoName = match.group(1)
        if fifoName+"_bits" in outputSignals and fifoName+"_ready" in inputSignals:
            outputFIFONames += [fifoName]
        else:
            print >> sys.stderr, "some FIFO signals for " + fifoName + " not found!"    
    return outputFIFONames
    

if len(sys.argv) == 2:
    headerFileName = str(sys.argv[1])
else:
    print >> sys.stderr, "Please specify input header file name."
    sys.exit()

with open(headerFileName, "r") as myfile:
    data=myfile.read()

moduleName = re.findall(r'SC_MODULE\((.*)\)', data, re.M)[0]
inputSignals = getInputSignals(data)
outputSignals = getOutputSignals(data)
inputFIFOs = getInputFIFONames(data)
outputFIFOs = getOutputFIFONames(data)

inputSignalDecls = ""
inputSignalConns = ""
inputSignalInits = ""   # initializers for the input drivers

outputSignalDecls = ""
outputSignalConns = ""

resetCode = ""

# Handle clock driver manually if there is a clk input
if "clk" in inputSignals:
    del inputSignals["clk"]
    inputSignalConns += "    uut.clk(clk);\n"
    resetCode += "    sig_reset = true;\n"
    resetCode += "    wait(10*CLOCK_CYCLE);\n"
    resetCode += "    sig_reset = false;\n"

for sigName in inputSignals:
    sigType = inputSignals[sigName]
    inputSignalDecls += "  sc_signal<" + sigType + "> sig_"+sigName+";\n"
    inputSignalConns += "    uut." + sigName + "(sig_" + sigName + ");\n"
    inputSignalInits += "    sig_" + sigName + " = 0;\n"

for sigName in outputSignals:
    sigType = outputSignals[sigName]
    outputSignalDecls += "  sc_signal<" + sigType + "> sig_"+sigName+";\n"
    outputSignalConns += "    uut." + sigName + "(sig_" + sigName + ");\n"




# Load the template
with open("testbench-template/testbench.cpp", "r") as templateFile:
    templateData = str(templateFile.read())

# Add module header #include
templateData=templateData.replace("${MODULE_HEADER}", moduleName+".h")

# Module name
templateData=templateData.replace("${MODULE_NAME}", moduleName)

# Testbench name
templateData=templateData.replace("${TESTBENCH_NAME}", "Test"+moduleName)

# Signal declarations
templateData=templateData.replace("${INPUT_DRIVERS}", inputSignalDecls)
templateData=templateData.replace("${OUTPUT_MONITORS}", outputSignalDecls)

# Signal connections
templateData=templateData.replace("${CONNECT_INPUT_DRIVERS}", inputSignalConns)
templateData=templateData.replace("${CONNECT_OUTPUT_MONITORS}", outputSignalConns)

# Init input drivers
templateData=templateData.replace("${INIT_INPUT_DRIVERS}", inputSignalInits)

# Reset code
templateData=templateData.replace("${RESET_CODE}", resetCode)

print templateData

# TODO fill in SystemC testbench code that instantiates sc_fifo's and
# appropriate adapters for connecting to a ready/valid/bits interface