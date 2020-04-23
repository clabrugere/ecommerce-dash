import numpy as np
import pandas as pd
from statsmodels.tsa.arima_model import ARIMA


def predict(dates, x, look_ahead):
    
    forecast_start_date = (dates.dt.date.max() + pd.DateOffset(1)).date()
    forecast_end_date = (forecast_start_date + pd.DateOffset(look_ahead - 1)).date()
    forecast_end = 15 + x.shape[0] - 1
    
    model = ARIMA(x, order=(9,0,1))
    model_fit = model.fit(method='css') # conditional sum of squares likelihood is maximized, faster as no Kalmann filter needs to be designed and the full maximum likehood is not computed
    
    predictions, stderr, ci = model_fit.forecast(look_ahead)
    
    predictions = pd.DataFrame({
        'date': pd.date_range(forecast_start_date, forecast_end_date, freq='1D'),
        'forecast': predictions,
        'ci_low': ci[:,0],
        'ci_high': ci[:, 1],
        'stderr': stderr
    })
    
    return predictions