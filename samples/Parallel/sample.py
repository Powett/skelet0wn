import os
import time
from typing import Optional

from loguru import logger
from pymongo import MongoClient
from pymongo.results import InsertOneResult

from skelet0wn.limbs.bones import Nmap
from skelet0wn.limbs.joints import Parallel
from skelet0wn.utilities import logger_setup

logger_setup()
logger.level("INFO")
logger.info("########## Database setup")

# Connect to MongoDB
logger.info("* Connecting to client")
client: MongoClient = MongoClient("mongodb://localhost:27017/")
database_name = time.strftime("%Y%m%d-%H%M%S")

logger.info(f"  * Creating new database {database_name}... ")
mongo_database = client[database_name]


# Add an initial object
logger.debug("  * Inserting first object... ")
insert_result: Optional[InsertOneResult] = mongo_database["subnets"].insert_one(
    {"cidr": "192.168.56.1/27"}
)
if insert_result is None or insert_result.acknowledged is False:
    logger.error("Could not insert object")
    exit(1)
initialID = insert_result.inserted_id
# Define workflow and build Docker images
logger.info("########## Building workflow")

# POC - Parallel
workflow = Parallel(
    front=Nmap(mapping_file="./samples/Parallel/mappingNmap.yml"),
    back=Nmap(mapping_file="./samples/Parallel/mappingNmap2.yml"),
)

# Set names and create outputs folders
logger.info("* Setting names and creating output folders")
workflow.prepare_environment(
    output_dir=os.getcwd() + "/outputs", shared_dir=os.getcwd() + "/outputs/shared"
)
# Exec
logger.info("########## Running workflow")

try:
    workflow.run(mongo_database)
except Exception as exc:
    logger.info(f"Exception {exc}")
