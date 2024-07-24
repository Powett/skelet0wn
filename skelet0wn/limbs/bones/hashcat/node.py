import re
import xml.etree.ElementTree as ET
from typing import Optional

from bson.binary import Binary
from pymongo.database import Database
from pymongo.results import InsertOneResult

from skelet0wn.limbs.bones import Bone
from skelet0wn.utilities import get_package_relative_path


class Hashcat(Bone):
    """:py:class:`Bone` wrapping Hashcat, allowing for password hash cracking.
    Currently supports modes 18200 (TGT) and 13100 (TGS) in dictionnary mode, with optional rules file.
    """

    def __init__(self, mapping_file: str) -> None:
        super().__init__(
            interface_file=get_package_relative_path(
                "limbs/bones/hashcat/interface.yml"
            ),
            docker_dockerfile_directory=get_package_relative_path(
                "limbs/bones/hashcat/"
            ),
            docker_image_tag="skelet0wn/hashcat",
            mapping_file=mapping_file,
        )

    # Implement here the tool-specific parsing and database feeding
    def store_results(self, mongo_database: Database, run_id: str) -> None:
        # parse raw
        with open(f"{self.output_dir}/output.txt", "rb") as f:
            outputRaw = Binary(f.read())
        with open(f"{self.output_dir}/output.txt", "r") as f:
            tickets = f.readlines()

        regexes = {
            "18200": r"\$krb5asrep\$\d*\$([^\@]*)@([^\:]*):[0-9a-f]*\$[0-9a-f]*:(.*)",
            "13100": r"\$krb5tgs\$[^\$]*\$\*([^\$]*)\$([^\$]*)\$[^\$]*\$[0-9a-f]*\$[0-9a-f]*:(.*)",
            "default": r":()()([^:]*)$",
        }

        for ticket in tickets:
            if self.fetched_values["format_code"] in regexes:
                reg = regexes[self.fetched_values["format_code"]]
            else:
                reg = regexes["default"]
            match = re.match(reg, ticket)
            if match:
                username, domain, password = (
                    match.group(1),
                    match.group(2).lower(),
                    match.group(3),
                )
                mongo_database["users"].update_one(
                    {"username": username, "domain": domain},
                    {
                        "$set": {
                            "username": username,
                            "domain": domain,
                            "password": password,
                        }
                    },
                    upsert=True,
                )
                self.log(
                    f"Found password: {domain}/{username}:{password}", level="DEBUG"
                )

        insert_result: Optional[InsertOneResult] = mongo_database["files"].insert_one(
            {
                "filename": "cracked_file.txt",
                "content": outputRaw,
                "content_decoded": outputRaw.decode(),
            }
        )
        if insert_result is None or insert_result.acknowledged is False:
            raise Exception("Could not feed raw output in database")
        childID = insert_result.inserted_id

        # store step metadata
        super().store_metadata(mongo_database, run_id, "files", childID)
