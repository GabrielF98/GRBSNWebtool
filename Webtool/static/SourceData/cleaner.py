import os

EXCLUDE = [".DS_Store"]
for folder in os.listdir("."):
    if folder not in EXCLUDE and os.path.isdir(folder):
        for file in os.listdir(os.path.abspath(folder)):
            if os.path.exists(
                os.path.join(os.path.abspath(folder) + "/readme.txt")
            ):
                os.remove(
                    os.path.join(os.path.abspath(folder) + "/readme.txt")
                )
            elif os.path.exists(
                os.path.join(
                    os.path.abspath(folder) + "/" + folder + "filesources.csv"
                )
            ):
                print("removing")
                os.remove(
                    os.path.join(
                        os.path.abspath(folder)
                        + "/"
                        + folder
                        + "filesources.csv"
                    )
                )
