import argparse
import webbrowser
from pathlib import Path

from roadqa_imu.imu_gps_data import ImuGpsData
from roadqa_imu.roadqa_map import RoadQAMap
from roadqa_imu.utils import open_csv


def main():
    args = parse_args()
    data_buffer = open_csv(args.data_path)
    imu_gps_data = ImuGpsData.from_csv(data_buffer)
    
    imu_gps_data.process()
    road_map = RoadQAMap(imu_gps_data)
    
    map = road_map.generate_map()
    
    output_file = "map_result.html"
    map.save(output_file)
    webbrowser.open(output_file, new=1)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("data_path", type=Path, help="Data path")
    return parser.parse_args()

if __name__ == "__main__":
    main()
