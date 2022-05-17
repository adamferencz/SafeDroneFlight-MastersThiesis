"""
Script used to summarise outputs of many user tests.

Adam Ferencz
VUT FIT 2022
"""

import json
import os
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

# Selected flights from folder "safe_flight_assistant/logs/test_users/"
test_users = [
    'tester1-visual-no-assistent-yes',
    'tester1-visual-no-assistent-no',
    'tester2-visual-no-assistent-yes',
    'tester2-visual-no-assistent-no',
    'tester3-visual-no-assistent-yes',
    'tester3-visual-no-assistent-no',
    'tester4-visual-no-assistent-yes',
    'tester4-visual-no-assistent-no',
]


def plot_photos(user_name, flight_name):
    """
    Plots photos from selected tests.

    :param user_name: str name of the tester
    :param flight_name: str timestamp of the flight

    """
    path = 'logs/test_users/' + user_name + '/' + flight_name
    print(path)
    path_photos = 'logs/test_users/' + user_name + '/' + flight_name + '/photos/'
    path_photos_results_folder = 'logs/test_users_results/photos/' + user_name
    photos_names = os.listdir(path_photos)

    p_count = len(photos_names)
    if (p_count == 0):
        print("Error p_count: " + path)
        return
    f, axarr = plt.subplots(int(p_count / 3) + 1 if p_count > 0 else 0, 3)
    print(f"arr ({len(photos_names)}) [{int(len(photos_names) / 3), 3}]")
    f.suptitle('Car photos: ' + user_name + '/' + flight_name, fontsize=10)
    print(int(len(photos_names) / 3), 3)
    for (photos_name, idx) in zip(photos_names, range(len(photos_names))):
        photo = plt.imread(path_photos + photos_name)
        print(f"[{int(idx / 3)},{int(idx % 3)}]")
        axarr[int(idx / 3), int(idx % 3)].imshow(photo)
        axarr[int(idx / 3), int(idx % 3)].set_axis_off()
        axarr[int(idx / 3), int(idx % 3)].set_title(idx + 1)

    plt.savefig(path + '/photo-summary.png')
    Path(path_photos_results_folder).mkdir(parents=True, exist_ok=True)
    plt.savefig(path_photos_results_folder + '/' + flight_name + '-photo-summary.png')


def print_inventory(dct):
    """
    Helper function for printing dict nicely.

    :param dct: dict

    """
    print("\nSummary:")
    for item, amount in dct.items():
        if type(amount) == int or type(amount) == float:
            print("{} : {:.2f}".format(item, amount))
        else:
            print("{} : {}".format(item, amount))


if __name__ == "__main__":

    # Prepare header of csv for summarization.
    with open('logs/test_users_results' + '/output.csv', 'w', newline='') as csvfile:
        fieldnames = ["tester",
                      "test_type",
                      "timestamp",
                      "mean_d",
                      "mean_dw",
                      "% time_out_warning_zone",
                      "photo_score",
                      "time"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    # Loop all test users.
    for test_user in test_users:
        print(test_user)
        test_user_flight_logs_names = os.listdir('logs/test_users/' + test_user)
        test_user_flight_logs = []
        if (len(test_user_flight_logs_names)) == 0:
            continue

        # Prepare plot.
        fig, axes = plt.subplots(len(test_user_flight_logs_names), 1, squeeze=False, figsize=(15, 15))
        fig.subplots_adjust(hspace=0.5)
        fig.suptitle('User: ' + test_user, fontsize=16)

        # Loop all test user flights.
        for (flight_log_name, i) in zip(test_user_flight_logs_names, range(len(test_user_flight_logs_names))):
            test_user_flight_logs.append({'log': None,
                                          'summary': None})
            path = 'logs/test_users/' + test_user + '/' + flight_log_name
            try:
                open(path + '/summary.json')
            except:
                continue

            # Inits score 0 for the photos, then changed manually.
            # with open(path + '/photo_score.json', "w") as f:
            #     f.write('{"score" : 0}')

            # Extracts summary.
            with open(path + '/summary.json') as json_file:
                data = json.load(json_file)
                test_user_flight_logs[-1]['summary'] = data

                with open(path + '/photo_score.json') as photo_score_json:
                    print(path + '/photo_score.json')
                    photo_score_data = json.load(photo_score_json)
                    photo_score = photo_score_data["score"]
                # print(data)
                useful_data = {
                    "tester": test_user.split('-')[0],
                    "test_type": "assistent-" + test_user.split('-')[4],
                    "timestamp": flight_log_name,
                    "mean_d": data["mean_d"],
                    "mean_dw": data["mean_dw"],
                    "% time_out_warning_zone": data["% time_out_warning_zone"],
                    "photo_score": photo_score,
                    "time": int(data["time_out_warning_zone"] + data["time_in_warning_zone"])
                }
                print_inventory(useful_data)

            # Appends important outputs from the whole summarization.
            with open('logs/test_users_results' + '/output.csv', 'a', newline='') as csvfile:
                fieldnames = ["tester",
                              "test_type",
                              "timestamp",
                              "mean_d",
                              "mean_dw",
                              "% time_out_warning_zone",
                              "photo_score",
                              "time"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(useful_data)

            # Read flight log.
            fields = 'date,fly_time,fly_time_s,x,y,z,z_max,vx,vy,vz,vx_max,vy_max,vz_max,latitude,longitude,altitude,pitch,roll,yaw,cx,cy,cz,scx,scy,scz,d,dx,dy,dz,gc_pow_x,gc_pow_y,gc_pow_z,gpc_pow_x,gpc_pow_y,gpc_pow_z,gfc_pow_x,gfc_pow_y,gfc_pow_z'.split(
                ',')
            df = pd.read_csv(path + '/log.csv', skipinitialspace=True, usecols=fields)
            test_user_flight_logs[-1]['log'] = df

            # Plot absolut distance from the path.
            fly_time_s = df['fly_time_s'].tolist()
            d = df['d'].tolist()
            free_range = np.ones(len(d)) * 1
            warning_range = np.ones(len(d)) * 2
            axes[i, 0].plot(fly_time_s, d, color='b', label='distance')
            axes[i, 0].plot(fly_time_s, free_range, color='y', label='free_range')
            axes[i, 0].plot(fly_time_s, warning_range, color='r', label='warning_range')
            axes[i, 0].set_xlabel('time')
            axes[i, 0].set_ylabel('distance')
            axes[i, 0].grid(True)
            # axes[i, 0].legend('best')
            axes[i, 0].set_title(flight_log_name)

            plot_photos(user_name=test_user, flight_name=flight_log_name)

        handles, labels = axes[-1, 0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper right', prop={'size': 20})

        # Summary image of set of flights by one tester.
        fig.savefig('logs/test_users_results/distances/' + test_user + '-dist-summary.png')
