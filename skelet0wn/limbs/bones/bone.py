from abc import abstractmethod
from typing import Any, Optional

import docker
import yaml
from bson import ObjectId
from jinja2 import Template
from pymongo.collection import Collection
from pymongo.database import Database

from skelet0wn.exceptions import *
from skelet0wn.limbs import Limb
from skelet0wn.utilities import *


class Bone(Limb):
    """`skelet0wn` abstract class describing a wrapped tool, statically configured by a Dockerfile and an interface file and dynamically configured by a mapping file.

    Attributes:
        interface (None | :py:class:`dict`\): Static YAML interface of the :py:class:`Bone` subclass. Constant of the subclass constructor.
        mapping (None | :py:class:`dict`\): Dynamic YAML data mapping of the :py:class:`Bone` instance. Parsed in the subclass contructor at runtime.
        fetched_values (None | dict): Arguments values as specified in interface file, fetched at runtime according to the mapping file providers.
        built_command (str): Command to be ran in the docker container, built from the static template and the fetched arguments values.
        docker_dockerfile_directory (str): Directory of the Dockerfile describing the docker image to build and use. Constant of the subclass constructor.
        docker_image (:py:class:`docker.models.images.Image`\): Built docker image.
        docker_image_tag (str): Specific tag identifier of this image.
        docker_build_logs (Iterable): Logs of the `docker build` step.
        docker_container (:py:class:`docker.models.containers.Container`\): Container object created by this :py:class:`Limb` instance.
        docker_run_logs (List[str]): Logs of the `docker run` step.
        docker_run_status (:py:class:`WaitContainerStatus`\): Status of the `docker run` step.
    """

    def __init__(
        self,
        interface_file: str,
        mapping_file: str,
        docker_dockerfile_directory: str,
        docker_image_tag: str,
    ):
        """Instantiates a :py:class:`Bone`\.

        Args:
            interface_file (str): Path to .yml file defining the static interface of this:py:class:`Bone`class.
            mapping_file (str): Path to .yml file defining the argument mapping of this:py:class:`Bone`instance. Contains static values or dynamic provider for every argument.
            docker_dockerfile_directory (str): Path to Dockerfile of this:py:class:`Bone`class.
            docker_image_tag (str): Tag to add to the :py:class:`Bone`class docker image that will be built.

        Raises:
            :py:class:`InterfaceFileError`\: If the interface file could not be parsed.
            :py:class:`MappingError`\: If the mapping file could not be parsed.
            :py:class:`DockerBuildError`\: If the docker image could not be built.
        """
        super().__init__()
        self.log(f"Building {docker_image_tag} Limb")
        self.docker_dockerfile_directory = docker_dockerfile_directory
        self.docker_image_tag = docker_image_tag
        # Open interface file
        self.log(f"Parsing interface file...", depth_increment=1, level="DEBUG")
        try:
            with open(interface_file) as f:
                self.interface: dict = yaml.safe_load(f)
        except Exception as exc:
            raise InterfaceFileError(f"{exc}")
        # Open mapping file
        self.log(f"Parsing mapping file... ", depth_increment=1, level="DEBUG")
        try:
            with open(mapping_file) as f:
                self.mapping: dict = yaml.safe_load(f)
        except Exception as exc:
            raise MappingFileError(f"{exc}")

        # Build docker image
        self.log(f"Building {docker_image_tag} image... ")
        try:
            docker_client = docker.from_env()
            self.docker_image, self.docker_build_logs = docker_client.images.build(
                path=self.docker_dockerfile_directory, tag=self.docker_image_tag
            )
            for log in self.docker_build_logs:
                self.log(f"{log}", level="TRACE")
        except Exception as exc:
            raise DockerBuildError(f"{exc}")

    def fetch_arguments(self, mongo_database: Database, run_id: str) -> bool:
        """Returns the :py:class:`Limb` arguments availability. If False, calling run() is certain to fail.

        Args:
            mongo_database (:py:class:`pymongo.database.Database`\): MongoDB database to fetch the arguments from.
            run_id (str): Unique identifier of this specific run. Necessary to reuse the same database in several runs.
        Raises:
            :py:class:`BoneStateError`\: If the :py:class:`Bone` is not in the correct state to perform the task.
            :py:class:`MappingError`\: If one or several mandatory arguments had no correct provider.

        Returns:
            bool: True if the arguments needed are available to be consumed.
        """

        self.log(f"Fetching arguments", depth_increment=1)
        if self.mapping is None:
            raise BoneStateError(
                name=self.name,
                class_name=self.__class__.__name__,
                state="NULL",
                task="FETCH_ARGUMENTS",
            )
        self.fetched_values = dict()
        for input_parameter in self.interface["inputs"]:
            parameter_name, mandatory = (
                input_parameter["name"],
                input_parameter["mandatory"] == 1,
            )

            self.log(f"Fetching {parameter_name}", depth_increment=2, level="DEBUG")
            if mandatory and parameter_name not in self.mapping:
                raise MappingError(
                    argument=parameter_name, msg=f"No provider for mandatory parameter"
                )
            if parameter_name in self.mapping:
                if "type" not in self.mapping[parameter_name]:
                    raise MappingError(
                        argument=parameter_name, msg=f"Need to specify a type"
                    )
                t = self.mapping[parameter_name]["type"]
                self.log(f"of type {t}", depth_increment=3, level="DEBUG")
                if t == "static":
                    if self.mapping[parameter_name].get("value") is None:
                        raise MappingError(
                            argument=parameter_name,
                            msg=f"Need to specify a value for static parameter",
                        )
                    self.fetched_values[parameter_name] = self.mapping[parameter_name][
                        "value"
                    ]
                    self.log(
                        f"Value {self.fetched_values[parameter_name]}",
                        depth_increment=3,
                        level="DEBUG",
                    )
                elif t == "dynamic":
                    if "query" not in self.mapping[parameter_name]:
                        raise MappingError(
                            argument=parameter_name,
                            msg=f"Need to specify a query for dynamic parameter",
                        )
                    (
                        provider_root,
                        provider_collection,
                        provider_filter_crit,
                        provider_projection,
                    ) = (
                        self.mapping[parameter_name]["query"].get("root"),
                        self.mapping[parameter_name]["query"].get("collection"),
                        self.mapping[parameter_name]["query"].get("filter"),
                        self.mapping[parameter_name]["query"].get("projection"),
                    )
                    provider_filter_crit = (
                        dict() if provider_filter_crit is None else provider_filter_crit
                    )
                    provider_projection = (
                        dict() if provider_projection is None else provider_projection
                    )
                    if provider_collection is None:
                        raise MappingError(
                            argument=parameter_name,
                            msg=f"Invalid query, missing a collection",
                        )
                    if len(provider_projection) > 1:
                        raise MappingError(
                            argument=parameter_name,
                            msg=f"Invalid query, too many fields",
                        )
                    field = list(provider_projection)[0]
                    field_list = field.split(".")

                    # Query for the provided step output
                    if provider_root is None:
                        # Query first from provided collection
                        self.log(f"from any", depth_increment=3, level="DEBUG")
                    else:
                        if provider_root == "previous":
                            provider_name = get_previous_name(self.name)
                            if provider_name is None:
                                raise MappingError(
                                    argument=parameter_name,
                                    msg=f"Cannot fetch_arguments for limb {self.name}, has no 'previous'",
                                )
                        else:
                            provider_name = provider_root
                        self.log(
                            f"from {provider_name}",
                            depth_increment=3,
                            level="DEBUG",
                        )
                        # Query output location of provided limb
                        query = {
                            "name": provider_name,
                            "run_id": run_id,
                            "outputCollection": {"$ne": None},
                            "outputID": {"$ne": None},
                        }
                        projection = {"outputCollection": 1, "outputID": 1, "_id": 0}
                        result: Optional[Collection] = mongo_database["steps"].find_one(
                            query, projection
                        )
                        if result is None:
                            raise Exception(
                                f"Query for {parameter_name}: Cannot fetch_arguments for root limb {self.name}, {provider_name} has no output"
                            )
                        outputCollection, outputID = (
                            result["outputCollection"],
                            result["outputID"],
                        )
                        self.log(
                            f"in collection {outputCollection}, id {outputID}",
                            depth_increment=3,
                            level="DEBUG",
                        )
                        if outputCollection != provider_collection:
                            raise MappingError(
                                argument=parameter_name,
                                msg=f"Incoherent collection provided in mapping {provider_collection} and provider output collection {outputCollection}",
                            )
                        provider_filter_crit["_id"] = outputID

                    # Query for parameter
                    self.log(
                        f"Query {provider_filter_crit} in {provider_collection}, proj {provider_projection}",
                        depth_increment=4,
                        level="DEBUG",
                    )
                    collection = mongo_database[provider_collection]
                    field_result: Optional[Collection] = collection.find_one(
                        provider_filter_crit, provider_projection
                    )
                    self.log(
                        f"Obtained result {field_result}, has field_list {field_list}",
                        depth_increment=5,
                        level="DEBUG",
                    )
                    try:
                        for f in field_list:
                            assert field_result is not None
                            field_result = field_result[f]
                    except:
                        # Missing a parameter
                        self.log(
                            f"Field {field} of type {t}, no value found",
                            depth_increment=3,
                            level="WARNING",
                        )
                        return False

                    self.fetched_values[parameter_name] = field_result
                    self.log(
                        f'Field {field} of type {t}, obtained result: "{field_result}"',
                        depth_increment=4,
                        level="DEBUG",
                    )
                else:
                    raise MappingError(
                        argument=parameter_name, msg=f"Invalid type value"
                    )
        return True

    def build_command(self) -> None:
        """Build command using the template command defined in the interface file and the fetched argument values.

        Raises:
            :py:class:`BoneStateError`\: If the :py:class:`Bone` is not in the correct state to perform the task.
        """
        if self.fetched_values is None:
            raise BoneStateError(
                name=self.name,
                class_name=self.__class__.__name__,
                state="INIT",
                task="COMMAND_BUILD",
            )
        self.built_command = []
        for argument in self.interface["command"]:
            val = Template(argument).render(self.fetched_values)
            if val != "":
                self.built_command.append(val)

    def run_command(self) -> None:
        """Run the previously built command in a docker container, from the previously built docker image.

        Raises:
            :py:class:`BoneStateError`\: If the :py:class:`Bone` is not in the correct state to perform the task.
            :py:class:`DockerRunError`\: If the docker run call fails.
        """
        if self.built_command is None:
            raise BoneStateError(
                name=self.name,
                class_name=self.__class__.__name__,
                state="",
                task="RUN_COMMAND",
            )
        docker_client = docker.from_env()
        self.docker_container = docker_client.containers.run(
            image=self.docker_image,
            command=self.built_command,
            volumes=[
                f"{self.output_dir}:/mnt/skelet0wn/",
                f"{self.shared_dir}:/mnt/shared",
            ],
            auto_remove=False,
            name=self.name,
            environment={"PYTHONUNBUFFERED": "1"},
            detach=True,
        )
        logs = self.docker_container.logs(stream=True)
        self.docker_run_logs = []
        for log in logs:
            self.log(log.decode("utf-8"), level="TRACE")
            self.docker_run_logs.append(log.decode("utf-8"))

        self.docker_run_status = self.docker_container.wait()
        if self.docker_run_status["StatusCode"] == 137:
            self.log("Early stop", level="WARNING")
        elif self.docker_run_status["StatusCode"] != 0:
            raise DockerRunError(f"{self.docker_run_status}")

    @abstractmethod
    def store_results(self, mongo_database: Database, run_id: str) -> None:
        """Mandatory method for a:py:class:`Bone` class, parsing the logs and/or output files and feeding them to the database.

        Args:
            mongo_database (:py:class:`pymongo.database.Database`\): MongoDB database to store the results in.
            run_id (str): Unique identifier of this specific run. Necessary to reuse the same database in several runs.
        Raises:
            ValueError
        """
        pass

    def run(self, mongo_database: Database, run_id: str) -> None:
        """Base method for a Limb.

        Args:
            mongo_database (:py:class:`pymongo.database.Database`\): MongoDB database to fetch the arguments from and store the results in.
            run_id (str): Unique identifier of this specific run. Necessary to reuse the same database in several runs.
        """
        self.log(f"Running limb {self.name}, {self.__class__.__name__}")

        # Fetch arguments
        fetch_arguments_success = self.fetch_arguments(mongo_database, run_id)

        if not fetch_arguments_success:
            self.log("Could not fetch arguments.")
            self.store_metadata(mongo_database, run_id)
            raise BoneStateError(
                name=self.name,
                class_name=self.__class__.__name__,
                state="",
                task="RUN_COMMAND",
            )

        # Build cmd
        self.log(f"Building command... ", depth_increment=1)
        try:
            self.build_command()
        except Exception as exc:
            self.log("Failed", level="ERROR")
            self.store_metadata(mongo_database, run_id)  # Store limb metadata anyway
            raise LimbError(
                limb=self.name,
                class_name=self.__class__.__name__,
                msg=f"Could not build command: {exc}",
            )
        self.log(f"Done : '{self.built_command}'", level="DEBUG")

        # Running command
        self.log(f"Running command... ", depth_increment=1)
        try:
            self.run_command()
        except Exception as exc:
            self.log(f"Run error {exc}", level="ERROR")
            self.store_metadata(mongo_database, run_id)  # Store limb metadata anyway
            # raise LimbError(limb=self.name,class_name=self.__class__.__name__, msg=f"Could not run command: {exc}")

        # Clean up
        self.log(f"Cleaning up... ", depth_increment=1)
        try:
            self.remove_container()
        except Exception as exc:
            self.log("Failed", level="WARNING")

        # Feed DB
        self.log(f"Parsing results... ", depth_increment=1)
        try:
            self.store_results(mongo_database, run_id)
        except Exception as exc:
            self.log("Failed", level="WARNING")
            self.store_metadata(mongo_database, run_id)  # Store limb metadata anyway
            raise LimbError(
                limb=self.name,
                class_name=self.__class__.__name__,
                msg=f"Could not parse results: {exc}",
            )
        self.log("OK, exiting", level="SUCCESS")

    def interrupt(self) -> None:
        """Sends an interruption signal to the Bone. If a container is running, calls ``docker stop``\."""
        self.log(f"Interrupting {self.name}... ")
        try:
            assert self.docker_container is not None
            self.docker_container.stop()
        except:
            self.log("Already stopped", level="WARNING")
            pass

    def remove_container(self) -> None:
        """Cleans up the container."""
        try:
            assert self.docker_container is not None
            self.docker_container.remove()
        except:
            self.log("Already removed", level="WARNING", depth_increment=2)
            pass

    def store_metadata(
        self,
        mongo_database: Database,
        run_id: str,
        outputCollection: Optional[str] = None,
        outputID: Optional[ObjectId] = None,
        other_fields: dict = dict(),
    ) -> None:
        try:
            other_fields["docker"] = {
                "buildLog": ("\n".join([str(k) for k in self.docker_build_logs]),),
                "runLog": str(self.docker_run_logs),
                "runStatus": str(self.docker_run_status),
            }
            other_fields["command"] = self.built_command
        except Exception as exc:
            self.log(f"Error while storing metadata: {exc}", level="ERROR")
        super().store_metadata(
            mongo_database, run_id, outputCollection, outputID, other_fields
        )
