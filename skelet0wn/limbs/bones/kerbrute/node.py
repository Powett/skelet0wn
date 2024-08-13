import re

from bson.binary import Binary
from pymongo.database import Database
from pymongo.results import InsertOneResult, UpdateResult

from skelet0wn.limbs.bones import Bone
from skelet0wn.utilities import get_package_relative_path


class Kerbrute(Bone):
    """:py:class:`Bone` wrapping Kerbrute, allowing for Active Directory user enumeration.
    Currently supports simple user enumeration only.
    """

    def __init__(self, mapping_file: str) -> None:
        super().__init__(
            interface_file=get_package_relative_path(
                "limbs/bones/kerbrute/interface.yml"
            ),
            docker_dockerfile_directory=get_package_relative_path(
                "limbs/bones/kerbrute/"
            ),
            docker_image_tag="skelet0wn/kerbrute",
            mapping_file=mapping_file,
        )

    def store_results(self, skull: Database, run_id: str) -> None:
        with open(f"{self.output_dir}/kerbrute_output.txt", "r") as f:
            lines = f.readlines()

        user_regex = r".*VALID USERNAME:\s+([^@]*)@(.*)"
        for line in lines:
            match = re.match(user_regex, line)
            if match:
                username, domain = match.group(1), match.group(2).lower()
                query = {"username": username}
                update = {
                    "$set": {
                        "username": username,
                        "domain": domain,
                    }
                }
                result: UpdateResult = skull["users"].update_one(
                    query, update, upsert=True
                )
                self.log(f"Found valid user {username}@{domain}", level="DEBUG")
                if result.upserted_id:
                    self.log(f"Added user {username}@{domain}", level="DEBUG")

        with open(f"{self.output_dir}/kerbrute_output.txt", "rb") as f:
            outputRaw = Binary(f.read())
        insert_result: InsertOneResult = skull["files"].insert_one(
            {
                "filename": "kerbrute_userenum.txt",
                "content": outputRaw,
                "content_decoded": outputRaw.decode(),
            }
        )
        if insert_result is None or insert_result.acknowledged is False:
            raise Exception("Could not insert element in files")
        # store step metadata
        self.store_metadata(
            skull,
            run_id,
            outputCollection="files",
            outputID=insert_result.inserted_id,
        )
