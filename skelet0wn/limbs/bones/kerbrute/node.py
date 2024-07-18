import re

from bson.binary import Binary
from pymongo.database import Database
from pymongo.results import UpdateResult

from skelet0wn.limbs.bones import Bone


class Kerbrute(Bone):
    """:py:class:`Bone` wrapping Kerbrute, allowing for Active Directory user enumeration.
    Currently supports simple user enumeration only.
    """

    def __init__(self, mapping_file: str) -> None:
        super().__init__(
            interface_file="./skelet0wn/limbs/bones/kerbrute/interface.yml",
            docker_dockerfile_directory="./skelet0wn/limbs/bones/kerbrute/",
            docker_image_tag="skelet0wn/kerbrute",
            mapping_file=mapping_file,
        )

    def store_results(self, mongo_database: Database) -> None:
        with open(f"{self.output_dir}/output.txt", "r") as f:
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
                result: UpdateResult = mongo_database["users"].update_one(
                    query, update, upsert=True
                )
                self.log(f"Found valid user {username}@{domain}", level="DEBUG")
                if result.upserted_id:
                    self.log(f"Added user {username}@{domain}", level="DEBUG")

        with open(f"{self.output_dir}/output.txt", "rb") as f:
            rawOutput = Binary(f.read())
        mongo_database["files"].insert_one(
            {"filename": "kerbrute_userenum.txt", "content": rawOutput}
        )
        # store step metadata
        super().store_metadata(mongo_database)
