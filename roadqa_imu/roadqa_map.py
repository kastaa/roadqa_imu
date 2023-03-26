import folium
import numpy as np
from pylab import cm
from matplotlib.colors import rgb2hex
from scipy.ndimage import generic_filter

from .imu_gps_data import ImuGpsData


class RoadQAMap:
    def __init__(self, imu_gps_data: ImuGpsData, map_type: str = "stamentoner", map_zoom: int = 15,
                 colormap: str = "jet"):
        self.imu_gps_data = imu_gps_data
        self.process_vibration()
        self._map_type = map_type
        self._map_zoom = map_zoom
        self._color_map = self._generate_colormap(colormap)
    
    def _generate_colormap(self, colormap: str):
        cmap = cm.get_cmap(colormap, 255)
        color_dict = {}
        for i in range(cmap.N):
            rgba = cmap(i)
            color_dict[i] = rgb2hex(rgba)
        return color_dict
        
    def process_vibration(self, threshold: float = 0.01, sensibility: float = 0.4, 
                          contrast: float = (1 / 3.)):
        acc_y = self.imu_gps_data.acceleration[2, :]
        acc_y_norm = acc_y - acc_y.mean()
        diff_acc_y = np.abs(np.diff(acc_y))
        
        vibration = diff_acc_y - diff_acc_y.min()
        vibration = (vibration / vibration.max()) ** (1 / sensibility)

        vibration[vibration < threshold] = vibration[vibration < threshold] * 0

        self.vibration = vibration ** contrast
    
    def _create_map(self):
        coord_mean = self.imu_gps_data.coord.mean(axis=1)
        init_map = folium.Map(location=coord_mean, zoom_start=self._map_zoom)
        folium.TileLayer(self._map_type).add_to(init_map)
        return init_map
    
    def generate_map(self, subsample_factor: int = 100):
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
        
    
    
    