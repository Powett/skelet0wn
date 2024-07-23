import os
import time
from typing import Optional

from loguru import logger
from pymongo import MongoClient
from pymongo.results import InsertOneResult

from skelet0wn.limbs.bones import Nmap
from skelet0wn.limbs.joints import Sequence
from skelet0wn.utilities import logger_setup

logger_setup()
logger.level("INFO")
logger.info("########## Database setup")

# Connect to MongoDB
logger.info("* Connecting to client")
client: MongoClient = MongoClient("mongodb://localhost:27017/")

# Set unique runID
run_id = time.strftime("%Y%m%d-%H%M%S")

# if no database was specified, create a new one
database_name = os.getenv("DATABASE_NAME")
if database_name is None:
    database_name = time.strftime("%Y%m%d-%H%M%S")
    logger.info(f"  * Creating new database {database_name}... ")
else:
    logger.info(f"  * Using existing database {database_name}... ")
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

# POC - Sequences
# - n0 : will proceed until last child, independantly of the children statuses
#   - n0.0 : will stop on first failure (here, n0.0.0)
#       - n0.0.0 : will fail due to unavailable field
#       - n0.0.1 : will not be run
#   - n0.1 : will succeed
#   - n0.2 : will stop on first success (here, n0.2.0)
#       - n0.2.0 : will succeed
#       - n0.2.1 : will not be run
workflow = Sequence(
    children=[
        Sequence(
            children=[
                Nmap(mapping_file="./samples/Sequences/mappingNmapFail.yml"),
                Nmap(mapping_file="./samples/Sequences/mappingNmap.yml"),
            ],
            stop_on_failure=True,
        ),
        Nmap(mapping_file="./samples/Sequences/mappingNmap.yml"),
        Sequence(
            children=[
                Nmap(mapping_file="./samples/Sequences/mappingNmap.yml"),
                Nmap(mapping_file="./samples/Sequences/mappingNmapFail.yml"),
            ],
            stop_on_success=True,
        ),
    ],
    stop_on_failure=False,
    stop_on_success=False,
)

# Set names and create outputs folders
logger.info("* Setting names and creating output folders")
workflow.prepare_environment(
    output_dir=os.getcwd() + "/outputs", shared_dir=os.getcwd() + "/outputs/shared"
)
# Exec
logger.info("########## Running workflow")

try:
    workflow.run(mongo_database, run_id)
except Exception as exc:
    logger.info(f"Exception {exc}")
