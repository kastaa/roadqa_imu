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
    road_map.process_vibration(args.threshold, args.sensibility, args.contrast)
    
    map = road_map.generate_map()
    
    if args.outpath is None:
        output_file = args.outpath
    else:
        output_file = "map_result.html"
    map.save(output_file)
    webbrowser.open(output_file, new=1)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("data_path", type=Path, help="Data path")
    parser.add_argument("-t", "--threshold", type=float, default=0.01,
                        help="Threshold factor (0 - 1) below which vibration is to to 0")
    parser.add_argument("-s", "--sensivity", type=float, default=0.3,
                        help="Sensivity factor (0 - 1) to process vibration data")
    parser.add_argument("-c", "--contrast", type=float, default=(1 / 3.),
                        help=":Contrast factor (0 - 1) for vibration metric")
    parser.add_argument("-o", "--outpath", type=Path, default=None,
                        help="Output filename where html map data will be saved")
    return parser.parse_args()

if __name__ == "__main__":
    main()
