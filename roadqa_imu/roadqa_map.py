import folium
import numpy as np
from pylab import cm
from matplotlib.colors import rgb2hex
from scipy.ndimage import generic_filter

from .imu_gps_data import ImuGpsData

SENSIBILITY_THRESHOLD = 0.1


class RoadQAMap:
    """Class that generate vibration map from ImuGPSData input."""
    def __init__(self, imu_gps_data: ImuGpsData, map_type: str = "stamentoner", 
                 map_zoom: int = 15, colormap: str = "jet") -> None:
        """

        Args:
            imu_gps_data (ImuGpsData): Imu ang GPS data
            map_type (str, optional): map type used to draw the map. Defaults 
            to "stamentoner".
            map_zoom (int, optional): Zoom used to draw the map. Defaults to 15.
            colormap (str, optional): Colormap identifier to draw vibration data. 
            Defaults to "jet".
        """
        self.imu_gps_data = imu_gps_data
        self.process_vibration()
        self._map_type = map_type
        self._map_zoom = map_zoom
        self._color_map = self._generate_colormap(colormap)
    
    def _generate_colormap(self, colormap: str) -> dict[int, str]:
        """Generate a color map dictionnary used to display the vibration data

        Args:
            colormap (str): Color map identifier.

        Returns:
            dict[int, str]: color map dictionnary.
        """
        cmap = cm.get_cmap(colormap, 255)
        color_dict = {}
        for i in range(cmap.N):
            rgba = cmap(i)
            color_dict[i] = rgb2hex(rgba)
        return color_dict
        
    def process_vibration(self, threshold: float = 0.01, sensibility: float = 0.4, 
                          contrast: float = (1 / 3.)) -> None:
        """Process IMU data to generate a estimate a quality estimation of the road 

        Args:
            threshold (float, optional): Threshold value between 0 and 1 at which 
            vibration are rounded to 0. Defaults to 0.01.
            sensibility (float, optional): Sensibility factor between 0 and 1 that 
            increase the sensibility of the metric to small vibration. Defaults to 0.4.
            contrast (float, optional): Constrast factor between 0 and 1 to increase 
            contrast of the metric. Defaults to (1 / 3.).
        """
        # Only taking the up/down component of acceleration
        acc_y = self.imu_gps_data.acceleration[2, :]
        acc_y_norm = acc_y - acc_y.mean()
        diff_acc_y = np.abs(np.diff(acc_y_norm))
        
        vibration = diff_acc_y - diff_acc_y.min()
        sensibility = sensibility + SENSIBILITY_THRESHOLD
        vibration = (vibration / vibration.max()) ** (1 / (sensibility))

        vibration[vibration < threshold] = vibration[vibration < threshold] * 0

        self.vibration = vibration ** contrast
    
    def _create_map(self) -> None:
        """Initialize / reset the map"""
        coord_mean = self.imu_gps_data.coord.mean(axis=1)
        init_map = folium.Map(location=coord_mean, zoom_start=self._map_zoom)
        folium.TileLayer(self._map_type).add_to(init_map)
        return init_map
    
    def generate_map(self, subsample_factor: int = 100):
        """Display the vibration data on the map 

        Args:
            subsample_factor (int, optional): vibration data are subsample on the map by this 
            factor. Defaults to 100.

        Returns:
            _type_: _description_
        """
        map_ = self._create_map()
        
        vibration_max = generic_filter(self.vibration, np.max, size=subsample_factor)
        vibration_sample = vibration_max[::subsample_factor]
        
        latitude = self.imu_gps_data.coord[0, ::subsample_factor]
        longitude = self.imu_gps_data.coord[1, ::subsample_factor]
        
        vibration_map = vibration_sample - vibration_sample.min()
        vibration_map = vibration_map / vibration_map.max() * (len(self._color_map) - 1)
        
        for i in range(len(latitude) - 1):
            color_value = np.round(vibration_map[i]).astype(np.uint8)
            folium.PolyLine(((latitude[i], longitude[i]), (latitude[i + 1], longitude[i + 1])),
                              color=self._color_map[color_value], weight=7).add_to(map_)
        
        return map_
        
    
    
    