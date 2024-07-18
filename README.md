# skelet0wn

## Overview
*skelet0wn* is a cutting-edge pentesting automation framework designed to streamline and automate the entire cyber kill chain. As the core engine of an open-source project, skelet0wn enables penetration testers to efficiently execute complex workflows using docker-encapsulated tools and logic elements.

## Features
- **Full Automation**: Automate all steps of the cyber kill chain from reconnaissance to post-exploitation.
- **Docker Encapsulation**: Seamlessly run various pentesting tools encapsulated in Docker containers for consistent and reproducible environments.
- **Complex Workflows**: Create and manage intricate workflows combining multiple tools and logic elements.
- **Extensibility**: Easily extend and customize with additional tools and scripts to fit specific testing needs.
- **Open Source**: Completely open-source, fostering community contributions and transparency.

## Documentation
[![Documentation Status](https://readthedocs.org/projects/skelet0wn/badge/?version=latest)](https://skelet0wn.readthedocs.io/en/latest/?badge=latest)

## Content
The content of this repository is as follows:
```bash
.
├── docs/                                   # Sphinx documentation folder
├── LICENSE                                 # License file (MIT)
├── misc/                                   # Helper scripts
│   ├── build_all_bones.sh                  # (pre-)Build all Bone docker images 
│   ├── build_bone.sh                       # (pre-)Build specific Bone docker image
│   ├── format.sh                           # Format .py files
│   ├── mongodb_quickstart.sh               # Quickstart a MongoDB docker instance
│   ├── test.sh                             # (DEBUG) Run all samples
│   └── test_short.sh                       # (DEBUG) Run some samples
├── README.md                               # This file
├── requirements.txt                        # PIP requirements
├── samples/                                # Sample workflow provided as examples
│   ├── ASREPRoast/                         # TGS offline cracking
│   ├── Kerberoast/                         # TGT offline cracking
│   ├── Kerbrute/                           # Kerberos user enumeration
│   ├── Minimal/                            # Minimalistic sample (Nmap)
│   ├── NXCEnum/                            # NetExec user and SMB shares enumeration
│   ├── Parallel/                           # Sample to test the Parallel Joint
│   └── Sequences/                          # Sample to test the Sequence Joint (several configurations)
└── skelet0wn/                              # Main module folder
    ├── exceptions.py                       # Custom exception types
    ├── limbs/                              # Skelet0wn's base elements 
    │   ├── bones/                          # Skelet0wn's integrated tools
    │   │   ├── bone.py                     # Base class for integrated tools
    │   │   ├── generic_bone_template/      # Template for Bone integration
    │   │   ├── getnpusers/                 # Impacket's GetNPUsers
    │   │   ├── getuserspns/                # Impacket's GetUserSPNs
    │   │   ├── hashcat/                    # Hashcat, hash cracker
    │   │   ├── kerbrute/                   # Kerbrute, Kerberos enumerating tool
    │   │   ├── nmap/                       # Nmap, network scanning tool
    │   │   └── nxc_smb/                    # NetExec (SMB only), SMB enumerator and vuln scanner
    │   ├── joints/                         # Skelet0wn's logic elements
    │   │   ├── files/                      # Upload files to skelet0wn, share files from a Limb to others
    │   │   ├── joint.py                    # Base class for logic elements
    │   │   ├── parallel/                   # Run two Limb in parallel (back and fore-ground)
    │   │   ├── sequence/                   # Run Limbs sequentially
    │   │   └── transformer/                # Perform a MongoDB query and transform the output
    │   └── limb.py                         # Base skelet0wn class
    └── utilities.py                        # Miscellaneous functions
```

## Getting Started
### Prerequisites
- docker installed (preferably in [rootless](https://docs.docker.com/engine/security/rootless/) mode, otherwise using the *skelet0wn* framework will require sudo privileges)
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
### Setting up MongoDB
An existing running MongoDB server can be used.  

Else, a starter script launching a docker instance can be found [here](./misc/mongodb_quickstart.sh).

```bash
bash ./misc/mongodb_quickstart.sh
```

**[WARNING]** Please be aware that this script might start a non-official MongoDB docker image (in case of missing AVX CPU support).  
**[WARNING]** Please be aware that the created MongoDB instance is not persisted upon container stop. Data will be lost.

## Usage

### Designing a workflow
Sample workflows are provided in [./samples/](./samples/), ready to be used or copied for modification.

Example (from the provided [minimal workflow example](./samples/Minimal/sample.py)), decomposed:

1) Import the needed `Limb`s
```python
from limbs.bones import Nmap
from limbs.joints import Sequence
```
2) Connect to MongoDB database (should be running already)
```python
client: MongoClient = MongoClient("mongodb://localhost:27017/")
database_name = time.strftime("%Y%m%d-%H%M%S")
db_client = client[database_name]
```
3) Create your workflow: use `Joint`s to perform control-flow and logic operations, and `Bone`s to run tools. Provide `Bone`s with static configuration files (see TBD) and `Joint`s with specific configuration files/parameters.
```python
workflow = Sequence(
    children=[
        Nmap(mapping_file="./samples/Minimal/mappingNmap22.yml"),
        Nmap(mapping_file="./samples/Minimal/mappingNmap80.yml"),
    ]
)
```
4) Setup the workflow's working directory and names: every `Limb` will have its own working subdirectory (isolated from others), mounted within the docker container (if any). The `Limb` naming and directory generation is automatic, using the workflow topology.
```python
workflow.prepare_environment(
    output_dir=os.getcwd() + "/outputs",
    shared_dir=os.getcwd() + "/outputs/shared"
)
```
5) Run workflow: As all *skelet0wn* classes herit from the same `Limb` class, running a worfklow is simply done by calling `run(mongo_db)` on the top-level `Limb`.
```python
# Run workflow
workflow.run(db_client)
```

### Running the workflow
When running from source, make sure to set the following environment variables:
- `LOGURU_LEVEL`: Logging level, either `"TRACE"`, `"DEBUG"`, `"INFO"` (default), `"WARNING"` or `"ERROR"`.
- `PYTHONPATH=$PATH_TO_SKELET0WN_REPO`: Base directory for Python module fetching, should be set to `$PWD` to allow `import skelet0wn` statements to be correctly handled.

Please refer to the [documentation](https://skelet0wn.rtfd.io) for further explanations.

## Integrating/Modifying a `Limb`
The process is fairly similar to integrate and modify a `Limb`.

### Integrating/Modifying a `Joint`
As of now, `Joint`s bear little constraint nor organisation. Feel free to implement any logic in new `Joint`s !

You can implement wrappers performing scheduling/control flow tasks such as [`Parallel`](./skelet0wn/limbs/joints/parallel/node.py), [`Sequences`](./skelet0wn/limbs/joints/sequences/node.py), data-transforming nodes such as [`Transformer`](./skelet0wn/limbs/joints/transformer/node.py), or any needed logic operation for your use cases.

In the case of `Joint`s wrapping children `Limb`s, make sure to write `set_environment()` method accordingly, to set proper names and subfolders for the children `Limb`s.

### Integrating/Modifying a `Bone`

A generic `Bone` implementation template is provided: [`GenericBone`](./skelet0wn/limbs/bones/generic_bone_template/).  
A `Bone` class folder contains the following:
```
skelet0wn/limbs/bones/generic_bone_template
├── Dockerfile
├── entrypoint.sh
├── __init__.py
├── interface.yml
└── node.py
```
It is advised to respect the same folder organization, but non-python files can be stored elsewhere as long as the filepaths are correctly configured in `node.py`.

##### `Dockerfile`
Define here the docker image in which to run the tool to be integrated.
- Prefer compact docker images (`alpine`, `kalilinux`) to avoid having too many different images bloating up.
- Install dependancies, if any

It is strongly advised to keep the *entrypoint* logic **as set by default**: copying the `./entrypoint.sh` script into the container and using it as entry.

#### `entrypoint.sh`
Define here pre-run, run, post-run command(s) to be run in the docker container. In most cases, the run command should simply be  `./tool $@` (+ stdout redirection if not done by command argument), to ensure proper parameter, status code and task priority handling.

It is possible to wrap the run command to filter the status code, so as to return non-zero (error) status codes in a more permissive or restrictive way (e.g. in [`Hashcat`](./skelet0wn/limbs/bones/hashcat/node.py)).

#### `__init__.py`
Usual python module initializion file, should usually be empty.

#### `interface.yml`
Describe here the static interface of the tool to be wrapped:
- **Inputs**: list arguments by name, with the field `mandatory` set to 0/False or 1/True. The `Bone` will fail to run if one or more `mandatory` arguments are not available at runtime.
- **command**: ordered list of Jinja2 template elements to build the command. Template variables should be arguments as listed above, that will be put in place when building the command.

#### `node.py`
Main python file for the `Bone` class being defined.

The constructor should not need to be modified, except for the paths to the previously defined files.

`store_result()` is the most important method of the new `Bone`: the logic to parse the raw tool output and feed relevant data in the MongoDB database is described here. It usually contains four steps:
- Reading the raw output (.txt, .yml, .xml, ...)
- Processing the output to extract relevant data
- Storing the obtained data in the relevant MongoDB collections
- Calling `super().store_metadata()` to store the execution metadata (logs, statuses, etc)

[**Composite object tracking**] The `outputID` and `outputCollection` parameters to `.store_metadata()` allow to mark the location of the main element inserted by this `Bone` execution in the Database.
- They default to None if no significant element is to be reused by direct reference of other `Limb`s
- In the case you need to keep track of several elements IDs and collections created by a `Bone` $b_0$, you can create a composite element (e.g. stored in the "tmp" Collection) containing several pairs (elementID, collection). In order to dereference the sub-objects, use `Transformer`s to dereference each sub-object [WIP].
  

## TODO
- [ ] Writing detailed documentation
- [ ] Integrating more `Bone`s and `Joint`s
- [ ] Adding a GUI for easier workflow generation
- [ ] Adding version management on `Limb`s ?
- [ ] Reorganise `Joint`s
- [ ] ...

## Contributing
Contributions are welcome! Please file a pull request with detailed improvements/modifications and I'll review it.

Please make sure your pull request is properly documented, typed and formatted. Use the [provided formatting script](./misc/format.sh).

## Acknowledgements
This development was tested against a custom version of [GOAD](https://github.com/Orange-Cyberdefense/GOAD), ported to AWS. Thank you [Orange-Cyberdefense](https://github.com/Orange-Cyberdefense) for your work.

Credits to all tools developer evoked in this framework (NetExec, Nmap, Impacket, etc.).

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Contact
For questions or support, please open an issue.
