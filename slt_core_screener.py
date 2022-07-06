# librairies import
import pandas as pd
import numpy as np
import certifi
import json
from urllib.request import urlopen

# disable warnings
import warnings

warnings.filterwarnings("ignore")


def get_jsonparsed_data(url):
    """
    Receive the content of ``url``, parse it as JSON and return the object.

    Parameters
    ----------
    url : str

    Returns
    -------
    dict
    """
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)


## INPUT ##

personal_api_key = "YOUR_API_KEY"  # to update with personal api key.
tickers = ["MSFT", "AAPL", "TSLA", "PFE"]  # to change with relevant tickers list.

## QUALITY GROWTH METRICS ##

# dataframe initialization
ratios = [
    "Operating Profit Margin",
    "Net Profit Margin",
    "ROA",
    "ROE",
    "ROCE",
    "Current Ratio",
    "Debt/Equity Ratio",
    "Debt/Assets Ratio",
    "FCF Yield",
    "5Y Revenue Growth",
    "5Y CFO Growth",
    "5Y EPS Growth",
]  # quality and growth ratios.

df = pd.DataFrame(index=ratios, columns=tickers)

# collection and storage in a dataframe of the above ratios for each stock in the tickers list.
for ticker in tickers:

    try:

        # Fimancial Modeling Prep API requests - key quality growth ratios
        cfr = get_jsonparsed_data(
            "https://financialmodelingprep.com/api/v3/ratios-ttm/"
            + ticker
            + "?apikey="
            + personal_api_key
        )  ## Company Financial Ratios
        ckm = get_jsonparsed_data(
            "https://financialmodelingprep.com/api/v3/key-metrics-ttm/"
            + ticker
            + "?apikey="
            + personal_api_key
        )  ## Company Key Metrics
        cfg = get_jsonparsed_data(
            "https://financialmodelingprep.com/api/v3/financial-growth/"
            + ticker
            + "?apikey="
            + personal_api_key
        )  ## Company Financial Growth

    except:
        pass

    try:

        ## grouping ratios from different requests into one single dataframe.

        # storage of collected ratios from the Company Financial Ratios request
        df.loc["Operating Profit Margin"][ticker] = cfr[0]["operatingProfitMarginTTM"]
        df.loc["Net Profit Margin"][ticker] = cfr[0]["netProfitMarginTTM"]
        df.loc["ROA"][ticker] = cfr[0]["returnOnAssetsTTM"]
        df.loc["ROE"][ticker] = cfr[0]["returnOnEquityTTM"]
        df.loc["ROCE"][ticker] = cfr[0]["returnOnCapitalEmployedTTM"]

        # storage of collected ratios from the Company Key Metrics request
        df.loc["Current Ratio"][ticker] = ckm[0]["currentRatioTTM"]
        df.loc["Debt/Equity Ratio"][ticker] = ckm[0]["debtToEquityTTM"]
        df.loc["Debt/Assets Ratio"][ticker] = ckm[0]["debtToAssetsTTM"]
        df.loc["FCF Yield"][ticker] = ckm[0]["freeCashFlowYieldTTM"]

        # storage of collected ratios from the Company Financial Growth request.
        df.loc["5Y Revenue Growth"][ticker] = cfg[0]["fiveYRevenueGrowthPerShare"]
        df.loc["5Y CFO Growth"][ticker] = cfg[0]["fiveYOperatingCFGrowthPerShare"]
        df.loc["5Y EPS Growth"][ticker] = cfg[0]["fiveYNetIncomeGrowthPerShare"]

    except:
        pass

df = df.T.fillna(0)  ## dataframe with required quality and growth metrics.

## QUALITY GROWTH SCORE ##

# scoring based on metric levels compared to  group quartiles.
high = [
    "Operating Profit Margin",
    "Net Profit Margin",
    "ROA",
    "ROE",
    "ROCE",
    "Current Ratio",
    "FCF Yield",
    "5Y Revenue Growth",
    "5Y CFO Growth",
    "5Y EPS Growth",
]  ## higher is the best
low = ["Debt/Equity Ratio", "Debt/Assets Ratio"]  ## lower is the best

# dictionary initialization to store results of the scoring
results = dict.fromkeys(df.index, 0)

# scoring calclation for all tickers in the index.
# calculation of a sub-score for each ratio.
# sub-scores are added up together to compute the global score of a company.
# the process is repeated for all the tickers in the list.

for ticker in df.index:
    for col in high:

        if df[col][ticker] <= df[col].quantile(0.25):
            results[ticker] += 1
        elif df[col][ticker] <= df[col].quantile(0.5):
            results[ticker] += 2
        elif df[col][ticker] <= df[col].quantile(0.75):
            results[ticker] += 3
        else:
            results[ticker] += 4

    for col in low:
        if df[col][ticker] >= df[col].quantile(0.75):
            results[ticker] += 1
        elif df[col].quantile(0.75) > df[col][ticker] >= df[col].quantile(0.5):
            results[ticker] += 2
        elif df[col].quantile(0.5) > df[col][ticker] >= df[col].quantile(0.25):
            results[ticker] += 3
        else:
            results[ticker] += 4

# converting into a dataframe and sorting values from highest to lowest.
qualitygrowth_score = pd.DataFrame(
    results.items(), columns=["Ticker", "QG Score"]
).sort_values(by="QG Score", ascending=False)
qualitygrowth_score = qualitygrowth_score.set_index("Ticker")
# print(qualitygrowth_score)

## ESG METRICS ##

esg_scores = [
    "Environment Score",
    "Social Score",
    "Governance Score",
]  # E, S, and G scores used to compute global ESG score.
df = pd.DataFrame(index=esg_scores, columns=tickers)

# collection and storage in a dataframe of the above scores for each stock in the tickers list.
for ticker in tickers:

    try:

        # Fimancial Modeling Prep API requests - ESG data
        esg = get_jsonparsed_data(
            "https://financialmodelingprep.com/api/v4/esg-environmental-social-governance-data?symbol="
            + ticker
            + "&apikey="
            + personal_api_key
        )

    except:
        pass

    try:

        # storage of collected scores.
        df.loc["Environment Score"][ticker] = esg[0]["environmentalScore"]
        df.loc["Social Score"][ticker] = esg[0]["socialScore"]
        df.loc["Governance Score"][ticker] = esg[0]["governanceScore"]

    except:
        pass

df = df.T.fillna(0)  ## dataframe with ESG scores

## ESG SCORE ##

# dictionary initialization to store results of the scoring
results = dict.fromkeys(df.index, 0)

# scoring calclation for all tickers in the ESG dataframe.

for ticker in df.index:
    for col in df.columns:

        if df[col][ticker] <= df[col].quantile(0.33):
            results[ticker] += -1
        elif df[col].quantile(0.33) < df[col][ticker] <= df[col].quantile(0.66):
            results[ticker] += 0
        else:
            results[ticker] += 1

# converting into a dataframe and sorting values from highest to lowest.
esg_score = pd.DataFrame(results.items(), columns=["Ticker", "ESG Score"]).sort_values(
    by="ESG Score", ascending=False
)
esg_score = esg_score.set_index("Ticker")
# print(esg_score)

## EARNINGS SURPRISE METRICS ##

metrics = [
    "Earnings Surprise L5Y Average",
    "Earnings Surprise Standard Deviation",
]  # earnings surprise metrics to be calculated.

df = pd.DataFrame(index=metrics, columns=tickers)

for ticker in tickers:

    try:

        # Fimancial Modeling Prep API requests - All availabke realised quarterly earnings and consensus estimates.
        surprise = get_jsonparsed_data(
            "https://financialmodelingprep.com/api/v3/earnings-surprises/"
            + ticker
            + "?apikey="
            + personal_api_key
        )

    except:
        pass

    try:

        # earnings beat/miss as a percentage calcualtion for the last 20 quarters (4 * 5 years)
        results = []
        i = 0
        while i < 20:
            results.append(
                surprise[i]["actualEarningResult"] / surprise[i]["estimatedEarning"] - 1
            )
            i = i + 1

    except:
        pass

    try:

        # calculation and storage of earnings beat/miss mean and std.
        df.loc["Earnings Surprise L5Y Average"][ticker] = np.mean(results)
        df.loc["Earnings Surprise Standard Deviation"][ticker] = np.std(results)

    except:
        pass

df = df.T.fillna(0)

## EARNINGS SURPRISE SCORE ##

# dictionary initialization to store results of the scoring
results = dict.fromkeys(df.index, 0)

# scoring calclation for all tickers in the index.
# calculation of a sub-scores for both metrics.
# earnings surprise average: from -2 (worst 5Y average quartile) to +2 (best 5Y average quartile)
# earnings surprise std: from -1 (highest std quartile) to +1 (lowest std quartile)

for ticker in df.index:

    if df["Earnings Surprise L5Y Average"][ticker] <= df[
        "Earnings Surprise L5Y Average"
    ].quantile(0.25):
        results[ticker] += -2
    elif df["Earnings Surprise L5Y Average"][ticker] <= df[
        "Earnings Surprise L5Y Average"
    ].quantile(0.5):
        results[ticker] += -1
    elif df["Earnings Surprise L5Y Average"][ticker] <= df[
        "Earnings Surprise L5Y Average"
    ].quantile(0.75):
        results[ticker] += 1
    else:
        results[ticker] += 2

    if df["Earnings Surprise Standard Deviation"][ticker] <= df[
        "Earnings Surprise Standard Deviation"
    ].quantile(0.33):
        results[ticker] += 1
    elif (
        df["Earnings Surprise Standard Deviation"].quantile(0.33)
        < df["Earnings Surprise Standard Deviation"][ticker]
        <= df["Earnings Surprise Standard Deviation"].quantile(0.66)
    ):
        results[ticker] += 0
    else:
        results[ticker] += -1

earnings_score = pd.DataFrame(
    results.items(), columns=["Ticker", "Earnings Surprise Score"]
).sort_values(by="Earnings Surprise Score", ascending=False)
earnings_score = earnings_score.set_index("Ticker")
# print(earnings_score)


## FINAL SCORE ##

final_score = pd.merge(
    pd.merge(qualitygrowth_score, esg_score, on="Ticker"), earnings_score, on="Ticker"
)
final_score["Final Score"] = (
    final_score["QG Score"]
    + final_score["ESG Score"]
    + final_score["Earnings Surprise Score"]
)
print(final_score.sort_values(by="Final Score", ascending=False))
