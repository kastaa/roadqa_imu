from pathlib import Path
from scipy.interpolate import interp1d


def open_csv(csv_path: Path):
    with open(csv_path, "rt") as logfile:
        full_data = logfile.read().splitlines()
    return full_data


def interpolate_data(time_ms_base, data, time_interpolate_axis):
    f_data = interp1d(time_ms_base, data)
    return f_data(time_interpolate_axis)