# pycing-present
This page is for presenting data and source code of PyCing experiments.
All the statistics are in the file **experiment data.xlsx**.

We will first present the source code of PyCing, and then list the leaks detected by PyCing. 


## Source code of PyCing
As described in the paper, PyCing includes a Python bytecode-based static analyzer and a StruCon-based fuzzer. 
The code for the analyzer is at directory **LocateFunction**, and the fuzzer is at directory **GenOnBack**.
In addition, the code in directory **TestcaseExtraction** is for extracing test cases from the project source code.

#### Workflow
In our experiments, we first use code in directory **TestcaseExtraction** to get test cases, then run code in directory **LocateFunction** to store the methods and input data. 
To explore execution paths, we run the code in directory **GenOnBack** and save the explored results.

## Detection of Memory Leaks
https://bugs.python.org/issue44608

https://github.com/numpy/numpy/issues/19400

https://github.com/numpy/numpy/issues/19397

https://github.com/matplotlib/matplotlib/issues/20641

https://github.com/scipy/scipy/issues/14401

https://github.com/scipy/scipy/issues/14400

https://github.com/numpy/numpy/issues/19395

https://github.com/scipy/scipy/issues/14383