import os
import time

from loguru import logger
from pymongo import MongoClient

from skelet0wn.limbs.bones import Kerbrute
from skelet0wn.limbs.joints import DownloadFile, Sequence, UploadFile
from skelet0wn.utilities import logger_setup

logger_setup()
logger.info("########## Database setup")

# Connect to MongoDB
logger.info("* Connecting to client")
client: MongoClient = MongoClient("mongodb://localhost:27017/")
database_name = time.strftime("%Y%m%d-%H%M%S")

logger.info(f"  * Creating new database {database_name}... ")
mongo_database = client[database_name]


# Define workflow and build Docker images
logger.info("########## Building workflow")

# POC - Kerbrute
workflow = Sequence(
    children=[
        UploadFile("./samples/Kerbrute/userlist.txt", "userlist.txt"),
        DownloadFile("userlist.txt"),
        Kerbrute("./samples/Kerbrute/mappingKerbrute.yml"),
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
    workflow.run(mongo_database)
except Exception as exc:
    logger.info(f"Exception {exc}")
