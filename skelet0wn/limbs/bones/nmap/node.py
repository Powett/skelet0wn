import xml.etree.ElementTree as ET

from bson.binary import Binary
from pymongo.database import Database
from pymongo.results import InsertOneResult

from skelet0wn.exceptions import *
from skelet0wn.limbs.bones import Bone
from skelet0wn.utilities import get_package_relative_path


def parse_xml(xml_file: str) -> ET.ElementTree:
    # Open output file
    with open(xml_file) as f:
        return ET.parse(xml_file)


class Nmap(Bone):
    """:py:class:`Bone` wrapping impacket's Nmap, allowing for network scanning.
    Currently supports most runtime options, and parsing of hostnames, hosts status, ports status.
    """

    def __init__(self, mapping_file: str) -> None:
        super().__init__(
            interface_file=get_package_relative_path("limbs/bones/nmap/interface.yml"),
            docker_dockerfile_directory=get_package_relative_path("limbs/bones/nmap/"),
            docker_image_tag="skelet0wn/nmap",
            mapping_file=mapping_file,
        )

    def store_results(self, skull: Database, run_id: str) -> None:
        db_machines = skull["machines"]

        # open file
        try:
            tree = parse_xml(f"{self.output_dir}/output.xml")
        except Exception as exc:
            raise BoneError(
                name=self.name,
                class_name=self.__class__.__name__,
                msg=f"Error parsing {self.output_dir}/output.xml: {exc}",
            )
        try:
            root = tree.getroot()

            # parse results
            for t_host in root.iter("host"):
                add_field = t_host.find("address")
                assert add_field is not None
                add = add_field.get("addr")

                # Create machine
                status_field = t_host.find("status")
                assert status_field is not None

                query = {"IP.ipv4": add}
                update = {
                    "$set": {
                        "IP": {"ipv4": add},
                        "status": status_field.get("state"),
                    }
                }
                db_machines.update_one(query, update, upsert=True)

                # Add hostnames
                for hnames in t_host.iter("hostnames"):
                    for hname in hnames.iter("hostname"):
                        db_machines.update_one(
                            {"IP.ipv4": add},
                            {"$addToSet": {"hostnames": hname}},
                            upsert=True,
                        )

                # Add ports
                for t_port in t_host.iter("port"):
                    state_field = t_port.find("state")
                    assert state_field is not None
                    service_field = t_port.find("service")
                    assert service_field is not None
                    db_machines.update_one(
                        {"IP.ipv4": add},
                        {
                            "$set": {
                                f"ports.{t_port.get('portid')}": {
                                    "status": state_field.get("state"),
                                    "service": service_field.attrib,
                                }
                            }
                        },
                        upsert=True,
                    )

            # parse raw
            with open(f"{self.output_dir}/output.xml", "rb") as f:
                outputRaw = Binary(f.read())
            insert_result: InsertOneResult = skull["files"].insert_one(
                {
                    "filename": "nmap_run.xml",
                    "content": outputRaw,
                    "content_decoded": outputRaw.decode(),
                }
            )
            assert insert_result.acknowledged is True
            childID = insert_result.inserted_id

        except Exception as exc:
            raise Exception("Could not feed raw output in database: {exc}")

        # store step metadata
        super().store_metadata(skull, run_id, "files", childID)
