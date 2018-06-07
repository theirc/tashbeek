import pandas as pd
import statsmodels.api as sm
from sklearn import cross_validation

independent_vars = phy_train.columns[3:]
X_train, X_test, y_train, y_test = cross_validation.train_test_split(
        phy_train[independent_vars], 
        phy_train['target'], 
        test_size=0.3, 
        random_state=0
)

X_train = pd.DataFrame(X_train)
X_train.columns = independent_vars

X_test = pd.DataFrame(X_test)
X_test.columns = independent_vars

y_train = pd.DataFrame(y_train)
y_train.columns = ['target']

y_test = pd.DataFrame(y_test)
y_test.columns = ['target']

logit = sm.Logit(y_train,X_train[subset],missing='drop')
result = logit.fit()

print(result.summary())
