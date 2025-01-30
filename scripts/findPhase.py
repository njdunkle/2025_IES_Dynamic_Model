# -*- coding: utf-8 -*-
"""
Authors: Nicholas Dunkle, Alex Wheeler, Vik Singh
Advisor: Dr. Sandra Bogetic

This script will write create the directories and write a matlab file for each dicretory
This script will not sumit the files however. That will be dine in a separate bash script.

"""

# import packages
import numpy as np
import pandas as pd
import re
import sys
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def sine_wave_fit(x, a, b, c, d):
    # x is time (should be off by a 1000)
    # a is amplitude (k)
    # b is the frequency (rad/sec)
    # c is the phase shift (rad)
    # d is the steady state values before hand
    result = a * np.sin(b * (x) + c) + d
    return result


numberOfRuns = 150

freq_space = np.logspace(
    -4, 2, num=numberOfRuns
)  # must be the same in both runFreq.py and findPhase.py
phase_orig = []

orig_stdout = sys.stdout
output_file = open("data_fit.py", "w+")
sys.stdout = output_file

thermgain = []
thermphase = []
elecogain = []
elecophase = []
hydrogain = []
hydrophase = []

for runNumber in range(
    1, numberOfRuns + 1
):  # , runNumber in zip(freq_space, range(1, numberOfRuns+1)):

    workPath = "../run" + "{:.0f}".format(
        runNumber
    )  # "../f%f" % freq_space[runNumber-1]
    dataFileName = "/run" + "{:.0f}".format(runNumber) + "_res.csv"
    freq_in = freq_space[runNumber - 1]
    simData = pd.read_csv("{}".format(workPath) + dataFileName)

    # simData headers contain conflicting characters that need removing

    simDataHeader = str(list(simData.columns))
    chars_to_remove = ["[", "]", ".", "(", ")", "_", "'"]
    rx = "[" + re.escape("".join(chars_to_remove)) + "]"
    newSimDataHeader = re.sub(rx, "", simDataHeader)

    newSimDataHeader = newSimDataHeader.replace(" ", "")
    newSimDataHeader = newSimDataHeader.split(",")

    simData.columns = newSimDataHeader

    # Data analysis
    time = simData["time"]
    therm = simData["CoreNomPower"]
    eleco = simData["RBOPQ_turbine"]
    hydro = simData["HySmdot_H2_out"]

    # find the index when the sine wave transite starts
    begin = next(x for x, val in enumerate(time) if val > 1000)
    time[:] = [number - 1000 for number in time]

    # Fit the sine wave
    p0 = [300e-5, freq_in, 0, 1]  # first guess
    bottom_bound = (
        freq_in - 1e-10
    )  # this is the frequncy bound, cant pass a single value so the bounds are for >1/1000%
    top_bound = freq_in + 1e-10
    # fit values
    popt, pcov = curve_fit(
        sine_wave_fit,
        time[begin:],
        power[begin:],
        p0,
        bounds=(
            (1e-5, bottom_bound, -1.570796327, 0.995),
            (1000e-5, top_bound, 1.570796327, 1.015),
        ),
    )
    # print(popt)
    gain.append(popt[0] / (1e-5))  # store gain is relative to input terms
    phase.append(popt[2] * 180 / np.pi)  # store phase in terms of degree

print("This file was made by findPhase.py")

print("Thermal Power Gain")
print(thermgain)
print("Thermal Power Phase")
print(thermphase)
print("Electric Power Gain")
print(elecogain)
print("Electric Power Phase")
print(elecophase)
print("H2 Production Gain")
print(hydrogain)
print("H2 Production Phase")
print(hydrophase)

sys.stdout = orig_stdout
output_file.close()
