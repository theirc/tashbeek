import numpy as np

from math import sqrt, log, pi
from scipy.optimize import fmin
from scipy.special import erf
from scipy.stats import norm


def stdn_cdf(x):
    return 0.5 * (1 + erf(np.divide(x, sqrt(2))))

def norm_cdf(x, m=None, v=None):
    shape = x.shape
    r = shape[0]
    c = shape[1] if len(shape) > 1 else 1

    if r * c  == 0:
        raise Exception('norm_cdf: x must not be empty')

    if not m:
        m = np.zeros((r, 1))
    if not v:
        v = np.ones((r, 1))

    cdf = np.zeros((r, 1))
    col = stdn_cdf(
        np.divide(
            x.T[0] - m.T[0],
            np.sqrt(v.T[0])
        )
    )
    cdf.T[0] = col

    return cdf


def stdn_pdf(x):
    shape = x.shape
    r = shape[0]
    c = shape[1] if len(shape) > 1 else 1
    s = r * c
    np.reshape(x, (1, s))
    pdf = np.zeros((1, s))

    k = np.where(np.isnan(x))
    if np.any(k):
        pdf[k] = np.nan * ones((1, k.shape[0]))

    k = np.logical_not(np.isinf(x))
    if np.any(k):
        pdf[k] = (2 * np.pi)^(-0.5) * np.exp((-x[k] ** 2) / 2)

    return np.reshape(pdf, (r, c))

def norm_pdf(x, m=None, v=None):
    shape = x.shape
    r = shape[0]
    c = shape[1] if len(shape) > 1 else 1

    if not m and not v:
        m = np.zeros((r, 1))
        v = np.ones((r, 1))

    x1 = x[:r]
    m1 = m[:r]
    v1 = v[:r]

    pdf[::r, 0] = stdn_pdf(
        (x1 - m1) / np.sqrt(v1) / np.sqrt(v1)
    )
    return pdf

def ll(beta, y, x):
    pred_prob = norm_cdf(x * beta)
    loglikelihood = sum(
        np.multiply(
            np.multiply(y, np.log(pred_prob)) + (1 - y),
            np.log(1 - pred_prob)
        )
    )
    sigma = 1
    npdf = norm.pdf(np.divide(beta, sigma))
    loglikelihood = loglikelihood + np.sum(np.log(npdf))
    return loglikelihood[0]

def predicted_probability(y, x):
    guess = np.zeros((x.shape[1], 1))
    betahat = fmin(ll, x0=guess, args=(y, x))
    r = norm.cdf(np.matmul(x, betahat))
    return r
