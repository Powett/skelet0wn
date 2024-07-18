from typing import List, Optional

from pymongo.database import Database

from skelet0wn.limbs import Limb
from skelet0wn.limbs.joints import Joint


class Sequence(Joint):
    """Logic element allowing to run a list of :py:class:`Limb`\s sequentially. By default, continues while the children run successfully and stop on first error.

    Attributes:
        children (List[:py:class:`Limb`]): Children :py:class:`Limb`\s to try and run.
        stop_on_success (bool): If True, the sequence will stop on the first success. If False, the sequence will move on to the next child :py:class:`Limb`\. Defaults to False.
        stop_on_failure (bool): If True, the sequence will stop on the first failure. If False, the sequence will move on to the next child :py:class:`Limb`\. Defaults to True.
    """

    def __init__(
        self,
        children: List[Limb],
        stop_on_success: bool = False,
        stop_on_failure: bool = True,
    ) -> None:
        """Minimal constructor.

        Args:
            children (List[:py:class:`Limb`]): Children :py:class:`Limb`\s to try and run.
            stop_on_success (bool, optional): If True, the sequence will stop on the first success. If False, the sequence will move on to the next child :py:class:`Limb`\. Defaults to False.
            stop_on_failure (bool, optional): If True, the sequence will stop on the first failure. If False, the sequence will move on to the next child :py:class:`Limb`\. Defaults to True.
        """
        super().__init__()
        self.children = children
        self.stop_on_success = stop_on_success
        self.stop_on_failure = stop_on_failure

    def run(self, mongo_database: Database) -> None:
        self.log(f"Running limb {self.name}, {self.__class__.__name__}")
        self.log(
            f"Stop on failure: {self.stop_on_failure}, Stop on success: {self.stop_on_success}",
            level="DEBUG",
        )
        for child in self.children:
            try:
                self.log(f"Trying {child.name}...", depth_increment=1, level="DEBUG")
                child.run(mongo_database)
            except Exception as exc:
                if self.stop_on_failure:
                    raise Exception(
                        f"Sequence {self.name} error on child {child.name} : {exc}"
                    )
                else:
                    self.log("Not OK, moving to next child", level="WARNING")
                    self.log(f"Had error: {exc}", level="DEBUG")
            else:
                if self.stop_on_success:
                    return
        self.log("Reached last child", level="DEBUG")
        self.store_metadata(mongo_database)
        self.log("OK, exiting", level="SUCCESS")

    def interrupt(self) -> None:
        """Sends an interruption signal to the Limb. No assumption is taken on its response to this signal.
        This overrides the :py:meth:`Limb.interrupt()` method to propagate signal to all children :py:class:`Limb`\s.
        """
        for child in self.children:
            try:
                child.interrupt()
            except:
                pass

    def prepare_environment(
        self, output_dir: str, shared_dir: str, name: str = "n0"
    ) -> None:
        """Sets up the :py:class:`Limb` environment: private output directory, shared directory, hierarchical name.
        This overrides the :py:meth:`Limb.prepare_environment()` method to set the children :py:class:`Limb`\s environments.

        Args:
            output_dir (str): Private output directory. Children will live in subdirectories.
            shared_dir (str): Shared, flat directory for file sharing.
            name (str, optional): Hierarchical name of the limb. Defaults to "n0".
        """
        super().prepare_environment(
            output_dir=output_dir,
            shared_dir=shared_dir,
            name=name,
        )
        for i, child in enumerate(self.children):
            child.prepare_environment(
                self.output_dir, self.shared_dir, name + "." + str(i)
            )
