import xml.etree.ElementTree as ET

from bson.binary import Binary
from pymongo.database import Database
from pymongo.results import InsertOneResult

from skelet0wn.limbs.bones import Bone


class GetNPUsers(Bone):
    """:py:class:`Bone` wrapping impacket's GetNPUsers.py, allowing for ASREPRoast attacks testing."""

    def __init__(self, mapping_file: str) -> None:
        super().__init__(
            interface_file="./skelet0wn/limbs/bones/getnpusers/interface.yml",
            docker_dockerfile_directory="./skelet0wn/limbs/bones/getnpusers/",
            docker_image_tag="skelet0wn/getnpusers",
            mapping_file=mapping_file,
        )

    # Implement here the tool-specific parsing and database feeding
    def store_results(self, mongo_database: Database, run_id: str) -> None:
        # parse raw
        with open(f"{self.output_dir}/output.txt", "rb") as f:
            outputRaw = Binary(f.read())

        insert_result: InsertOneResult = mongo_database["files"].insert_one(
            {
                "filename": "tgt.txt",
                "content": outputRaw,
                "content_decoded": outputRaw.decode(),
            }
        )
        if insert_result is None or insert_result.acknowledged is False:
            raise Exception("Could not feed raw output in database")
        childID = insert_result.inserted_id

        # store step metadata
        super().store_metadata(mongo_database, run_id, "files", childID)
