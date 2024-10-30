import pytest

from src.statistics import AggregatedStatistic, Statistics

def make_stat(test_prices: list[float], test_volumes: list[int]) -> Statistics:
    test_date = '2024-11-01'
    tes_time = '10:15:29'
    test_ticker = "ticker_X"
    assert len(test_prices) == len(test_volumes)

    test_records: list[tuple] = list()
    for i in range(0, len(test_prices)):
        test_records.append(
            (test_prices[i], test_volumes[i], test_date, tes_time)
        )

    return Statistics(test_ticker, test_records)

def calculate_mean(data: list) -> (list[float], float):
    expect_data_deltas_in_percent = [abs(data[i] - data[i - 1]) * 100 / data[i - 1] for i in range(1, len(data))]
    expect_absolute_mean_data_in_percent = sum(expect_data_deltas_in_percent) / len(expect_data_deltas_in_percent)
    return expect_data_deltas_in_percent, expect_absolute_mean_data_in_percent

def calculate_mean_absolute_deviation(data_delta: list, mean: float) -> float:
    abs_delta: list[float] = [abs(x - mean) for x in data_delta]
    mad = sum(abs_delta) / len(data_delta)
    return mad



def test_statistics_class():
    test_prices: list[float] = [
        10.0, 12.0, 13.0, 17.0, 13.0, 9.0, 8.0, 9.0, 9.0, 10.0
    ]
    test_volumes: list[int] = [
        100, 110, 115, 145, 150, 160, 162, 170, 172, 175
    ]

    test_stat = make_stat(test_prices, test_volumes)

    expect_prices_delta, expect_absolute_mean_price_in_percent = calculate_mean(test_prices)
    expect_volumes_delta, expect_absolute_mean_volume_in_percent = calculate_mean(test_volumes)

    expect_price_mad_in_percent = calculate_mean_absolute_deviation(expect_prices_delta, expect_absolute_mean_price_in_percent)
    expect_volume_mad_in_percent = calculate_mean_absolute_deviation(expect_volumes_delta, expect_absolute_mean_volume_in_percent)

    assert test_stat.absolute_mean_price_in_percent == pytest.approx(expect_absolute_mean_price_in_percent)
    assert test_stat.absolute_mean_volume_in_percent == pytest.approx(expect_absolute_mean_volume_in_percent)

    assert test_stat.price_mad_in_percent == pytest.approx(expect_price_mad_in_percent)
    assert test_stat.volume_mad_in_percent == pytest.approx(expect_volume_mad_in_percent)

def test_absolute_mean_metrics_sensitivity_1():
    # цены за данный timeframe слабо изменялись(слабая волатильность)
    test_prices_X = [
        10.0, 10.0, 10.0, 10.0, 10.0, 9.0, 8.0, 9.0, 9.0, 10.0
    ]
    test_volumes_X = [
        100, 115, 116, 145, 150, 160, 162, 167, 170, 175
    ]
    test_stat_X = make_stat(test_prices_X, test_volumes_X)

    # цены за данный timeframe слабо изменялись(слабая волатильность)
    test_prices_Y = [
        10.0, 10.0, 9.0, 9.0, 9.0, 9.0, 9.0, 8.0, 8.0, 8.0
    ]
    test_volumes_Y = [
        100, 110, 115, 145, 150, 160, 162, 170, 172, 175
    ]
    test_stat_Y = make_stat(test_prices_Y, test_volumes_Y)

    """
    Исходя из данных мы можем сделать вывод, что бумага X более волатильная чем бумага Y
    """
    assert test_stat_X.absolute_mean_price_in_percent > test_stat_Y.absolute_mean_price_in_percent
    """"
    тоже самое можно сказать и про средни темпы изменения объемов, волатильность объемов бумаги X большее чем Y 
    """
    assert test_stat_X.absolute_mean_volume_in_percent > test_stat_Y.absolute_mean_volume_in_percent

def test_absolute_mean_metrics_sensitivity_2():
    # цены за данный timeframe слаба изменялись(слабая волатильность)
    test_prices_X = [
        100.0, 100.0, 102.0, 103.0, 103.0, 103.0, 102.0, 103.0, 103.0, 103.0
    ]
    test_volumes_X = [
        1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000
    ]
    test_stat_X = make_stat(test_prices_X, test_volumes_X)

    # цены за данный timeframe слаба изменялись(слабая волатильность)
    test_prices_Y = [
        1000.0, 1005.0, 1020.0, 1035.0, 1030.0, 1032.0, 1021.0, 1033.0, 1030.0, 1030.0
    ]
    test_volumes_Y = [
        1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000
    ]
    test_stat_Y = make_stat(test_prices_Y, test_volumes_Y)

    """
    Исходя из данных мы можем сделать вывод, что бумага Y более волатильная чем бумага X, но при этом
    разница в волатильности минимальна, так как несмотря на больше значение изменения бумаги Y в абсолютных
    значениях, но в относительных они одного порядка приблизительно, что мы и должны наблюдать
    """
    assert test_stat_Y.absolute_mean_price_in_percent > test_stat_X.absolute_mean_price_in_percent

def test_absolute_mean_metrics_sensitivity_3():
    # цены за данный timeframe слаба изменялись(слабая волатильность)
    test_prices_X = [
        100.0, 117.0, 120.0, 156.0, 160.0, 133.0, 115.0, 167.0, 188.0, 118.0, 113.0, 145.0, 156.0, 120.0, 111.0, 110.0,
    ]
    test_volumes_X = [
        100, 110, 115, 145, 150, 160, 162, 170, 172, 175, 200, 200, 200, 200, 200, 200,
    ]
    test_stat_X = make_stat(test_prices_X, test_volumes_X)

    # цены за данный timeframe слаба изменялись(слабая волатильность)
    test_prices_Y = [
        100.0, 100.0, 102.0, 103.0, 103.0, 103.0, 102.0, 103.0, 103.0, 103.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0,
    ]
    test_volumes_Y = [
        100, 110, 115, 145, 150, 160, 162, 170, 172, 175, 200, 200, 200, 200, 200, 200,
    ]
    test_stat_Y = make_stat(test_prices_Y, test_volumes_Y)

    """
    Несмотря на то что по общему взгляду кажется что бумагу X сильно колбасит(большая волатильность) но средне 
    изменение цены около 16%(что довольно маловато на мой взгляд) но не все так плохо, в сравнении этой метрики
    со значением бумаги Y то действительно видно что бумага X значительнее подвержана волатильности. Из чего
    можно сделать вывод что эти метрики не совсем хорошо информативны в абсолютных значениях, но крайне хороши в 
    сравнении с аналогичными метриками других бумаг
    """
    assert test_stat_X.absolute_mean_price_in_percent > test_stat_Y.absolute_mean_price_in_percent



# def test_aggregated_stat_class():
#     test_prices_X = [
#         10.0, 12.0, 13.0, 17.0, 13.0, 9.0, 8.0, 9.0, 9.0, 10.0
#     ]
#     test_volumes_X = [
#         100, 110, 115, 145, 150, 160, 162, 170, 172, 175
#     ]
#     test_stat_X = make_stat(test_prices_X, test_volumes_X)
#
#
#     test_prices_Y = [
#         20.0, 21.0, 25.0, 25.0, 24.0, 22.0, 22.0, 23.0, 23.0, 22.0
#     ]
#     test_volumes_Y = [
#         200, 210, 235, 345, 350, 460, 562, 770, 772, 775
#     ]
#     test_stat_Y = make_stat(test_prices_Y, test_volumes_Y)
#
#
#     test_prices_Z = [
#         1000.0, 1010.0, 1025.0, 1067.0, 1100.0, 1200.0, 1050.0, 999.0, 980.0, 985.0
#     ]
#     test_volumes_Z = [
#         3000, 3010, 3035, 3045, 3100, 3600, 4620, 4700, 4802, 5705
#     ]
#     test_stat_Z = make_stat(test_prices_Z, test_volumes_Z)
#
#     test_stat_list = [test_stat_X, test_stat_Y, test_stat_Z]
#
#     aggregated_stat = AggregatedStatistic()
#     for test_ticker_stat in test_stat_list:
#         aggregated_stat.use_day_stat(test_ticker_stat)
#
#     aggregated_stat.complete_calculation()
#
#     print("\n")

