class InterfaceFileError(Exception):
    """Custom Exception type for interface file parsing errors."""

    def __init__(self, msg: str) -> None:
        super().__init__(f"Interface file error: {msg}")


class MappingFileError(Exception):
    """Custom Exception type for mapping file parsing errors."""

    def __init__(self, msg: str) -> None:
        super().__init__(f"Mapping file error: {msg}")


class MappingError(Exception):
    """Custom Exception type for mapping errors when fetching values."""

    def __init__(self, msg: str, argument: str) -> None:
        super().__init__(f"Mapping error on {argument}: {msg}")


class DockerBuildError(Exception):
    """Custom Exception type for docker build errors."""

    def __init__(self, msg: str) -> None:
        super().__init__(f"Docker build error: {msg}")


class DockerRunError(Exception):
    """Custom Exception type for docker run errors."""

    def __init__(self, msg: str) -> None:
        super().__init__(f"Docker run error: {msg}")


class BoneError(Exception):
    """Custom generic Exception type for :py:class`Bone` errors."""

    def __init__(self, name: str, class_name: str, msg: str) -> None:
        super().__init__(f"Bone {name} ({class_name}) error: {msg}")


class LimbError(Exception):
    """Custom generic Exception type for :py:class`Limb` errors."""

    def __init__(self, msg: str, limb: str, class_name: str) -> None:
        super().__init__(f"Limb {limb} ({class_name}) error: {msg}")


class BoneStateError(BoneError):
    """Custom Exception type for :py:class`Bone` errors due to a forbidden method call in the current state."""

    def __init__(self, name: str, class_name: str, state: str, task: str) -> None:
        super().__init__(name, class_name, f"Wrong Bone state {state} to {task}")
