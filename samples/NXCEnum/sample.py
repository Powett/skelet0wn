import os
import time
from typing import Any, Callable, List, Optional

from loguru import logger
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.results import InsertOneResult

from skelet0wn.limbs.bones import Nmap, NxcSmb
from skelet0wn.limbs.joints import Sequence, Transformer
from skelet0wn.utilities import logger_setup

logger_setup()
logger.info("########## Database setup")

# Connect to MongoDB
logger.info("* Connecting to skull_client")
skull_client: MongoClient = MongoClient("mongodb://localhost:27017/")

# Set unique runID
run_id = time.strftime("%Y%m%d-%H%M%S")

# if no database was specified, create a new one
database_name = os.getenv("DATABASE_NAME")
if database_name is None:
    database_name = time.strftime("%Y%m%d-%H%M%S")
    logger.info(f"  * Creating new database {database_name}... ")
else:
    logger.info(f"  * Using existing database {database_name}... ")
skull = skull_client[database_name]

# Define workflow and build Docker images
logger.info("########## Building workflow")


# POC - Seq Nmap-Transfo-NXCUser-NXCShare
def transfo(l: List[Collection]) -> Any:
    logger.info(l)
    return " ".join([str(v["IP"]["ipv4"]) for v in l])


workflow = Sequence(
    children=[
        Nmap("./samples/NXCEnum/mappingNmap.yml"),
        Transformer(
            "machines", {"ports.445.status": "open"}, {"IP.ipv4": 1, "_id": 0}, transfo
        ),
        NxcSmb("./samples/NXCEnum/mappingNXC.yml"),
        NxcSmb("./samples/NXCEnum/mappingNXC2.yml"),
    ]
)

# Set names and create outputs folders
logger.info("* Setting names and creating output folders")
workflow.prepare_environment(
    output_dir=os.getcwd() + "/outputs", shared_dir=os.getcwd() + "/outputs/shared"
)
# Exec
logger.info("########## Running workflow")

try:
    workflow.run(skull, run_id)
except Exception as exc:
    logger.info(f"Exception {exc}")
