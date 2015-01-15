#include <systemc.h>
#include <iostream>
#include <string>
#include "${MODULE_HEADER}"

using namespace std;

// clock period for the test clock
#define   CLOCK_CYCLE   sc_time(10, SC_NS)

class ${TESTBENCH_NAME} : public sc_module
{
  SC_HAS_PROCESS(${TESTBENCH_NAME});

public:  
  ${TESTBENCH_NAME}(sc_module_name name) : 
    sc_module(name), uut("uut"), clk("clk", CLOCK_CYCLE)
  {
    // TODO handle FIFOs
    
    // connect input drivers
${CONNECT_INPUT_DRIVERS}
    // connect output monitors
${CONNECT_OUTPUT_MONITORS}
    
    // declare run_tests as SystemC thread
    SC_THREAD(run_tests);
  }
  
  // initialize the driving signals for the uut inputs
  void init_drivers()
  {
${INIT_INPUT_DRIVERS}
  }
  
  // reset system if needed
  void reset_system()
  {
${RESET_CODE}
  }
  
  void run_tests()
  {
    // initialize input drivers
    init_drivers();
    reset_system();
    cout << "Reset completed at " << sc_time_stamp() << ", starting tests..." << endl;
    // TODO insert test code here
    
  }
  
  sc_clock clk;
  
  // instance for the module being tested
  ${MODULE_NAME} uut;
  
  // signals for manipulating the module
${INPUT_DRIVERS}
${OUTPUT_MONITORS}
  
};

int sc_main(int argc, char *argv[])
{
  ${TESTBENCH_NAME} tb("tb");
  
  sc_start();
  
  return 0;
}
