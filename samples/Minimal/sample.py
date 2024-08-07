import os
import time

from pymongo import MongoClient

from skelet0wn.limbs.bones import Nmap
from skelet0wn.limbs.joints import Sequence

# Connect to MongoDB
client: MongoClient = MongoClient("mongodb://localhost:27017/")

# Set unique runID
run_id = time.strftime("%Y%m%d-%H%M%S")

# if no database was specified, create a new one
database_name = os.getenv("DATABASE_NAME")
if database_name is None:
    database_name = time.strftime("%Y%m%d-%H%M%S")
mongo_database = client[database_name]

mongo_database = client[database_name]
# Create workflow (two Nmap nodes with static parameters only)
workflow = Sequence(
    children=[
        Nmap(mapping_file="./samples/Minimal/mappingNmap22.yml"),
        Nmap(mapping_file="./samples/Minimal/mappingNmap80.yml"),
    ]
)

# Set names and create outputs folders
workflow.prepare_environment(
    output_dir=os.getcwd() + "/outputs", shared_dir=os.getcwd() + "/outputs/shared"
)

# Run workflow
workflow.run(mongo_database, run_id)
