import os
# os.environ["WRDS_USERNAME"] = "gfeng1"
# os.environ["WRDS_PASSWORD"] = "cityu20210612"

import datetime as dt
import famafrench.famafrench as ff


pickled_dir = os.getcwd() + '/pickled_db/'

startDate = dt.date(2007, 1, 1)
endDate = dt.date(2020, 12, 12)
runQuery = True
ffFreq = 'M'
ffsortCharac = ['ME', 'BM']
ffFactors = ['MKT-RF', 'SMB', 'HML', 'RMW', 'CMA']

ff3 = ff.FamaFrench(pickled_dir, runQuery, ffFreq, ffsortCharac, ffFactors)
factorsTableM = ff3.getFFfactors(startDate, endDate)