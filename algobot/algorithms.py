import math
from typing import Dict, List, Tuple, Union

import numpy as np

from algobot.helpers import get_data_from_parameter


def get_wma(data: List[Dict[str, float]], prices: int, parameter: str, desc: bool = True) -> float:
    """
    Calculates the weighted moving average from data provided.
    The data is assumed to be in descending order - meaning newer dates are in the front of the list.
    :param desc: Order data is in. If descending, this will be true, else false.
    :param data: Data to calculate weighted moving average.
    :param prices: Periods of data to get weighted moving average.
    :param parameter: Parameter from data dictionary with which to get the weighted moving average.
    :return: Weighted moving average.
    """
    if desc:
        total = get_data_from_parameter(data=data[0], parameter=parameter) * prices
        data = data[1:]

        index = 0
        for x in range(prices - 1, 0, -1):
            total += x * get_data_from_parameter(data=data[index], parameter=parameter)
            index += 1
    else:
        total = get_data_from_parameter(data=data[-1], parameter=parameter) * prices
        data = data[:-1]

        for index, data in enumerate(data, start=1):
            total += index * get_data_from_parameter(data, parameter)

    divisor = prices * (prices + 1) / 2
    wma = total / divisor
    return wma


def get_sma(data: List[Dict[str, float]], prices: int, parameter: str) -> float:
    """
    Calculates the simple moving average from data provided.
    :param data: Data to calculate simple moving average.
    :param prices: Periods of data to get simple moving average.
    :param parameter: Parameter from data dictionary with which to get the simple moving average.
    :return: Simple moving average.
    """
    return sum([get_data_from_parameter(data=period, parameter=parameter) for period in data]) / prices


def get_ema(data: List[dict], prices: int, parameter: str, sma_prices: int, memo: dict = None, desc: bool = True) -> \
        Tuple[float, dict]:
    """
    Calculates the exponential moving average from data provided.
    The data is assumed to be in descending order - meaning newer dates are in the front of the list.
    :param desc: Order data is in. If descending, this will be true, else false.
    :param data: Data to calculate exponential moving average.
    :param prices: Periods to data to get exponential moving average.
    :param parameter: Parameter from data dictionary with which to get the exponential moving average.
    :param sma_prices: Initial SMA periods to use to calculate first exponential moving average.
    :param memo: Memoized dictionary containing past exponential moving averages data.
    :return: A tuple containing the exponential moving average and memoized dictionary.
    """
    multiplier = 2 / (prices + 1)

    if memo and prices in memo and parameter in memo[prices]:
        index = 0 if desc else -1
        current_price = get_data_from_parameter(data[index], parameter)
        if memo[prices][parameter][-1][1] == data[index]['date_utc']:
            previous_ema = memo[prices][parameter][-2][0]
            ema = current_price * multiplier + previous_ema * (1 - multiplier)
            memo[prices][parameter][-1][0] = ema
        elif memo[prices][parameter][-1][1] < data[index]['date_utc']:
            previous_ema = memo[prices][parameter][-1][0]
            ema = current_price * multiplier + previous_ema * (1 - multiplier)
            memo[prices][parameter].append([ema, data[index]['date_utc']])
        else:
            raise ValueError("Something went wrong in the calculation of the EMA.")
    else:
        if desc:
            sma_data = data[len(data) - sma_prices:]
        else:
            sma_data = data[:sma_prices]

        ema = get_sma(sma_data, sma_prices, parameter)
        if desc:
            values = [[ema, data[len(data) - sma_prices]['date_utc']]]
            data = data[:len(data) - sma_prices][::-1]  # Reverse the data to start from back to front.
        else:
            values = [[ema, data[sma_prices - 1]['date_utc']]]
            data = data[sma_prices:]

        for period in data:
            current_price = get_data_from_parameter(period, parameter=parameter)
            ema = current_price * multiplier + ema * (1 - multiplier)
            values.append([ema, period['date_utc']])

        if not memo:
            memo = {prices: {parameter: values}}
        elif memo and prices not in memo:
            memo[prices] = {parameter: values}
        else:
            memo[prices][parameter] = values

    return ema, memo


def get_rsi():
    pass


# Volume Indicators

def get_accumulation_distribution_indicator(data: Dict[str, float]) -> float:
    """
    Retrieve the accumulation distribution indicator based on open, close, high, low, and volume values.
    :param data: Dictionary containing open, high, close, low, and volume data.
    :return: Accumulation distribution indicator.
    """
    return (data['close'] - data['open']) / (data['high'] - data['low']) * data['volume']


def get_normal_volume_oscillator(periods: int, ad_cache: List[float], data: List[Dict[str, float]]) -> \
        Union[float, None]:
    """
    Gets the normal value oscillator based on the periods, past accumulation distribution indicator values, and volumes.
    :param periods: Number of periods to look previously.
    :param ad_cache: Data containing previous accumulation distribution indicator values.
    :param data: List containing previous periods' data.
    :return: Normal volume oscillator.
    """
    if len(ad_cache) < periods or len(data) < periods:
        return None
    else:
        volumes = [data_period['volume'] for data_period in data[-periods:]]
        ad_values = ad_cache[-periods:]
        return sum(ad_values) / sum(volumes)


def get_intraday_intensity_indicator(data: Dict[str, float]) -> float:
    """
    Returns the intraday intensity indicator based on the data provided.
    :param data: Dictionary containing open, high, close, low, and volume data.
    :return: Intraday intensity indicator.
    """
    return (2 * data['close'] - data['high'] - data['low']) / (data['high'] - data['low']) * data['volume']


def get_normalized_intraday_intensity(periods: int, intraday_intensity_cache: List[float],
                                      data: List[Dict[str, float]]) -> Union[float, None]:
    """
    Returns the normalized intraday intensity value based on the periods, past intraday intensity values, and past
    data period values.
    :param periods: Number of periods to look previously.
    :param intraday_intensity_cache: Cache of previous intraday intensities.
    :param data: List containing previous periods' data.
    :return: Normalized intraday intensity.
    """
    if len(intraday_intensity_cache) < periods or len(data) < periods:
        return None
    else:
        intraday_intensities = intraday_intensity_cache[-periods:]
        volumes = [data_period['volume'] for data_period in data[-periods:]]
        return sum(intraday_intensities) / sum(volumes)


def get_basic_volatility(periods: int, data: List[Dict[str, float]]) -> float:
    """
    Retrieves the basic volatility based on periods and data provided.
    :param periods: Amount of periods to traverse behind for basic volatility.
    :param data: Data to get close values from.
    """
    closes = []
    previous_close = data[-periods - 1]['close']
    for period in data[-periods:]:
        close_average = period['close'] / previous_close - 1
        previous_close = period['close']
        closes.append(close_average)

    return float(np.std(closes, ddof=1))


def get_parkinson_volatility(periods: int, data: List[Dict[str, float]]) -> float:
    """
    Retrieves the Parkinson volatility based on periods and data provided.
    :param periods: Amount of periods to traverse behind for basic volatility.
    :param data: Data to get close values from.
    """
    running_sum = 0
    for period in data[-periods:]:
        calculation = math.log(period['high'] / period['low']) ** 2
        running_sum += calculation

    return math.sqrt(running_sum / (4 * math.log(2) * periods))


def get_gk_volatility(periods: int, data: List[Dict[str, float]]) -> float:
    """
    Retrieves the Garman-Klass (GK) volatility based on periods and data provided.
    :param periods: Amount of periods to traverse behind for basic volatility.
    :param data: Data to get close values from.
    """
    running_sum = 0
    for period in data[-periods:]:
        high = period['high']
        low = period['low']
        close = period['close']
        open_ = period['open']  # open is a Python keyword
        calculation = 0.5 * math.log(high / low) ** 2 + (2 * math.log(2) - 1) * math.log(close / open_) ** 2
        running_sum += calculation

    return math.sqrt(running_sum / periods)


def get_rs_volatility(periods: int, data: List[Dict[str, float]]) -> float:
    """
    Retrieves the Rogers Satchell (RS) volatility based on periods and data provided.
    :param periods: Amount of periods to traverse behind for basic volatility.
    :param data: Data to get close values from.
    """
    running_sum = 0
    for period in data[-periods:]:
        u = math.log(period['high'] / period['open'])
        d = math.log(period['low'] / period['open'])
        c = math.log(period['close'] / period['open'])
        running_sum += u * (u - c) + d * (d - c)

    return math.sqrt(running_sum / periods)


def get_zh_volatility(periods: int, data: List[Dict[str, float]]) -> float:
    """
    Retrieves the Yang Zhang (ZH) volatility based on periods and data provided.
    :param periods: Amount of periods to traverse behind for basic volatility.
    :param data: Data to get close values from.
    """
    close_values = []
    open_values = []
    for period in data[-periods:]:
        o = math.log(period['open'] / period['close'])
        c = math.log(period['close'] / period['open'])
        close_values.append(c)
        open_values.append(o)

    open_std = float(np.std(open_values, ddof=1))
    close_std = float(np.std(close_values, ddof=1))
    k = 0.34 / (1.34 + (periods + 1) / (periods - 1))
    rs_volatility = get_rs_volatility(periods=periods, data=data)

    return math.sqrt(close_std ** 2 + k * open_std ** 2 + (1 - k) * rs_volatility ** 2)
