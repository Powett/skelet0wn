import xml.etree.ElementTree as ET

from bson.binary import Binary
from pymongo.database import Database
from pymongo.results import InsertOneResult

from skelet0wn.limbs.bones import Bone
from skelet0wn.utilities import get_package_relative_path


class GetUserSPNs(Bone):
    """:py:class:`Bone` wrapping impacket's GetUserSPNs.py, allowing for Kerberoast attacks testing."""

    def __init__(self, mapping_file: str) -> None:
        super().__init__(
            interface_file=get_package_relative_path(
                "limbs/bones/getuserspns/interface.yml"
            ),
            docker_dockerfile_directory=get_package_relative_path(
                "limbs/bones/getuserspns/"
            ),
            docker_image_tag="skelet0wn/getuserspns",
            mapping_file=mapping_file,
        )

    # Implement here the tool-specific parsing and database feeding
    def store_results(self, skull: Database, run_id: str) -> None:
        # parse raw
        with open(f"{self.output_dir}/userspns_output.txt", "rb") as f:
            outputRaw = Binary(f.read())

        insert_result: InsertOneResult = skull["files"].insert_one(
            {
                "filename": "tgs.txt",
                "content": outputRaw,
                "content_decoded": outputRaw.decode(),
            }
        )
        if insert_result.acknowledged is False:
            raise Exception("Could not feed raw output in database")
        childID = insert_result.inserted_id

        # store step metadata
        super().store_metadata(skull, run_id, "files", childID)
