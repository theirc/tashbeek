import numpy as np

from math import sqrt, log, pi
from scipy.optimize import fmin
from scipy.special import erf
from scipy.stats import norm

def ll(beta, y, x):
    pred_prob = norm_cdf(np.matmul(x, beta))

    s = np.multiply(y, np.log(pred_prob)) + np.multiply((1 - y), np.log(1 - pred_prob))

    loglikelihood = np.sum(
        s
    )

    print(loglikelihood)
    print(s)
    sigma = 1
    npdf = norm.pdf(np.divide(beta, sigma))
    loglikelihood = loglikelihood + np.sum(np.log(npdf))
    return loglikelihood

def predicted_probability(y, x):
    guess = np.zeros((x.shape[1], 1))
    betahat = fmin(ll, x0=guess, args=(y, x))
    r = norm.cdf(np.matmul(x, betahat))
    return r
