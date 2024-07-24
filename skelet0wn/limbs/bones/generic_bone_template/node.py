from bson.binary import Binary
from pymongo.database import Database
from pymongo.results import InsertOneResult

from skelet0wn.limbs.bones import Bone
from skelet0wn.utilities import get_package_relative_path


class GenericBone(Bone):
    """Template :py:class:`Bone` provided to ease integration of new tools (here, reversing a file).
    Define here the :py:meth:`store_results()` method to process the tool-specific output.
    """

    def __init__(self, mapping_file: str) -> None:
        super().__init__(
            # Replace with actual path to Bone configuration
            interface_file=get_package_relative_path(
                "limbs/bones/generic_bone_template/interface.yml"
            ),
            docker_dockerfile_directory=get_package_relative_path(
                "limbs/bones/generic_bone_template/"
            ),
            docker_image_tag="skelet0wn/generic_bone_template",
            mapping_file=mapping_file,
        )

    # Implement here the tool-specific parsing and database feeding
    def store_results(self, mongo_database: Database, run_id: str) -> None:
        # parse tool-specific raw output
        with open(f"{self.output_dir}/output.txt", "rb") as f:
            outputRaw = Binary(f.read())

        # process output if needed

        # insert data in MongoDB Database
        insert_result: InsertOneResult = mongo_database["files"].insert_one(
            {
                "filename": "reverted_file.txt",
                "content": outputRaw,
                "content_decoded": outputRaw.decode(),
            }
        )
        # Assert the insertion was successful
        if insert_result.acknowledged is False:
            raise Exception("Could not feed raw output in database")
        childID = insert_result.inserted_id

        # store step metadata
        super().store_metadata(mongo_database, run_id, "files", childID)
