from pathlib import Path
import numpy as np
from typing import List
from scipy.interpolate import interp1d


def open_csv(csv_path: Path) -> List[str]:
    """Open data saved by the arduino.

    Args:
        csv_path (Path): Path of the data to open.

    Returns:
        List[str]: List of every line in the data file.
    """
    with open(csv_path, "rt") as logfile:
        full_data = logfile.read().splitlines()
    return full_data


def interpolate_data(time_ms_base: np.ndarray, data:np.ndarray, 
                     time_interpolate_axis: np.ndarray) -> np.ndarray:
    """Interpolate time / data set on a new time axis.

    Args:
        time_ms_base (np.ndarray): Initial time axis.
        data (np.ndarray): Data of the initial time axis.
        time_interpolate_axis (np.ndarray): New axis on which the data should 
        be interpolated.

    Returns:
        np.ndarray: Data interpolate on the new time axis.
    """
    f_data = interp1d(time_ms_base, data)
    return f_data(time_interpolate_axis)