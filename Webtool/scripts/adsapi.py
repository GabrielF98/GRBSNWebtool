"""
This script needs to be run to return the citation information from NASA ADS.
This is the data that eventually appears in the table on the event page.

Note that you need an ADS token saved in your environment as an env var called 'ADSAPI'.
"""

import json
import os
import re
import sqlite3

import pandas as pd
import requests
import yaml

DATABASE_RELPATH_STR = "../static/Masterbase.db"
SOURCE_DATA_RELPATH_STR = "../static/SourceData/"
CITATION_PATH = "../static/citations/"
ADS_TOKEN = os.environ["ADSAPI"]


def get_db_connection():
    """
    Connect to the master database.
    """
    print("Establishing an connection with the GRBSN database.")
    conn = sqlite3.connect(os.path.abspath(DATABASE_RELPATH_STR))
    conn.row_factory = sqlite3.Row
    print("Connection established\n")
    return conn


def bibcode_names(type):
    """
    Return ADS urls of the primary sources
    """
    conn = get_db_connection()
    urls1 = conn.execute(f"SELECT DISTINCT({type}) FROM SQLDataGRBSNe")
    urls2 = conn.execute("SELECT DISTINCT(source) FROM TrigCoords")
    urls3 = conn.execute("SELECT DISTINCT(source) FROM PeakTimesMags")
    urls = []

    for i in urls1:
        if i not in urls:
            urls.append(i)

    # We don't want to get the sources from TrigCoords and PeakTimesMags
    # if we are using this funcition for secondary sources.
    if type == "PrimarySources":
        for i in urls2:
            if i not in urls:
                urls.append(i)

        for i in urls3:
            if i not in urls:
                urls.append(i)

    bibcodes = []
    hyperlinks = []
    randoms = []
    for i in urls:
        if str(i[0])[0:10] == "https://ui":
            # Split the bibcode into a list by breaking it each time a / appears
            bibcodes.append(str(i[0]).split("/")[4].replace("%26", "&"))
            hyperlinks.append(str(i[0]))
        # Include anything without https://ui but dont go to ADS
        else:
            randoms.append(i[0])
    conn.close()

    return bibcodes, hyperlinks, randoms


def contact_nasa_ads(bibcode):
    # API Access
    # Some code copied from the howto for the ADS API (though some of it is mine too)
    # https://github.com/adsabs/adsabs-dev-api/blob/master/Converting_curl_to_python.ipynb
    print(f"Creating request for {bibcode['bibcode']} and dispatching to NASA ADS.")
    r = requests.post(
        "https://api.adsabs.harvard.edu/v1/export/custom",
        headers={
            "Authorization": "Bearer " + ADS_TOKEN,
            "Content-type": "application/json",
        },
        data=json.dumps(bibcode),
    )
    print(f"Reply received.")
    print(f'First Author: {re.split("[ ,]", r.json()["export"])[0]}')
    print(f'Year: {re.split("[ ,]", r.json()["export"])[-1]}')
    return r


def check_present(resource_url, dictionary):
    """
    Is this key already in the relevant dictionary.

    Returns True if it is, False otherwise.
    """

    if dictionary.get(resource_url) is None:
        return False
    else:
        return True


def return_author_year(response):
    out_dict = {}

    author_list = response.json()["export"]
    author_split = response.json()["export"].split(",")

    if len(author_split) > 2:
        out_dict["names"] = author_split[0] + " et al."
        out_dict["year"] = author_list[-5:-1]
    else:
        out_dict["names"] = author_list[:-6]
        out_dict["year"] = author_list[-5:-1]

    return out_dict


def grb_names():
    """
    # Get the names of all GRB-SNe in the webtool.
    """
    conn = get_db_connection()
    names = conn.execute("SELECT DISTINCT GRB, SNe FROM SQLDataGRBSNe")
    grbs = []
    for i in names:
        if str(i[0]) != "None" and str(i[1]) != "None":
            if str(i[1][:4]).isnumeric():
                grbs.append("GRB" + str(i[0]) + "-SN" + str(i[1]))
            else:
                grbs.append("GRB" + str(i[0]) + "-" + str(i[1]))

        elif str(i[1]) == "None":
            grbs.append("GRB" + str(i[0]))

        elif str(i[0]) == "None":
            if str(i[1][:4]).isnumeric():
                grbs.append("SN" + str(i[1]))
            else:
                grbs.append(str(i[1]))

    conn.close()

    return grbs


# MAIN PROGRAM
# Primary sources
print("\n==============================")
print("Beginning primary file sources.")
print("===============================\n")

# Get bibcodes.
print("Getting bibcodes\n")
bibcodes, hyperlinks, randoms = bibcode_names("PrimarySources")

with open(
    os.path.join(os.path.abspath(CITATION_PATH) + "/citations.json"),
    "r",
    encoding="utf-8",
) as file:
    dictionary = json.load(file)


for i, hyperlink in enumerate(hyperlinks):
    bibcode = {"bibcode": [str(bibcodes[i])], "format": "%m %Y"}
    if check_present(resource_url=hyperlink, dictionary=dictionary) is False:
        r = contact_nasa_ads(bibcode=bibcode)
        dictionary[str(hyperlinks[i])] = return_author_year(response=r)
    else:
        print(f"{bibcode['bibcode'][0]} is already in the database")

# Take care of the randoms
for i in range(len(randoms)):
    dictionary[randoms[i]] = randoms[i]

# Save the dictionary with json.dump()
with open(
    os.path.join(os.path.abspath(CITATION_PATH) + "/citations.json"),
    "w",
    encoding="utf-8",
) as file:
    cleaned_data = {k: v for k, v in dictionary.items() if k != "null"}
    json.dump(cleaned_data, file, indent=4, separators=(",", ": "))


# Secondary sources from the database.
print("\n============================")
print("Beginning secondary sources.")
print("============================\n")

# Get bibcodes
print("Getting bibcodes\n")
bibcodes2, hyperlinks2, randoms2 = bibcode_names("SecondarySources")

with open(
    os.path.join(os.path.abspath(CITATION_PATH) + "/citations2.json"),
    "r",
    encoding="utf-8",
) as file:
    dictionary2 = json.load(file)
for i, hyperlink in enumerate(hyperlinks2):
    bibcode = {"bibcode": [str(bibcodes2[i])], "format": "%m %Y"}
    if check_present(resource_url=hyperlink, dictionary=dictionary2) is False:
        r = contact_nasa_ads(bibcode=bibcode)
        dictionary2[str(hyperlinks2[i])] = return_author_year(response=r)
    else:
        print(f"{bibcode['bibcode'][0]} is already in the database")

# Take care of the randoms
for i in range(len(randoms2)):
    dictionary2[randoms2[i]] = randoms2[i]
# Save the dictionary with json.dump()
with open(
    os.path.join(os.path.abspath(CITATION_PATH) + "/citations2.json"),
    "w",
    encoding="utf-8",
) as file:
    cleaned_data = {k: v for k, v in dictionary2.items() if k != "null"}
    json.dump(cleaned_data, file, indent=4, separators=(",", ": "))


# Observation file citations
print("\n===================================")
print("Beginning observation file sources.")
print("===================================\n")
# Go to all the GRB-SN source files and get the names.
folder_names = grb_names()

# Get the bibcodes and hyperlinks
print("Getting bibcodes\n")
bibcodes3 = []
hyperlinks3 = []
randoms3 = []
for folder in folder_names:
    with open(os.path.join("../static/SourceData/" + folder + "/readme.yml")) as file:
        grbsn_info = yaml.safe_load(file)

    if grbsn_info.get("filenames") is None:
        citations = []
    else:
        citations = [
            str(grbsn_info.get("filenames").get(filename).get("sourceurl"))
            for filename in list(grbsn_info.get("filenames", {}).keys())
        ]

    for i in citations:
        if str(i)[0:10] == "https://ui":
            # Split the bibcode into a list by breaking it each time a / appears
            bibcodes3.append(str(i).split("/")[4].replace("%26", "&"))
            hyperlinks3.append(str(i))

        elif "tns" in str(i):
            randoms3.append(str(i))


# Primary sources
with open(
    os.path.join(os.path.abspath(CITATION_PATH) + "/citations(ADSdatadownloads).json"),
    "r",
    encoding="utf-8",
) as file:
    dictionary3 = json.load(file)

for i, hyperlink in enumerate(hyperlinks3):
    bibcode = {"bibcode": [str(bibcodes3[i])], "format": "%m %Y"}
    if check_present(resource_url=hyperlink, dictionary=dictionary3) is False:
        r = contact_nasa_ads(bibcode=bibcode)
        dictionary3[str(hyperlinks3[i])] = return_author_year(response=r)
    else:
        print(f"{bibcode['bibcode'][0]} is already in the database")

# Deal with the randoms
for i in range(len(randoms3)):
    dictionary3[randoms3[i]] = {"names": "Transient Name Server", "year": ""}

# Save the dictionary with json.dump()
with open(
    os.path.join(os.path.abspath(CITATION_PATH) + "/citations(ADSdatadownloads).json"),
    "w",
    encoding="utf-8",
) as file:
    cleaned_data = {k: v for k, v in dictionary3.items() if k != "null"}
    json.dump(cleaned_data, file, indent=4, separators=(",", ": "))
