from typing import List
from dataclasses import dataclass
import numpy as np

from .utils import interpolate_data


@dataclass
class IMU:
    """IMU data as collected by the measuring device
    """
    ms_count: int
    acc_x: float
    acc_y: float
    acc_z: float

@dataclass
class GPS:
    """GPS data as collected by the measuring device
    """
    ms_count: int
    latitude: float
    longitude: float 
    speed: float


class ImuGpsData:
    metadata_index = 2 # number of medata line in the data file
    
    def __init__(self, gps: List[GPS] = [], imu: List[IMU] = []):
        self._raw_gps = gps
        self._raw_imu = imu
        self._valid_gps = None
        self.ms_count = None
        self.coord = None
        self.acceleration = None
        
    @classmethod
    def from_csv(cls, csv_buffer: List[str]):
        """Initalize the ImuGpsData from a data file.

        Args:
            csv_buffer (List[str]): list of line from the data file.

        Raises:
            ValueError: unknown data in the data file.

        Returns:
            _type_: _description_
        """
        # TODO make some validation using the metadata. Eventually if I do update, the reader could be based
        # on what in those metadata
        data_dict = {"gps": [], "imu": []}
        for csv_line in csv_buffer[cls.metadata_index:]:
            split_csv_line = csv_line.split(";")
            sensor_key = split_csv_line[0]
            if sensor_key == "imu":
                imu_reading = (float(imu_value) for imu_value in split_csv_line[1:])
                data_dict["imu"].append(IMU(*imu_reading))
            elif sensor_key == "gps":
                # The 4 last values of gps data are not use right now: Hours, minute, second, empty
                gps_reading = (float(imu_value) for imu_value in split_csv_line[1:-4])
                data_dict["gps"].append(GPS(*gps_reading))
            else:
                raise ValueError(f"Got an unexpected sensor data {sensor_key}")
        return cls(**data_dict)
        
    def process(self, interpolation_period_ms=10) -> None:
        """Process IMU and GPS data to return a combine version of both data on the 
        same time axis.

        Args:
            interpolation_period_ms (int, optional): Sampling period of combine data. 
            Defaults to 10.
        """
        self._find_valid_gps()
        self._find_common_time_axis(interpolation_period_ms=interpolation_period_ms)
        self._process_gps()
        self._process_imu()
    
    def _find_valid_gps(self) -> None:
        valid = [np.abs(gps.latitude) > 0 and np.abs(gps.longitude) > 0 for gps in self._raw_gps]
        self._valid_gps = [index for (index, valid_value) in enumerate(valid) if valid_value]

    def _find_common_time_axis(self, interpolation_period_ms: int = 10) -> None:
        """Find the overlaping time between IMU and GPS

        Args:
            interpolation_period_ms (int, optional): Sampling period of the new time axis.
            Defaults to 10.
        """
        ms_count_gps = np.uint64([gps.ms_count for gps in self._raw_gps])[self._valid_gps]
        ms_count_imu = np.uint64([imu.ms_count for imu in self._raw_imu])
        
        # Finding overlap ms_count between goptionalps and imu
        min_common_time = max([ms_count_gps.min(), ms_count_imu.min()])
        max_common_time = min([ms_count_gps.max(), ms_count_imu.max()])
        
        self.ms_count = np.arange(min_common_time, max_common_time, interpolation_period_ms)
        
    def _process_imu(self) -> None:
        """Process IMU data
        """
        self.acceleration = []
        ms_count_imu = np.uint64([imu.ms_count for imu in self._raw_imu])
        acceleration_data = np.float32([[imu.acc_x, imu.acc_y, imu.acc_z] for imu in self._raw_imu])
        for acc_component in acceleration_data.T:
            acc_component_interpolate = interpolate_data(ms_count_imu, acc_component, self.ms_count)
            self.acceleration.append(acc_component_interpolate)
        self.acceleration = np.float32(self.acceleration)
    
    def _process_gps(self) -> None:
        """Process GPS data
        """
        self.coord = []
        ms_count_gps = np.uint64([gps.ms_count for gps in self._raw_gps])[self._valid_gps]
        gps_data = np.float32([[gps.latitude, gps.longitude] for gps in self._raw_gps])
        for gps_component in gps_data.T:
            gps_component_interpolate = interpolate_data(ms_count_gps, gps_component, self.ms_count)
            self.coord.append(gps_component_interpolate)
        self.coord = np.float64(self.coord)
        
        