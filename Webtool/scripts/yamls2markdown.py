import os

import yaml
from snakemd import Inline, Paragraph, new_doc

EXCLUDED_FOLDERS = ["GoodXRTData", "NotionExport"]

REL_PATH = "../static/SourceData/"


def yaml2markdown(folder_path, yaml_info_dict):

    doc = new_doc()

    doc.add_heading(yaml_info_dict.get("event_name"))
    doc.add_paragraph(
        "The text files listed below were downloaded from papers on\
                [NASA/ADS](https://ui.adsabs.harvard.edu) and converted to the GRBSN\
                [format](https://github.com/GabrielF98/GRBSNWebtool/tree/master/Webtool/static/SourceData).\
            The 'Master.txt' file(s) are a combination of these text files and contain all\
            of the downloaded data for a paticular wavelength range."
    )
    if yaml_info_dict.get("filenames") is not None:
        for filename in yaml_info_dict.get("filenames"):
            doc.add_horizontal_rule()
            doc.add_heading(filename, 3)
            doc.add_paragraph(
                "**Source:** "
                + str(
                    yaml_info_dict.get("filenames")
                    .get(filename)
                    .get("sourceurl")
                )
            )
            doc.add_paragraph(
                "**Data-type:** "
                + str(
                    yaml_info_dict.get("filenames")
                    .get(filename)
                    .get("datatype")
                )
            )
            doc.add_paragraph("**Notes:**")
            # Extract and process notes from dictionary
            notes = (
                yaml_info_dict.get("filenames", {})
                .get(filename)
                .get("notes", "No notes.")
            )

            doc.add_raw(notes)

    # Write out to a file
    doc.dump(os.path.join(folder_path + "/readme"))


list_of_folder_paths = []
for folder in os.listdir(os.path.abspath(REL_PATH)):
    folder_path = os.path.join(os.path.abspath(REL_PATH), folder)
    if os.path.isdir(folder_path) and folder not in EXCLUDED_FOLDERS:
        list_of_folder_paths.append(folder_path)


for i, item in enumerate(list_of_folder_paths):
    yaml_path = os.path.join(item) + "/readme.yml"
    if os.path.exists(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as file:
            info_dict = yaml.safe_load(file)
            yaml2markdown(item, info_dict)
