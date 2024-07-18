# skelet0wn

## Overview
**skelet0wn** is a cutting-edge pentesting automation framework designed to streamline and automate the entire cyber kill chain. As the core engine of an open-source project, skelet0wn enables penetration testers to efficiently execute complex workflows using docker-encapsulated tools and logic elements.

## Features
- **Full Automation**: Automate all steps of the cyber kill chain from reconnaissance to post-exploitation.
- **Docker Encapsulation**: Seamlessly run various pentesting tools encapsulated in Docker containers for consistent and reproducible environments.
- **Complex Workflows**: Create and manage intricate workflows combining multiple tools and logic elements.
- **Extensibility**: Easily extend and customize with additional tools and scripts to fit specific testing needs.
- **Open Source**: Completely open-source, fostering community contributions and transparency.

## Documentation
[![Documentation Status](https://readthedocs.org/projects/skelet0wn/badge/?version=latest)](https://skelet0wn.readthedocs.io/en/latest/?badge=latest)


## Getting Started
### Prerequisites
- A docker client (preferably in [rootless](https://docs.docker.com/engine/security/rootless/) mode, else using the **skelet0wn** framework will require sudo privileges)
- A MongoDB instance running (see [Setting up MongoDB](#setting-up-mongodb) for quickstart script)

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/Powett/skelet0wn.git
    cd skelet0wn
    ```
2. Install python packages (virtual environment recommended)
    ```bash
    python3 -m pip install -r requirements.txt
    ```

## Usage
### Setting up MongoDB
An existing running MongoDB server can be used.  

Else, a starter script launching a docker instance can be found [here](./misc/mongo_cmd.sh).

**[WARNING]** Please be aware that this script might start a non-official MongoDB docker image (in case of missing AVX CPU support).  
**[WARNING]** Please be aware that the created MongoDB instance is not persisted upon container stop. Data will be lost.

### Designing a workflow
Sample workflows are provided in [./samples/](./samples/), ready to be used or copied for modification.
Please refer to the [documentation](TODO) for further explanations.

### Running a workflow
As all **skelet0wn** classes herit from the same `Limb` class, running a worfklow is simply done by calling `run(mongo_db)` on the top-level `Limb`.

Example (from the provided [minimal workflow example](./samples/Minimal/sample.py))

```python
import os
import time

from pymongo import MongoClient

from limbs.bones import Nmap
from limbs.joints import Sequence

# Connect to MongoDB
client: MongoClient = MongoClient("mongodb://localhost:27017/")
database_name = time.strftime("%Y%m%d-%H%M%S")
db_client = client[database_name]


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
workflow.run(db_client)

```

## TODO
- [ ] Writing detailed documentation
- [ ] Integrating more `Bone`s and `Joint`s
- [ ] Adding a GUI for easier workflow generation
- [ ] ...

## Contributing
Contributions are welcome! Please file a pull request with detailed improvements/modifications and I'll review it.

Please make sure your pull request is properly documented, typed and formatted. Use the [provided formatting script](./misc/format.sh).

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Contact
For questions or support, please open an issue.
