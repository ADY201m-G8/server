import os
import shutil

import requests

from src import DATA_URL


def prepare_data() -> None:
    response = requests.get(DATA_URL)

    with open("data.zip", "wb") as file:
        file.write(response.content)

    shutil.unpack_archive("data.zip", "./")
    os.remove("data.zip")


if __name__ == "__main__":
    prepare_data()
