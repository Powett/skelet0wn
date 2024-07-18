from pymongo.database import Database

from skelet0wn.limbs.bones import Bone


class GenericBone(Bone):
    """Template :py:class:`Bone` provided to ease integration of new tools.
    Define here the :py:meth:`store_results()` method to process the tool-specific output.
    """

    def __init__(self, mapping_file: str) -> None:
        super().__init__(
            interface_file="./skelet0wn/limbs/bones/generic_tool_template/interface.yml",
            docker_dockerfile_directory="./skelet0wn/limbs/bones/generic_tool_template/",
            docker_image_tag="skelet0wn/generic_tool_template",
            mapping_file=mapping_file,
        )

    # Implement here the tool-specific parsing and database feeding
    def store_results(self, mongo_database: Database) -> None:
        pass
