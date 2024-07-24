import re
import sqlite3
import xml.etree.ElementTree as ET
from typing import Optional

from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import UpdateResult

from skelet0wn.limbs.bones import Bone
from skelet0wn.utilities import get_package_relative_path


class NxcSmb(Bone):
    """:py:class:`Bone` wrapping NetExec in SMB mode, allowing for shares and users enumeration.
    Currently supports scanning with and without username/password, and parsing shares or users (not simultaneously).
    """

    def __init__(self, mapping_file: str) -> None:
        super().__init__(
            interface_file=get_package_relative_path(
                "limbs/bones/nxc_smb/interface.yml"
            ),
            docker_dockerfile_directory=get_package_relative_path(
                "limbs/bones/nxc_smb/"
            ),
            docker_image_tag="skelet0wn/nxc_smb",
            mapping_file=mapping_file,
        )

    def store_results(self, mongo_database: Database, run_id: str) -> None:
        db_machines = mongo_database["machines"]
        conn = sqlite3.connect(f"{self.output_dir}/default/smb.db")
        cursor = conn.cursor()

        # Query relevant sql dbs
        try:
            cursor.execute("SELECT * FROM hosts")
            rows = cursor.fetchall()
            self.log(f"Got data from NXC SMB scanning: {rows}", level="TRACE")

            # Get column names from the cursor description
            column_names = [description[0] for description in cursor.description]
            for row in rows:
                fields = dict()
                for i, field in enumerate(column_names):
                    fields[field] = row[i]

                # Reformatting fields
                reformatted_fields = dict()
                for field in ["domain", "dc", "os"]:
                    reformatted_fields[field] = fields[field]
                    fields.pop(field)
                ip = fields.pop("ip")
                hostname = fields.pop("hostname")
                # Put remainder in proper service document
                reformatted_fields["services.SMB"] = fields

                # MongoDB query
                query = {"IP.ipv4": ip}
                # Update operation
                update = {
                    "$set": reformatted_fields,
                    "$addToSet": {"hostnames": hostname},
                }
                self.log(
                    f"Adding hostname {hostname} and {fields} to {ip}", level="TRACE"
                )
                # Perform the upsert operation
                result: UpdateResult = db_machines.update_one(
                    query, update, upsert=True
                )

        except sqlite3.Error as e:
            self.log(f"An error occurred: {e}", level="WARNING")
        finally:
            # Close the cursor and connection
            cursor.close()
            conn.close()
        if "--users" in self.built_command and "--shares" in self.built_command:
            self.log(
                "Please do not use --shares and --users at the same time!",
                level="ERROR",
            )
            return

        # parse enumerated users
        if "--users" in self.built_command:
            lines = self.docker_run_logs
            found_users = False
            header_regex = r"SMB\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+)\s+([^ ]+)\s+(-Username-)\s+(-Last PW Set-)\s+(-BadPW-)\s+(-Description-)"
            user_regex = r"SMB\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+)\s+([^ ]+)\s+([^ ]+)\s+((<never>)|(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d))\s+(0|1) *(.*)"
            for line in lines:
                if re.match(header_regex, line):
                    found_users = True
                    continue
                if found_users:
                    user_match = re.match(user_regex, line)
                    if user_match:
                        ip, port, hostname, username, last_set, badPW, description = (
                            user_match.group(1),
                            user_match.group(2),
                            user_match.group(3),
                            user_match.group(4),
                            user_match.group(5),
                            user_match.group(8),
                            user_match.group(9),
                        )
                        query = {"username": username}
                        update = {
                            "$set": {
                                "hostname": hostname,
                                "username": username,
                                "last_pw_set": last_set,
                                "badPW": badPW,
                                "description": description,
                            }
                        }
                        # try to fetch domain
                        filter_crit = {"hostnames": hostname}
                        projection = {"domain": 1}
                        domain_result: Optional[Collection] = mongo_database[
                            "machines"
                        ].find_one(filter=filter_crit, projection=projection)
                        if domain_result is not None:
                            domain = domain_result["domain"]
                            update["$set"]["domain"] = domain.lower()

                        result = mongo_database["users"].update_one(
                            query, update, upsert=True
                        )
                        if result.upserted_id:
                            self.log(f"Added user {username}", level="DEBUG")
                    else:
                        self.log(
                            f'Stopped parsing for users on "{line}"', level="DEBUG"
                        )
                        found_users = False

        # parse enumerated shares
        if "--shares" in self.built_command:
            lines = self.docker_run_logs
            found_shares = False
            header_regex = r"SMB\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+)\s+([^ ]+)\s+(-----)\s+(-----------)\s+(------)"
            share_regex = r"SMB\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+)\s+([^ ]+)\s+([^ ]+)\s+((READ|),*(WRITE|))\s+(.*)"
            for line in lines:
                if re.match(header_regex, line):
                    found_shares = True
                    continue
                if found_shares:
                    share_match = re.match(share_regex, line)
                    if share_match:
                        ip, port, hostname, share_name, permissions, remark = (
                            share_match.group(1),
                            share_match.group(2),
                            share_match.group(3),
                            share_match.group(4),
                            share_match.group(7),
                            share_match.group(8),
                        )
                        self.log(f"Found share {share_name}", level="DEBUG")
                        query = {"IP.ipv4": ip}
                        update = {
                            "$set": {
                                f"services.SMB.shares.{share_name}": {
                                    "permissions": permissions,
                                    "remark": remark,
                                }
                            },
                            "$addToSet": {
                                "hostnames": hostname,
                            },
                        }
                        result = mongo_database["machines"].update_one(
                            query, update, upsert=True
                        )
                        if result.upserted_id:
                            self.log(
                                f"Added share {share_name }to  {ip}", level="DEBUG"
                            )
                    else:
                        self.log(
                            f'Stopped parsing for shares on "{line}"', level="DEBUG"
                        )
                        found_shares = False

        # store step metadata
        super().store_metadata(mongo_database, run_id)
