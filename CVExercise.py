# % SimulateCVs
from est_predicted_prob import predicted_probability
import numpy as np

from numpy.random import randn
from numpy.matlib import repmat
from scipy.stats import norm

from matplotlib import pyplot

def main():
    K = 5;
    Respondents = 1;
    Options = 50;

    # %% First, draw parameters...

    Params = randn(Respondents, K)
    ID = 1
    BigParams = repmat(Params, Options, 1)
    BigID = repmat(ID, Options, 1)


    # %% Second, draw data...
    x = randn(Respondents * Options, K)
    x[:, 0] = 1

    # %% Third, simulate the outcome...
    xhat = np.sum(np.multiply(x, BigParams), axis=1)
    trueprob = norm.cdf(xhat)
    epsilon = randn(Respondents * Options, 1)

    y = (xhat + epsilon >= 0)

    # %% Fourth, estimate...
    predprob = np.empty((Respondents * Options, 1))
    predprob[:] = np.nan

    for count in range(Respondents):
        yy = y[count]
        xx = x
        newprob = predicted_probability(
            yy,
            xx
        )
        predprob = newprob

    pyplot.scatter(trueprob, predprob)
    pyplot.show()

if __name__ == '__main__':
    with np.errstate(all="raise"):
        main()
