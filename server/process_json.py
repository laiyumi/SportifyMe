import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter


def smooth_value(values, threshold=3, sigma=1):
    values = values[values != 0]
    mean_value = np.mean(values)
    std_value = np.std(values)
    z_scores = np.abs((values - mean_value) / std_value)
    clean_values = values[z_scores < threshold]
    smooth_values = gaussian_filter(clean_values, sigma=sigma)

    return smooth_values


def get_squat_num(json_fname):
    with open(json_fname, 'r') as file:
        data = json.load(file)

    l = []
    r = []
    for tp in data:
        l.append(tp[23]['y'])
        r.append(tp[24]['y'])
    l = smooth_value(np.array(l))
    r = smooth_value(np.array(r))

    peaks_l = find_peaks(l,prominence=0.01)[0]
    peaks_r = find_peaks(r,prominence=0.01)[0]

    num = np.floor((len(peaks_l)+len(peaks_r))/2)

    return num


def get_step_out_num(json_fname):
    with open(json_fname, 'r') as file:
        data = json.load(file)

    l = []
    r = []
    for tp in data:
        l.append(tp[23]['y'])
        r.append(tp[24]['y'])
    l = smooth_value(np.array(l))
    r = smooth_value(np.array(r))

    peaks_l = find_peaks(-l,prominence=0.1)[0]
    peaks_r = find_peaks(-r,prominence=0.1)[0]

    num = np.floor((len(peaks_l)+len(peaks_r))/2)

    return num


def get_jumping_jack_num(json_fname):
    with open(json_fname, 'r') as file:
        data = json.load(file)

    l = []
    r = []
    for tp in data:
        l.append([tp[15]['x'],tp[15]['y']])
        r.append([tp[16]['x'],tp[16]['y']])

    l = np.array(l)
    r = np.array(r)

    distances = smooth_value(np.linalg.norm(l - r, axis=1))

    peaks = find_peaks(-distances,prominence=0.3)[0]

    num = len(peaks)
    return num