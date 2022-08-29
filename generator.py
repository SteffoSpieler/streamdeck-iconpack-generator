# Licensed under the EUPL, Version 1.2
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
#
# https://joinup.ec.europa.eu/software/page/eupl
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licence is distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the Licence for the specific language governing permissions and
# limitations under the Licence.
import json
import logging
import os
from json import JSONDecodeError

import click
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(omit_repeated_times=False)]
)
logger = logging.getLogger("rich")


def is_iconpack_valid(folder: str) -> bool:
    """
    Checks if the iconpack is valid.
    """

    # If item is not a directory, skip it
    if not os.path.isdir("./iconpacks/" + folder):
        return False

    # If iconpack.json doesn't exist, skip it
    if not os.path.isfile("./iconpacks/" + folder + "/iconpack.json"):
        logger.warning(f"No iconpack.json found in iconpacks/{folder}")
        return False

    # Check if iconpack.json is valid
    try:
        with open("./iconpacks/" + folder + "/iconpack.json") as f:
            data = f.read()
            json.loads(data)
    except JSONDecodeError as e:
        logger.warning(f"Invalid JSON in iconpacks/{folder}/iconpack.json")
        return False

    # If iconpack.json doesn't contain manifest or id, return false
    if "manifest" not in json.loads(data) or "id" not in json.loads(data):
        logger.warning(f"Missing manifest or id in iconpacks/{folder}/iconpack.json")
        return False

    return True


def get_available_iconpacks() -> list:
    """
    Returns a list of available icon packs in the iconpacks directory.
    """

    iconpacks = []

    # If iconpacks directory doesn't exist, create it
    if not os.path.exists("./iconpacks"):
        os.mkdir("./iconpacks")

    # Loop through iconpacks directory
    for folder in os.listdir("./iconpacks"):
        if is_iconpack_valid(folder):
            iconpacks.append(folder)

    return iconpacks


def generate_pack(folder: str):
    """
    Generates a pack.
    """

    if not is_iconpack_valid(folder):
        logger.error(f"Invalid iconpack: {folder}")
        return

    with open("./iconpacks/" + folder + "/iconpack.json") as f:
        data = f.read()
        iconpack_config = json.loads(data)

        # Delete existing pack folder with all files
        if os.path.exists(f"./packs/{iconpack_config['id']}.sdIconPack"):
            os.system(f"rm -rf \"./packs/{iconpack_config['id']}.sdIconPack\"")
            logging.debug(f"Deleted existing pack: {iconpack_config['id']}.sdIconPack")

        os.mkdir(f"./packs/{iconpack_config['id']}.sdIconPack")
        logging.debug(f"Creating pack directory: {iconpack_config['id']}.sdIconPack")

        # Save manifest
        with open(f"./packs/{iconpack_config['id']}.sdIconPack/manifest.json", "w") as manifest_file:
            manifest_file.write(json.dumps(iconpack_config["manifest"]))
            logging.debug(f"Saving manifest")

        # Copy icon file
        if os.path.isfile(f"./iconpacks/{folder}/{iconpack_config['manifest']['Icon']}"):
            os.system(f"cp \"./iconpacks/{folder}/{iconpack_config['manifest']['Icon']}\" \"./packs/{iconpack_config['id']}.sdIconPack/icon.png\"")
            logging.debug(f"Copying icon file")

        # Go through all icons in the iconpack
        icons: list = []
        for root, dirs, files in os.walk(f"./iconpacks/{folder}/icons"):
            for file in files:
                if file.endswith(".png") or file.endswith(".jpg"):
                    icon_path = root.replace(f"./iconpacks/{folder}/icons", "")[1:]
                    icons.append({"path": f"{icon_path}/{file}"})

                    # Copy icon file
                    if not os.path.exists(f"./packs/{iconpack_config['id']}.sdIconPack/icons/{icon_path}"):
                        os.mkdir(f"./packs/{iconpack_config['id']}.sdIconPack/icons/{icon_path}")

                    os.system(f"cp \"./iconpacks/{folder}/icons/{icon_path}/{file}\" \"./packs/{iconpack_config['id']}.sdIconPack/icons/{icon_path}/{file}\"")
                    logging.debug(f"Found icon: {icon_path}/{file}")

        # Save icons.json
        with open(f"./packs/{iconpack_config['id']}.sdIconPack/icons.json", "w") as icons_file:
            logging.debug(f"Saving icons.json")
            icons_file.write(json.dumps(icons, indent=4))

        logging.info(f"Generated pack: {iconpack_config['id']}.sdIconPack with {len(icons)} icons")
        logging.info(f"Use it by copying it to %appdata%/Elgato/StreamDeck/IconPacks (on windows)")


@click.command()
@click.option("--iconpack", "-i", help="The iconpack to use")
def main(iconpack: str):
    """
    Generates the iconpack.
    """

    # If no iconpack is specified, print available iconpacks
    if not iconpack:
        logger.info("Available iconpacks:")
        for iconpack in get_available_iconpacks():
            logger.info(f"- {iconpack}")
        # ToDo: Make iconpack selectable with pick (https://github.com/wong2/pick)
        return

    # If iconpack is specified, but it's not valid, print error message
    if not is_iconpack_valid(iconpack):
        logger.error(f"Invalid iconpack: {iconpack}")
        return

    generate_pack(iconpack)


if __name__ == "__main__":
    main()
