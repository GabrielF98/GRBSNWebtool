# for this script to work you must be in the source data folder

# importing packages

import os
from os.path import dirname
from pathlib import Path

import matplotlib.pyplot as pl
import numpy as np
import pandas as pd

# define the function for changing filter names
# we have a list of conditions to change filter name sif these conditions are met


def standard_filters(data):
    # empty list for the new renamed bands
    newbands = []
    # current band list
    bands = data["band"]
    # in some cases we need to check the instrument too
    instr = data["instrument"]
    #'all the conditions for correcly renaming the filters'
    # included instrument in sime cases eg getting confused between UVOT u and sloan u (u')
    for i in range(0, len(bands)):
        if bands[i] == "SDSS-g" or bands[i] == "g$\\arcmin$" or bands[i] == "g′":
            newbands.append(str("g'"))
            continue
        elif bands[i] == "g'" and instr[i] == "GROND":
            newbands.append(str("g"))
            continue
        elif bands[i] == "SDSS-r" or bands[i] == "r$\\arcmin$" or bands[i] == "r′":
            newbands.append(str("r'"))
            continue

        elif bands[i] == "r'" and instr[i] == "GROND":
            newbands.append(str("r"))
            continue
        elif (
            bands[i] == "SDSS-i"
            or bands[i] == "i$\\arcmin$"
            or bands[i] == "i′"
            or bands[i] == "ii"
        ):
            newbands.append(str("i'"))
            continue
        elif bands[i] == "i'" and instr[i] == "GROND":
            newbands.append(str("g"))
            continue
        elif bands[i] == "SDSS-z" or bands[i] == "z\\arcmin" or bands[i] == "z′":
            newbands.append(str("z'"))
            continue
        elif bands[i] == "z'" and instr[i] == "GROND":
            newbands.append(str("z"))
            continue
        elif bands[i] == "u" and instr[i] != "UVOT":
            newbands.append("u'")
            continue
        elif bands[i] == "u'" and instr[i] == "GROND":
            newbands.append(str("u"))
            continue
        elif (bands[i] == "white" or bands[i] == "White") and instr[i] == "UVOT":
            newbands.append("UWh")
            continue
        elif bands[i] == "W" or bands[i] == "white":
            newbands.append("White")
            continue
        elif (
            bands[i] == "w1"
            or bands[i] == "W1"
            or bands[i] == "Uw1"
            or bands[i] == "uw1"
            or bands[i] == "uvw1"
            or bands[i] == "UVW1 (260 nm) Filter"
            or bands[i] == "UVW1"
        ):
            newbands.append("UW1")
            continue
        elif (
            bands[i] == "w2"
            or bands[i] == "W2"
            or bands[i] == "Uw2"
            or bands[i] == "uw2"
            or bands[i] == "uvw2"
            or bands[i] == "UVW2 (198 nm) Filter"
            or bands[i] == "UVW2"
        ):
            newbands.append("UW2")
            continue
        elif (
            bands[i] == "m1"
            or bands[i] == "M1"
            or bands[i] == "Um1"
            or bands[i] == "um1"
            or bands[i] == "uvm1"
            or bands[i] == "UVM1"
        ):
            newbands.append("UM1")
            continue
        elif (
            bands[i] == "m2"
            or bands[i] == "M2"
            or bands[i] == "Um2"
            or bands[i] == "um2 "
            or bands[i] == "uvm2"
            or bands[i] == "UVM2"
            or bands[i] == "UVM2 (220 nm) Filter"
        ):
            newbands.append("UM2")
            continue
        elif (bands[i] == "u" or bands[i] == "U" or bands[i] == "uvu") and (
            instr[i] == "UVOT" or instr[i] == "Swift/UVOT"
        ):
            newbands.append("UVU")
            continue
        elif (bands[i] == "b" or bands[i] == "B" or bands[i] == "uvb") and (
            instr[i] == "UVOT" or instr[i] == "Swift/UVOT"
        ):
            newbands.append("UVB")
            continue
        elif (bands[i] == "v" or bands[i] == "V" or bands[i] == "uvv") and (
            instr[i] == "UVOT" or instr[i] == "Swift/UVOT"
        ):
            newbands.append("UVV")
            continue
        elif bands[i] == "Ic" or bands[i] == "I_{C}":
            newbands.append("I_{c}")
            continue
        elif bands[i] == "UKIRTJ":
            newbands.append("J")
            continue
        elif bands[i] == "UKIRTH":
            newbands.append("H")
            continue
        elif bands[i] == "UKIRTK":
            newbands.append("K")
            continue
        elif (
            bands[i] == "Ks"
            or bands[i] == "K_{\\rm s}"
            or bands[i] == "$K_{\\rm s}$"
            or bands[i] == "K_{special}"
            or bands[i] == "K_{s]}"
            or bands[i] == "ks"
            or bands[i] == "k_{s}"
        ):
            newbands.append("K_{s}")
            continue
        elif bands[i] == "Js" or bands[i] == "J_{\\rm s}" or bands[i] == "J_{special}":
            newbands.append("J_{s}")
            continue
        elif bands[i] == "Rs" or bands[i] == "R_{\\rm s}" or bands[i] == "R_{special}":
            newbands.append("R_{s}")
            continue
        elif (
            bands[i] == "Rc"
            or bands[i] == "R_{\\rm c}"
            or bands[i] == "RC"
            or bands[i] == "R_{C}"
        ):
            newbands.append("R_{c}")
            continue
        elif bands[i] == "Clear":
            newbands.append("clear")
            continue
        elif (
            bands[i] == "CR"
            or bands[i] == "cr"
            or bands[i] == "Cr"
            or bands[i] == "C_R"
        ):
            newbands.append("C_{r}")
        elif bands[i] == "Gunn i":
            newbands.append("I")
            continue
        elif bands[i] == "Y" and instr[i] == "RATIR":
            newbands.append("y")
            continue
        elif bands[i] == "ACS/F606W":
            newbands.append("F606W")
            continue
        elif bands[i] == "ACS/F435W":
            newbands.append("F435W")
            continue
        elif bands[i] == "WFC3/UVIS/F336W":
            newbands.append("F336W")
            continue
        elif bands[i] == "WFC3/IR/F125W":
            newbands.append("F125W")
            continue
        elif bands[i] == "WFC3/IR/G102":
            newbands.append("G102")
            continue
        else:
            # if none of the bands meet these conditions we keep
            newbands.append(bands[i])
            continue

    return newbands


# go to source data folder with all the data
myPath = Path("../static/SourceData").resolve()

# get a list of all the folders in this path (all data for each transient)
subfolders = [f.name for f in os.scandir(myPath) if f.is_dir()]
for i in subfolders:
    # enter into each folder in source data to look for the optical master
    folderpath = os.path.join(myPath, i)
    print(folderpath)
    for file in os.listdir(folderpath):
        # check only text files that are optical master
        if file.lower().find("optical") != -1 and os.path.splitext(file)[1] == ".txt":
            print(file)
            # opens optical master
            filepath = os.path.join(folderpath, file)
            dd = pd.read_csv(filepath, delimiter="\t")
            ## checking the bands named correctly
            # print(file)
            # band_list =  list( dict.fromkeys(dd['band']))

            # replace the old bands with the new
            newfilter = standard_filters(dd)
            dd["band"] = newfilter

            dd.to_csv(filepath, sep="\t", index=False, na_rep="NaN")
