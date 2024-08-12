import os
import time
from abc import ABC, abstractmethod
from typing import Optional

from bson.objectid import ObjectId
from loguru import logger
from pymongo.database import Database
from pymongo.results import InsertOneResult


class Limb(ABC):
    """Base `skelet0wn` abstract class, superclass of every tool integrator (:py:class:`Bone`\) and logic element (:py:class:`Joint`\).

    Attributes:
        name (str): Name of the :py:class:`Limb` instance
        depth (int): Depth in the workflow tree, used for cleaner log rendering.
        output_dir (str): Location of output directory, specified and created recursively when parsing the workflow architecture.
        shared_dir (str): Location of shared directory, specified and created when starting the workflow. Used to share files between :py:class:`Limb`\s.
        logger (:py:class:`loguru.Logger`\): Binded log interface, parametrized for this specific :py:class:`Limb`\.
    """

    def __init__(self) -> None:
        """Minimal constructor, creating a temporary logger object"""
        self.logger = logger.bind(name="UNINIT".center(14), depth_pad="")

    @abstractmethod
    def run(self, skull: Database, run_id: str) -> None:
        """Base method for a Limb.

        Args:
            skull (:py:class:`pymongo.database.Database`\): MongoDB database to fetch the arguments from and store the results in.
            run_id (str): Unique identifier of this specific run. Necessary to reuse the same database in several runs.
        """
        pass

    def interrupt(self) -> None:
        """Sends an interruption signal to the Limb. No assumption is taken on its response to this signal."""
        pass

    def prepare_environment(
        self, output_dir: str, shared_dir: str, name: str = "n0"
    ) -> None:
        """Sets up the :py:class:`Limb` environment: private output directory, shared directory, hierarchical name.

        Args:
            output_dir (str): Private output directory. Children will live in subdirectories.
            shared_dir (str): Shared, flat directory for file sharing.
            name (str, optional): Hierarchical name of the :py:class:`Limb`\. Defaults to "n0".
        """
        self.name = name
        self.depth = name.count(".")
        self.output_dir = output_dir + "/" + self.name
        self.shared_dir = shared_dir
        self.logger = logger.bind(name=self.name.center(14), depth_pad=" " * self.depth)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if not os.path.exists(self.shared_dir):
            os.makedirs(self.shared_dir)

    def log(self, msg: str, depth_increment: int = 0, level: str = "INFO") -> None:
        """Helper to format and log messages according to :py:class:`Limb` depth.

        Args:
            msg (str): Message to be logged.
            depth_increment (int, optional): Increment of depth to add to :py:class:`Limb` depth. Defaults to 0.
            level (str, optional): Logging level to use.
        """
        self.logger.log(level, " " * (depth_increment + 1) + "* " + msg)

    def store_metadata(
        self,
        skull: Database,
        run_id: str,
        outputCollection: Optional[str] = None,
        outputID: Optional[ObjectId] = None,
        other_fields: dict = dict(),
    ) -> None:
        """Helper to store common:py:class:`Limb` metadata in MongoDB database.

        Args:
            skull (:py:class:`pymongo.database.Database`\): MongoDB database to store the data in.
            run_id (str): Unique identifier of this specific run. Necessary to reuse the same database in several runs.
            outputCollection (str | None, optional): Name of the collection where the :py:class:`Limb` stored its output, when relevant. Defaults to None.
            outputID (:py:class:`bson.objectid.ObjectId` | None, optional): ObjectId at which the :py:class:`Limb` stored its output, when relevant. Defaults to None.
            other_fields (dict, optional): Additional fields to store in the MongoDB Document. Defaults to dict().
        """
        steps_db = skull["steps"]
        fields = {
            "name": self.name,
            "class": self.__class__.__name__,
            "outputCollection": outputCollection,
            "outputID": outputID,
            "time": time.strftime("%Y%m%d-%H%M%S"),
            "run_id": run_id,
        }
        for field in other_fields:
            fields[field] = other_fields[field]
        insert_result: InsertOneResult = steps_db.insert_one(fields)
        if insert_result is None or insert_result.acknowledged is False:
            raise Exception("Could not insert element in steps")
