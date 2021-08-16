import pandas as pd

x = pd.DataFrame({'a':[1,1,3,3],'b':[3,3,5,5]},index=[11,11,12,12])
y = x.stack()
print(y)
print(y.groupby(level=[0,1]).sum())

