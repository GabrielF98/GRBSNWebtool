import pandas as pd
import os
import yaml
import ast

EXCLUDED_FOLDERS = ["GoodXRTData"]
CWD = os.getcwd()
folders = []
for i in os.listdir("../static/SourceData"):
    folder_path = os.path.abspath(os.path.join("../static/SourceData", i))
    if os.path.isdir(folder_path) and folder_path not in EXCLUDED_FOLDERS:
        folders.append(folder_path)

for folder in folders:
    os.chdir(folder)
    if os.path.exists("OpenSNPhotometry.csv"):
        open_sn = pd.read_csv("OpenSNPhotometry.csv", sep=",")

        optical_file_sources = []
        if os.path.exists("readme.yml"):
            with open("readme.yml", "r", encoding="utf-8") as file:
                readme_dict = yaml.safe_load(file)
                for filename in (readme_dict.get("filenames") or {}).keys():
                    if "optical" in str(filename).lower():
                        print(str(filename))
                        optical_file_sources.append(
                            readme_dict.get("filenames")
                            .get(str(filename))
                            .get("sourceurl")
                        )

        unique_refs = open_sn["refs"].unique().tolist()
        print(unique_refs)
        # for ref in unique_refs:
        #     print(ref)
        #     for dictt in ast.literal_eval(ref):
        #         if dictt.get("url") in optical_file_sources:
        #             print("Yes")
        #             try:
        #                 unique_refs.remove(ref)
        #             except ValueError as e:
        #                 if str(e) != "list.remove(x): x not in list":
        #                     raise

        num = 1
        for ref in unique_refs:
            new_df = pd.DataFrame()
            new_df = open_sn.loc[open_sn["refs"] == ref].copy()

            new_df_2 = pd.DataFrame()

            new_df_2["date"] = new_df["time"].copy().to_numpy()
            new_df_2["date_unit"] = "MJD"
            new_df_2["mag"] = new_df["magnitude"].copy().to_numpy()
            new_df_2["dmag"] = new_df["e_magnitude"].copy().to_numpy()
            new_df_2["mag_limit"] = 0
            new_df_2["mag_unit"] = ["unspecified"] * len(new_df_2["date_unit"])
            new_df_2["mag_type"] = ["apparent"] * len(new_df_2["date_unit"])
            new_df_2["band"] = new_df["band"].copy()
            new_df_2["instrument"] = ["NaN"] * len(new_df_2["date_unit"])

            new_filename = (
                f"{folder.split('/')[-1]}_Optical_{len(optical_file_sources)+num}.txt"
            )
            new_df_2.to_csv(
                new_filename,
                index=False,
                sep="\t",
                na_rep="NaN",
            )

            readme_dict["filenames"][new_filename] = []

            # with open("readme.yml", "w") as outfile:
            #     yaml.dump(readme_dict, outfile, default_flow_style=False)
            num += 1
    os.chdir(CWD)
