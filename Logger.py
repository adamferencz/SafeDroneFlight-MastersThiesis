"""
Custom-made logger class for logging additional values.

Adam Ferencz
VUT FIT 2022
"""

import csv
import json
import statistics
from datetime import datetime

import matplotlib.pyplot as plt

from utils import *


class Logger:
    """ Class used to analyse flight and collect flight log."""
    def __init__(self, free_range, warning_range, path='logs/general_log'):
        self.path = path
        self.is_logging = False
        self.z_max = 0
        self.date = 0

        self.fly_time_start = datetime.now()
        self.fly_time = 0
        self.fly_time_s = 0

        self.x, self.y, self.z = 0, 0, 0

        self.z_max = 0

        # Velocity.
        self.vx, self.vy, self.vz = 0, 0, 0
        self.vx_max, self.vy_max, self.vz_max = 0, 0, 0

        self.latitude, self.longitude, self.altitude = 0, 0, 0

        self.pitch, self.roll, self.yaw = 0, 0, 0

        # Command.
        self.cx, self.cy, self.cz = 0, 0, 0
        # Save command.
        self.scx, self.scy, self.scz = 0, 0, 0

        # Distance from the safe path.
        self.d = 0
        self.dx, self.dy, self.dz = 0, 0, 0

        # Powers in correction equations.
        self.gc_pow_x, self.gc_pow_y, self.gc_pow_z = 0, 0, 0
        self.gpc_pow_x, self.gpc_pow_y, self.gpc_pow_z = 0, 0, 0
        self.gfc_pow_x, self.gfc_pow_y, self.gfc_pow_z = 0, 0, 0

        self.data = []

        # Range levels.
        self.free_range = free_range
        self.warning_range = warning_range

    def reset_logging(self):
        """ Resets properties. """
        self.__init__(self.free_range, self.warning_range)

    def save(self, drone):
        """
        Saves log and creates summary.

        :param drone: object drone implementing ``AbstractDroneModel``

        """
        log_dict = self.get_log_dict()
        self.path = drone.log_folder
        with open(self.path + '/log.csv', 'w', newline='') as csvfile:
            fieldnames = log_dict.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for d in self.data:
                writer.writerow(d)

        self.create_summary()

    def update(self, drone, corrector):
        """
        Updates and computes collected values.

        :param drone: object drone implementing ``AbstractDroneModel``
        :param corrector: object ``Corrector``

        """
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y")
        self.date = dt_string

        dt_string = now.strftime("%H:%M:%S")
        self.time = dt_string

        delta_time = now - self.fly_time_start
        self.fly_time_s = delta_time.total_seconds()

        self.x = drone.position[0]
        self.y = drone.position[1]
        self.z = drone.position[2]

        if self.z_max < self.z:
            self.z_max = self.z

        self.vx = drone.speed[0]
        self.vy = drone.speed[1]
        self.vz = drone.speed[2]

        if self.vx_max < self.vx:
            self.vx_max = self.vx
        if self.vy_max < self.vy:
            self.vy_max = self.vy
        if self.vz_max < self.vz:
            self.vz_max = self.vz

        if drone.GPS is not None:
            self.latitude = drone.GPS.latitude
            self.longitude = drone.GPS.longitude
            self.altitude = drone.GPS.altitude
        else:
            self.latitude = 0
            self.longitude = 0
            self.altitude = 0

        self.pitch = drone.pitch
        self.roll = drone.roll
        self.yaw = drone.yaw

        self.cx = corrector.command[0]
        self.cy = corrector.command[1]
        self.cz = corrector.command[2]

        self.scx = corrector.safe_command[0]
        self.scy = corrector.safe_command[1]
        self.scz = corrector.safe_command[2]

        if corrector.nearest_point is not None:
            self.d = distance_np(corrector.nearest_point, drone.position)
            self.dx = corrector.nearest_point[0] - drone.position[0]
            self.dy = corrector.nearest_point[1] - drone.position[1]
            self.dz = corrector.nearest_point[2] - drone.position[2]

        self.gc_pow_x = corrector.gain_command_power[0]
        self.gc_pow_y = corrector.gain_command_power[1]
        self.gc_pow_z = corrector.gain_command_power[2]

        self.gpc_pow_x = corrector.gain_present_correction_power[0]
        self.gpc_pow_y = corrector.gain_present_correction_power[1]
        self.gpc_pow_z = corrector.gain_present_correction_power[2]

        self.gfc_pow_x = corrector.gain_future_correction_power[0]
        self.gfc_pow_y = corrector.gain_future_correction_power[1]
        self.gfc_pow_z = corrector.gain_future_correction_power[2]

    def get_log_dict(self):
        """ Prepare log dict for saving. """
        return {
            "date": self.date,

            "fly_time": self.time,
            "fly_time_s": self.fly_time_s,

            "x": self.x,
            "y": self.y,
            "z": self.z,

            "z_max": self.z_max,

            "vx": self.vx,
            "vy": self.vy,
            "vz": self.vz,

            "vx_max": self.vx_max,
            "vy_max": self.vy_max,
            "vz_max": self.vz_max,

            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,

            "pitch": self.pitch,
            "roll": self.roll,
            "yaw": self.yaw,

            "cx": self.cx,
            "cy": self.cy,
            "cz": self.cz,

            "scx": self.scx,
            "scy": self.scy,
            "scz": self.scz,

            "d": self.d,
            "dx": self.dx,
            "dy": self.dy,
            "dz": self.dz,

            "gc_pow_x": self.gc_pow_x,
            "gc_pow_y": self.gc_pow_y,
            "gc_pow_z": self.gc_pow_z,
            "gpc_pow_x": self.gpc_pow_x,
            "gpc_pow_y": self.gpc_pow_y,
            "gpc_pow_z": self.gpc_pow_z,
            "gfc_pow_x": self.gfc_pow_x,
            "gfc_pow_y": self.gfc_pow_y,
            "gfc_pow_z": self.gfc_pow_z,
        }

    def log(self, drone, corrector):
        """
        Logging process.

        :param drone: object drone implementing ``AbstractDroneModel``
        :param corrector: object ``Corrector``

        """
        if self.is_logging:
            self.update(drone, corrector)
            log_dict = self.get_log_dict()
            self.data.append(log_dict)

    @staticmethod
    def statistical_analysis(values):
        """
        Return statistics.

        :param values: list of values

        """
        minimum = min(values)
        maximum = max(values)
        mean = sum(values) / len(values)
        variance = statistics.variance(values)
        standard_deviation = statistics.stdev(values)

        return minimum, maximum, mean, variance, standard_deviation

    @staticmethod
    def statistical_analysis_ideal(values, ideal_value):
        """
        Return statistics. Changed by cutting level.

        :param values: list of values
        :param ideal_value: cutting level - everything below is zero

        """
        new_vals = list(map(lambda i: i - ideal_value if i - ideal_value > 0 else 0, values))
        minimum = min(new_vals)
        maximum = max(new_vals)
        mean = sum(new_vals) / len(new_vals)
        variance = statistics.variance(new_vals)
        standard_deviation = statistics.stdev(new_vals)

        return minimum, maximum, mean, variance, standard_deviation

    def print_graph(self, x, y):
        """
        Creates graph of absolut distance.

        :param x: array of distances
        :param y: array of times

        """
        d = x
        fly_time_s = y
        # fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
        # plt.rcParams.update({'font.size': 15})
        fig, ax1 = plt.subplots(1, 1)
        # fig.set_size_inches(10, 6)
        fig.subplots_adjust(hspace=0.5)
        fig.suptitle('Vzdálenost od bezpečná dráhy v čase', fontsize=16)
        # fig.suptitle('Distance from defined path in time', fontsize=16)
        free_range = np.ones(len(d)) * self.free_range
        warning_range = np.ones(len(d)) * self.warning_range
        ax1.plot(fly_time_s, d, color='b', label='vzdálenost')
        ax1.plot(fly_time_s, free_range, color='y', label='hranice volnosti')
        ax1.plot(fly_time_s, warning_range, color='r', label='hranice bezpečné zóny')
        ax1.set_xlabel('čas [s]')
        # ax1.set_xlabel('time [s]')
        ax1.set_ylabel('vzdálenost [m]')
        # ax1.set_ylabel('distance [m]')
        ax1.grid(True)
        # ax1.legend(loc=2, prop={'size': 15})

        # plt.show()
        # plt.imsave('distance_graph.png')
        plt.savefig(self.path+'/distance_graph.png')

    def create_summary(self):
        """ Creates summary json file. """
        # self.path = 'logs/12-04-2022_01-35-02'
        import pandas as pd
        fields = 'date,fly_time,fly_time_s,x,y,z,z_max,vx,vy,vz,vx_max,vy_max,vz_max,latitude,longitude,altitude,pitch,roll,yaw,cx,cy,cz,scx,scy,scz,d,dx,dy,dz,gc_pow_x,gc_pow_y,gc_pow_z,gpc_pow_x,gpc_pow_y,gpc_pow_z,gfc_pow_x,gfc_pow_y,gfc_pow_z'.split(
            ',')
        df = pd.read_csv(self.path + '/log.csv', skipinitialspace=True, usecols=fields)

        # počet opuštění zóny
        # poměr času letu mimo zónu

        # Free zone
        is_in_free_zone = True
        time_in_free_zone = 0
        time_out_free_zone = 0
        free_zone_left_count = 0
        time_out_free_zone_list = [0]

        # Warning zone
        is_in_warning_zone = True
        time_in_warning_zone = 0
        time_out_warning_zone = 0
        warning_zone_left_count = 0
        time_out_warning_zone_list = [0]

        d = df['d'].tolist()

        if sum(d) == 0:
            print("No path data in the flight log.")
            return
        fly_time_s = df['fly_time_s'].tolist()
        prev_fly_time_s = fly_time_s[0]
        for (distance, curr_fly_time_s) in zip(d, fly_time_s):
            print(distance, curr_fly_time_s)

            delta_time = curr_fly_time_s - prev_fly_time_s

            if distance < self.free_range:
                is_in_free_zone = True
                time_in_free_zone += delta_time


            else:
                if is_in_free_zone is True:
                    free_zone_left_count += 1
                    time_out_free_zone_list.append(0)
                    is_in_free_zone = False

                time_out_free_zone += delta_time
                time_out_free_zone_list[free_zone_left_count - 1] += delta_time

            if distance < self.warning_range:
                is_in_warning_zone = True
                time_in_warning_zone += delta_time

            else:
                if is_in_warning_zone is True:
                    warning_zone_left_count += 1
                    time_out_warning_zone_list.append(0)
                    is_in_warning_zone = False

                time_out_warning_zone += delta_time
                time_out_warning_zone_list[warning_zone_left_count - 1] += delta_time

            prev_fly_time_s = curr_fly_time_s

        time_out_warning_zone_list = [i for i in time_out_warning_zone_list if i != 0]
        time_out_warning_zone_list = [i for i in time_out_warning_zone_list if i != 0]
        print('minimum, maximum, mean, variance, standard_deviation')
        minimum_d, maximum_d, mean_d, variance_d, standard_deviation_d = self.statistical_analysis(d)
        minimum_df, maximum_df, mean_df, variance_df, standard_deviation_df = self.statistical_analysis_ideal(d,
                                                                                                              self.free_range)
        minimum_dw, maximum_dw, mean_dw, variance_dw, standard_deviation_dw = self.statistical_analysis_ideal(d,
                                                                                                              self.warning_range)

        summary = {
            '1': '',
            '--duration in and out of free_zone--': '--------------------',
            'time_in_free_zone': time_in_free_zone,
            'time_out_free_zone': time_out_free_zone,
            '% time_in_free_zone': time_in_free_zone / (time_out_free_zone + time_in_free_zone) * 100,
            '% time_out_free_zone': time_out_free_zone / (time_out_free_zone + time_in_free_zone) * 100,
            'free_zone_left_count': free_zone_left_count,
            'time_out_free_zone_list': time_out_free_zone_list,
            'average_duration_out_free_zone': sum(time_out_free_zone_list) / len(time_out_free_zone_list),
            '2': '',
            '--duration in and out of warning_zone--': '--------------------',
            'time_in_warning_zone': time_in_warning_zone,
            'time_out_warning_zone': time_out_warning_zone,
            '% time_in_warning_zone': time_in_warning_zone / (time_out_warning_zone + time_in_warning_zone) * 100,
            '% time_out_warning_zone': time_out_warning_zone / (time_out_warning_zone + time_in_warning_zone) * 100,
            'warning_zone_left_count': warning_zone_left_count,
            'time_out_warning_zone_list': time_out_warning_zone_list,
            'average_duration_out_warning_zone': sum(time_out_warning_zone_list) / len(time_out_warning_zone_list),
            '3': '',
            '--statistical data about distance from path--': '--------------------',
            'minimum_d': minimum_d,
            'maximum_d': maximum_d,
            'mean_d': mean_d,
            'variance_d': variance_d,
            'standard_deviation_d': standard_deviation_d,
            '4': '',
            '--statistical data about distance from free_zone--': '------------------',
            'minimum_df': minimum_df,
            'maximum_df': maximum_df,
            'mean_df': mean_df,
            'variance_df': variance_df,
            'standard_deviation_df': standard_deviation_df,
            '5': '',
            '--statistical data about distance from warning_zone--': '------------------',
            'minimum_dw': minimum_dw,
            'maximum_dw': maximum_dw,
            'mean_dw': mean_dw,
            'variance_dw': variance_dw,
            'standard_deviation_dw': standard_deviation_dw,
        }

        # https://stackoverflow.com/questions/44689546/how-to-print-out-a-dictionary-nicely-in-python
        def print_inventory(dct):
            """
            Helper function.
            :param dct: 

            """
            print("\nSummary:")
            for item, amount in dct.items():
                if type(amount) == int or type(amount) == float:
                    print("{} : {:.2f}".format(item, amount))
                else:
                    print("{} : {}".format(item, amount))

        print_inventory(summary)

        with open(self.path + '/summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=4)

        self.print_graph(d, fly_time_s)


# Test or solo usage.
if __name__ == "__main__":
    logger = Logger(1, 2, path='logs/test_users/tester1-visual-no-assistent-no/14-04-2022_21-29-51')
    logger.create_summary()
