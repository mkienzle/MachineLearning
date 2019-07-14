# Machine Learning Sandbox - Comparing Different Classification Solutions

## Why this project

This project contains scripts to generate jpg images containing dots, lines and other geometric features. Your goal is to develop code that can accurately count these geometric features. You are encouraged to contribute your solution to this repo for the benefit of other developers.  

## How to contribute a solution

You will need:

 * R installed with packages plotrix, optparse

### Generate the training dataset

```
cd Scripts/ProduceSyntheticData
Rscript DrawDots.R
```

### Generate the test dataset

[TO DO]


### Submit your solution

 1. Fork this repo
 2. Put your solution under directory Y/X where X is a name of your choice. Provide a README.md file that describes yopur solution, the software dependencies and how to install them, and a step by step description on how to run your solution. Use template Z as an example.
 3. Create a pull request

## How solutions are evaluated

The best solution has the lowest variance = sum (num of circles detected - number of circles)^2

## FAQs







 