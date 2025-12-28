# Tips on how to use cursor effectively

* use words like "short" "succinct" "sketch" "lightning" 
* Start with developing and debugging a plan, rather than jumping directly into the code.
* Edit the plan when you find problems with the code
  - ask agent to check for inconsistencies and completeness in the plan.
  - when you are both happy with the plan regenerate code.
  
* Use notebooks for exploration, not for code that would be used long term.
* When developing code, partition the task into smaller generic modules that can be combined in many ways.
  - Most of the time cursor would find the modules it needs to use automatically but it can sometimes help to give it a hint.
* When there are errors in a notebook or code:
  - Ask agent to fix them
  - use ask mode to ask why things are not working / What lines in the
    code cause the error.
* after the module runs without errors, ask cursor to generate a test
  for it, ask for the test to report coverage.
* ask for a readme file for the module, this is useful both for
  running the tests, and later, if the tests pass. As a reference for
  how to use the module (argparse parameters)
* Argparse parameter can also be inferred by running the module with the flag -h.


* use <cmd>-K to focus your desired change to a particular part of the code.
* When having problems with time-performance / memory overflow /
  segmentation fault, ask agent to create several variants,
  implemented in separate .py files) that solve the problem in
  different ways and select the one that performs best.
* 
