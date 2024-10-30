import pandas as pd

class Statistics:
    def __init__(self, ticker: str, records: list):
        self.ticker = ticker
        self.df = pd.DataFrame(records, columns=['last_price', 'last_volume', 'date', 'time'])

        self.price_delta_df_in_percent = pd.DataFrame()
        self.volume_delta_df_in_percent = pd.DataFrame()

        self.absolute_mean_price_in_percent: float = 0.0
        self.absolute_mean_volume_in_percent: float = 0.0

        self.price_mad_in_percent: float = 0.0
        self.volume_mad_in_percent: float = 0.0

        if not self.df.empty:
            self.price_delta_df_in_percent = self.df['last_price'].pct_change() * 100
            self.price_delta_df_in_percent = self.price_delta_df_in_percent.iloc[1: ].abs()

            self.volume_delta_df_in_percent = self.df['last_volume'].pct_change() * 100
            self.volume_delta_df_in_percent = self.volume_delta_df_in_percent.iloc[1: ].abs()

            if self.price_delta_df_in_percent.size > 1:
                self.absolute_mean_price_in_percent = self.__calculate_absolute_mean(self.price_delta_df_in_percent)
                self.price_mad_in_percent = self.__calculate_mean_absolute_deviation(
                    self.price_delta_df_in_percent, self.absolute_mean_price_in_percent
                )

            if self.volume_delta_df_in_percent.size > 1:
                self.absolute_mean_volume_in_percent = self.__calculate_absolute_mean(self.volume_delta_df_in_percent)
                self.volume_mad_in_percent = self.__calculate_mean_absolute_deviation(
                    self.volume_delta_df_in_percent, self.absolute_mean_volume_in_percent
                )

        self.total_volume: int = self.df['last_volume'].sum()
        self.total_volume_in_money: int = int(float(self.total_volume) * self.absolute_mean_price_in_percent)

    @staticmethod
    def __calculate_mean_absolute_deviation(df_delta: pd.DataFrame, mean: float) -> float:
        """
        Среднее абсолютное отклонение (Mean Absolute Deviation, MAD) показывает, насколько в среднем значения данных
        отклоняются от среднего значения в абсолютных значениях. Этот показатель измеряет среднюю величину отклонений
        от среднего значения, не учитывая направление отклонений (положительное или отрицательное).

            Физический смысл
        Среднее абсолютное отклонение показывает, насколько в среднем значения данных отклоняются от среднего значения.
        Оно измеряется в тех же единицах, что и исходные данные, что делает его более интуитивно понятным.
        """
        # Вычисление абсолютных отклонений от среднего(арифметического/геометрического/гармонического)
        absolute_deviations = (df_delta - mean).abs()

        # Вычисление среднего значения абсолютных отклонений
        mad = absolute_deviations.mean()
        return mad

    @staticmethod
    def __calculate_absolute_mean(df_delta: pd.DataFrame) -> float:
        """
        Мы не можем рассчитать обычное среднее арифметическое изменения, так как изменение может быть положительным, так
        и отрицательным, соответственно простое суммирование применять нельзя.
        В таком случае можно суммировать модуль изменения(да, так мы теряем направленность изменения + или -). Такой
        показатель будет показывать среднее изменение в абсолютных значениях
        """
        abs_sum_df = df_delta.to_numpy().sum().sum()
        n = df_delta.size
        assert n != 0
        return abs_sum_df / n

    def __repr__(self) -> str:
        return (f"Statistics(\n\tticker={self.ticker}\n\t"
                f"absolute_mean_price={self.absolute_mean_price_in_percent} %\n\t"
                f"price_mad={self.price_mad_in_percent} %\n\t"
                
                f"absolute_mean_volume={self.absolute_mean_volume_in_percent} %\n\t"
                f"volume_mad={self.volume_mad_in_percent} %\n\t"
                f"total_volume={self.total_volume}\n\t"
                f"total_volume_in_money={self.total_volume_in_money}\n)"
        )

class DayStatistic:
    def __init__(
            self,
            stat_for_5_min: Statistics,
            stat_for_30_min: Statistics,
            stat_for_1_hour: Statistics,
            stat_for_5_hour: Statistics
    ):
        self.stat_for_5_min: Statistics = stat_for_5_min
        self.stat_for_30_min: Statistics = stat_for_30_min
        self.stat_for_1_hour: Statistics = stat_for_1_hour
        self.stat_for_5_hour: Statistics = stat_for_5_hour

    def __repr__(self) -> str:
        return (f"DayStatistic(\n\t"
                f"stat_for_5_min={self.stat_for_5_min} %\n\t"
                f"stat_for_30_min={self.stat_for_30_min} %\n\t"
                f"stat_for_1_hour={self.stat_for_1_hour} %\n\t"
                f"stat_for_5_hour={self.stat_for_5_hour} %\n)")


class AggregatedStatistic:
    def __init__(self):
        self.__n_for_timeframe = 0
        self.absolute_mean_price_for_timeframe_in_percent: float = 0.0
        self.absolute_mean_volume_for_timeframe_in_percent: float = 0.0

    def use_day_stat(self, stat_for_timeframe: Statistics):
        self.__n_for_timeframe += stat_for_timeframe.df.size
        self.absolute_mean_price_for_timeframe_in_percent += stat_for_timeframe.absolute_mean_price_in_percent
        self.absolute_mean_volume_for_timeframe_in_percent += stat_for_timeframe.absolute_mean_volume_in_percent

        # ...

    def complete_calculation(self):
        if self.__n_for_timeframe != 0:
            self.absolute_mean_price_for_timeframe_in_percent /= self.__n_for_timeframe
            self.absolute_mean_volume_for_timeframe_in_percent /= self.__n_for_timeframe