<div align="center">
  <img src="static/img/final1.png"><br>
</div>

-----------------

# codepulse: Measure Execution Time for Each Line of Code

## What is codepulse?

**codepulse** is a Python package designed to provide detailed insights into the execution time of your code at a granular level, line by line. By meticulously tracking the execution time of each line of code, codepulse helps you identify bottlenecks, optimize performance, and gain a deeper understanding of your code's behavior.

## Table of Contents

- [Main Features](#main-features)
- [Where to get it](#where-to-get-it)
- [Usage](#usage)
- [License](#license)

## Main Features

- Precisely measures the execution time of each line of code within a function.
- Generates informative visualizations that highlight performance hotspots.
- Supports integration with popular Python development environments.
- Designed for ease of use and seamless integration into existing projects.


## Where to get it
The source code is currently hosted on GitHub at: https://github.com/SKR18156592/codepulse


### Usage

Import the Tracker module from the `codepulse` package, create an instance of it by passing the function you want to track as a parameter, and then utilize this instance to invoke the tracked function. When you create an instance using `Tracker(fun1)`, it generates a wrapper around fun1 that effectively measures and records the execution time line by line.

```
from codepulse import Tracker

def fun1(x,y):
    m = 1
    for i in range(x*100):
        m = m * 3 
        for j in range(x*30):
            m = m + 4 
    return m 

t = Tracker(fun1)
t(3,5)
```
output:
```
  ===========================================================================================
  |> Function Name: fun1, #iter: 3, mean_time(in ms): 46.856, std_time(in_ms): 0.019
  ===========================================================================================
  | LineNo     | line                              | mean_time(in ms)     | std_time(in ms) |
  ===========================================================================================
  | 0          |     m = 1                         | 0.0                  | 0.0
  | 1          |     for i in range(x*100):        | 46.856               | 0.024
  | 2          |         m = m * 3                 | 0.0                  | 0.0
  | 3          |         for j in range(x*30):     | 15.673               | 0.003
  | 4          |             m = m + 4             | 15.611               | 0.052
  | 5          |     return m                      | nan                  | nan
  -------------------------------------------------------------------------------------------
```
### License

This project is licensed under the MIT License
