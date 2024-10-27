from statistics import *
from datetime import datetime

def test_make_statistics_for_hours():
    data = [
        # last_price, last_volume, date, time
        (56.0, 1000.0, '2024-10-17', '15:04:05'),

        (56.0, 1000.0, '2024-10-17', '16:04:05'),

        (56.0, 1000.0, '2030-10-17', '17:04:05'),
        (56.0, 1000.0, '2024-10-17', '17:06:05'),

        (56.0, 1000.0, '2025-10-17', '18:04:05'),
        (56.0, 1000.0, '2027-10-17', '18:07:05'),
        (56.0, 1000.0, '2024-10-17', '18:08:05')
    ]

    df = sql_rows_to_pandas_data_frames(data)
    hours = Statistics.make_statistics_for_hours('X', df)
    assert len(hours) == 4

    prev_time = None
    for hour in hours:
        hour_fd = hour.get_df()
        assert 'time' in hour_fd.columns

        current_time = datetime.strptime(hour_fd.loc[hour_fd.index[0], 'time'], '%H:%M:%S').time()
        if prev_time:
            current_datetime = datetime.combine(datetime(2000, 1, 1), current_time)
            prev_datetime = datetime.combine(datetime(2000, 1, 1), prev_time)

            diff = current_datetime - prev_datetime

            diff_in_hours = diff.total_seconds() / 3600

            assert 1 <= diff_in_hours <= 24

        prev_time = current_time


def test_make_statistics_for_days():
    data = [
        # last_price, last_volume, date, time
        (56.0, 1000.0, '2024-10-10', '15:04:05'),
        (56.0, 1000.0, '2024-10-10', '16:04:05'),

        (56.0, 1000.0, '2024-10-17', '17:04:05'),

        (56.0, 1000.0, '2024-10-18', '17:06:05'),
        (56.0, 1000.0, '2024-10-18', '18:04:05'),
        (56.0, 1000.0, '2024-10-18', '18:07:05'),

        (56.0, 1000.0, '2024-10-23', '18:08:05')
    ]

    df = sql_rows_to_pandas_data_frames(data)
    days = Statistics.make_statistics_for_days('X', df)
    assert len(days) == 4

    prev_day = None
    for day in days:
        day_df = day.get_df()
        assert 'date' in day_df.columns

        current_day = datetime.strptime(day_df.loc[day_df.index[0], 'date'], '%Y-%m-%d').date()
        if prev_day:
            diff = current_day - prev_day
            diff_in_days = diff.days
            assert diff_in_days >= 1 and diff_in_days <= 365

        prev_day = current_day