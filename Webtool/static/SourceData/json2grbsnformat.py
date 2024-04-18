import glob
import json
import os
import shutil

import numpy as np
import pandas as pd
from astropy.time import Time

# Conversions from OAC JSON (https://github.com/astrocatalogs/schema) to GRBSN webtool format ()
# OAC - GRBSN
# spectra - None, just signifies it should be sent to a Spectra_Master file.
# time - date - the time of observation
# e_time - Note: error on the time, needs to be a range for the date.
# instrument - instrument
# telescope - instrument
# filename - name of the original file the spectrum came from.
# u_errors - flux_unit - Note: Units of the flux errors
# u_fluxes - flux_unit - Note: Flux units
# u_time - date_unit - Note: They count time in MJD so we will have to convert a bit.
# deredshifted - NA. Note: If present we need to quote the wavelengths as rest-frame.
# u_wavelengths - wavelength_unit
# data - NA. Note: In OAC this is a list of wavelengths and fluxes (possibly also errors). Wavelengths could be either rest or observed (see above).
# source - reference / Note: If there's more than one source, we will choose the paper on ADS if available


def convert_key(key_list, data_dict, filename):
    # New dict for the new spectra file
    spectrum = {}
    # The first key is the name of the event, the type is the second key
    event = key_list[0]
    data_kind = key_list[1]

    # Find out how much data there is
    if "data" in key_list:
        data = data_dict[event][data_kind].get("data")

        shape = [len(row) for row in zip(*data)]

        length = shape[0]

        if len(shape) == 2:
            wlen_list, flux_list = zip(*data)
            wlen_arr = np.array(wlen_list, dtype=np.float32)
            flux_arr = np.array(flux_list, dtype=np.float32)
            spectrum["flux"] = flux_arr

        elif len(shape) == 3:
            wlen_list, flux_list, flux_err_list = zip(*data)
            wlen_arr = np.array(wlen_list, dtype=np.float32)
            flux_arr = np.array(flux_list, dtype=np.float32)
            flux_err_arr = np.array(flux_err_list, dtype=np.float32)
            spectrum["flux"] = flux_arr
            spectrum["dflux"] = flux_err_arr

        else:
            print("Something has gone wrong")

        # Are the wavelengths rest frame or not?
        if str(data_dict[event][data_kind].get("deredshifted")) is True:
            spectrum["rest_wavelength"] = wlen_arr

        else:
            spectrum["obs_wavelength"] = wlen_arr

            # Redshift
            z = data_dict[event][data_kind].get("redshift")
            if z is None:
                z = input("What is the refshift")

            spectrum["redshift"] = length * [z]
            spectrum["rest_wavelength"] = wlen_arr / (1 + float(z))

    # Convert time to the date column
    if "time" in key_list:
        # Find out the unit
        date_unit = data_dict[event][data_kind].get("u_time")

        # Convert the date unit to utc
        if date_unit == "MJD":
            t = Time(data_dict[event][data_kind].get("time"), format="mjd")
            print(t.fits)

        else:
            print("Something is wrong with the time unit")

        # Print out if there's a time error
        if data_dict[event][data_kind].get("e_time") is not None:
            print("The time has an error!")
        spectrum["date_unit"] = length * ["utc"]
        spectrum["date"] = length * [t.fits]

    # Instrument
    spectrum["instrument"] = length * [
        data_dict[event][data_kind].get("telescope", "")
        + data_dict[event][data_kind].get("instrument", "")
    ]

    # units
    if (
        data_dict[event][data_kind].get("u_fluxes") == "erg/s/cm2/A"
        or data_dict[event][data_kind].get("u_fluxes") == "erg/s/cm^2/Angstrom"
    ):
        spectrum["flux_unit"] = "erg/s/cm2/A"

    elif data_dict[event][data_kind].get("u_fluxes") == "Uncalibrated":
        spectrum["flux_unit"] = "uncalibrated"
    else:
        print("The unit for flux isnt what was expected")

    spectrum["wavelength_unit"] = str(
        data_dict[event][data_kind].get("u_wavelengths")
    ).lower()

    # Deal with source
    if data_dict[event][data_kind].get("source"):
        source_list = data_dict[event][data_kind].get("source")

        for source in source_list:
            if "adsabs" in source["url"]:
                if (
                    source["url"]
                    == "https://ui.adsabs.harvard.edu/abs/2012PASP..124..668Y/abstract"
                ):
                    continue
                else:
                    spectrum["reference"] = length * [source["url"]]

    # Save to df
    spec_df = pd.DataFrame.from_dict(spectrum)
    spec_df.to_csv(f"{filename[:-5]}.txt", index=False, sep="\t", na_rep="NaN")


def load_json(file):
    with open(file, "r") as f:
        file_dict = json.load(f)
    return file_dict


def find_keys(data_dict):

    for key in data_dict.keys():
        if type(data_dict[key]) is dict:
            all_keys.append(key)
            find_keys(data_dict[key])
        else:
            all_keys.append(key)
    return all_keys


pwd = os.getcwd()
print(pwd)
directory = "/Users/gabriel/GitHub/Database/Webtool/static/SourceData"
folder_list = []
for thing in os.listdir(directory):
    if os.path.isdir(os.path.join(directory, thing)):
        folder_list.append(thing)

for folder in folder_list:
    print(folder)
    if "SN" in folder or "GRB" in folder:
        # Go to each folder.
        os.chdir(os.path.join(directory, folder))

        # Find all .json files
        json_list = glob.glob("*.json")

        # Perform operations on all json files
        # for file in json_list:
        #     if 'Spectra' in file:
        #         file_dict = load_json(file)
        #         all_keys = []
        #         list_of_keys = find_keys(file_dict)
        #         convert_key(list_of_keys, file_dict, file)

        # Update the filesources csv
        filesources_txt = glob.glob("*filesources*")
        filesources = pd.read_csv(filesources_txt[0])
        filesources["Filename"] = filesources["Filename"].fillna("NaN")

        txt_list = glob.glob("*OpenSNSpectra*.txt")
        for file in txt_list:
            info = pd.read_csv(file, delimiter="\t")
            reference = info["reference"][0]
            print(file[:-4], reference)
            print(filesources["Filename"])
            filesources.loc[
                (filesources["Filename"].str.contains(file[:-4])), "Filename"
            ] = file
            filesources.loc[
                (filesources["Filename"].str.contains(file[:-4])), "Reference"
            ] = reference

        filesources.to_csv(filesources_txt[0], index=False)

        # Shuttle all json files to the OriginalFormats folder
        # for file in json_list:
        #     try:
        #         shutil.move(file, 'OriginalFormats/')
        #     except FileNotFoundError:
        #         os.mkdir('OriginalFormats/')
        #         shutil.move(file, 'OriginalFormats/')

        # Return to the folder where you are running this code.
        os.chdir(pwd)
