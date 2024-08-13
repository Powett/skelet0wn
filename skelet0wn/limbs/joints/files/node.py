from os.path import isfile
from typing import Optional

from bson.binary import Binary
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import InsertOneResult

from skelet0wn.limbs import Limb
from skelet0wn.limbs.joints import Joint


class UploadFile(Joint):
    """Logic element allowing to upload a file from host to `skelet0wn` database.
    To use the file as input to another :py:class:`Limb`, a :py:class:`ShareFile` :py:class:`Limb` should be inserted in-between.

    Attributes:
        file_path (str): Full host path to the uploaded file.
        file_name (str): Name to store the file in the `skelet0wn` database under.
    """

    def __init__(self, file_path: str, file_name: str) -> None:
        """Minimal constructor.

        Args:
            file_path (str): Full host path to the uploaded file.
            file_name (str): Name to store the file in the `skelet0wn` database under.
        """
        super().__init__()
        self.file_path = file_path
        self.file_name = file_name

    def run(self, skull: Database, run_id: str) -> None:
        self.log(f"Running limb {self.name}, {self.__class__.__name__}")
        try:
            assert isfile(self.file_path)
            with open(self.file_path, "rb") as f:
                data = Binary(f.read())
        except Exception as exc:
            raise Exception(f"Could not read file {self.file_path}: {exc}")
        insert_result: InsertOneResult = skull["files"].insert_one(
            {
                "filename": self.file_name,
                "content": data,
                "content_decoded": data.decode(),
            }
        )
        if insert_result is None:
            raise Exception(f"Could not download file '{self.file_path}' to database")
        self.store_metadata(skull, run_id, "files", insert_result.inserted_id)
        self.log("OK, exiting", level="SUCCESS")


class ShareFile(Joint):
    """Logic element allowing to download a file from `skelet0wn` database to the shared folder.

    Attributes:
        file_name (str): Name of the file to download from the `skelet0wn` database.
        file_path (str): Host path to the downloaded file in the shared folder. Dynamically generated at workflow running time.
    """

    def __init__(self, file_name: str) -> None:
        super().__init__()
        self.file_name = file_name

    def run(self, skull: Database, run_id: str) -> None:
        self.log(f"Running limb {self.name}, {self.__class__.__name__}")
        result: Optional[Collection] = skull["files"].find_one(
            {"filename": self.file_name}
        )
        try:
            assert result is not None
            with open(self.file_path, "wb") as f:
                f.write(result["content"])
        except Exception as exc:
            raise Exception(f'Could not download file "{self.file_name}": {exc}')
        filepath = f"/mnt/shared/{self.file_name}"
        insert_result: InsertOneResult = skull["temp"].insert_one(
            {"result": {"filepath": filepath}}
        )
        if insert_result is None or insert_result.acknowledged is False:
            raise Exception("Could not insert element in temp")
        self.store_metadata(
            skull,
            run_id,
            outputCollection="temp",
            outputID=insert_result.inserted_id,
        )
        self.log(
            f"Downloaded {self.file_name} in {filepath}, insert_result name in temp",
            level="DEBUG",
        )
        self.log("OK, exiting", level="SUCCESS")

    def prepare_environment(
        self, output_dir: str, shared_dir: str, name: str = "n0"
    ) -> None:
        """Sets up the :py:class:`Limb` environment: private output directory, shared directory, hierarchical name.
        This overrides the :py:meth:`Limb.prepare_environment()` method to set the destination file path, computed at runtime.

        Args:
            output_dir (str): Private output directory. Children will live in subdirectories.
            shared_dir (str): Shared, flat directory for file sharing.
            name (str, optional): Hierarchical name of the limb. Defaults to "n0".
        """
        super().prepare_environment(
            output_dir=output_dir,
            shared_dir=shared_dir,
            name=name,
        )
        self.file_path = f"{self.shared_dir}/{self.file_name}"
