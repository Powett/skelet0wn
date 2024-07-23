import threading
from typing import Any, Callable, List, Optional

from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.results import InsertOneResult

from skelet0wn.limbs import Limb
from skelet0wn.limbs.joints import Joint


class Transformer(Joint):
    """Logic element allowing to perform a MongoDB query and transform the output, to reuse as input to another :py:class:`Limb`\.

    Attributes:
        collection (str): MongoDB collection to run the query on.
        filter_crit (dict, optional): Filter criterion to use in the query. Defaults to dict().
        projection (dict, optional): Projection criterion to use in the query. Defaults to dict().
        transformation (func(List[Collection] -> Any), optional): Transformation function to apply to the fetched data. Defaults to `lambda x:x[0]`\.
            Takes in input a list of :py:class:`pymongo.collection.Collection` query results, and returns an arbitrary-typed object, that will be stored in the database.
    """

    def __init__(
        self,
        collection: str,
        filter_crit: dict = dict(),
        projection: dict = dict(),
        transformation: Callable[[List[Collection]], Any] = lambda x: x[0],
    ):
        """Minimal constructor.

        Args:
            collection (str): MongoDB collection to run the query on.
            filter_crit (dict, optional): Filter criterion to use in the query. Defaults to dict().
            projection (dict, optional): Projection criterion to use in the query. Defaults to dict().
            transformation (func(List[Collection] -> Any), optional): Transformation function to apply to the fetched data. Defaults to `lambda x:x[0]`\.
        """
        super().__init__()
        self.collection = collection
        self.filter_crit = filter_crit
        self.projection = projection
        self.transformation = transformation

    def run(self, mongo_database: Database, run_id: str) -> None:
        self.log(f"Running limb {self.name}, {self.__class__.__name__}")
        db_collection = mongo_database[self.collection]
        cursor: Cursor = db_collection.find(self.filter_crit, self.projection)
        values = [v for v in cursor]
        self.log("Fetched data, transforming...", depth_increment=1, level="DEBUG")
        result: Any = self.transformation(values)

        self.log(f"Obtained {result}", depth_increment=1, level="DEBUG")
        insert_result: InsertOneResult = mongo_database["temp"].insert_one(
            {"result": result}
        )
        if insert_result is None or insert_result.acknowledged is False:
            raise Exception("Could not insert element in temp")
        self.store_metadata(
            mongo_database,
            run_id,
            outputCollection="temp",
            outputID=insert_result.inserted_id,
        )
        self.log("OK, exiting", level="SUCCESS")
