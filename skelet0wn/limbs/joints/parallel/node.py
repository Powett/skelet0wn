import threading
from typing import Optional

from pymongo.database import Database

from skelet0wn.limbs import Limb
from skelet0wn.limbs.joints import Joint


class Parallel(Joint):
    """Logic element allowing to run two :py:class:`Limb`\s in parallel.

    Attributes:
        front (:py:class:`Limb`\): Foreground-running :py:class:`Limb`\. Is expected to finish.
        back (:py:class:`Limb`\): Background-running :py:class:`Limb`\. Will be killed on :py:attr:`front` termination, if not finished yet.
    """

    def __init__(self, front: Limb, back: Limb) -> None:
        """Minimal constructor.

        Args:
            front (:py:class:`Limb`\): Foreground-running :py:class:`Limb`\. Is expected to finish.
            back (:py:class:`Limb`\): Background-running :py:class:`Limb`\. Will be killed on :py:attr:`front` termination, if not finished yet.
        """
        super().__init__()
        self.front = front
        self.back = back

    def run(self, skull: Database, run_id: str) -> None:
        self.log(f"Running limb {self.name}, {self.__class__.__name__}")
        self.log(f"Starting background limb... ", depth_increment=1, level="DEBUG")

        def background_wrapper() -> None:
            try:
                self.back.run(skull, run_id)
            except Exception as exc:
                self.log(
                    f"Background child encountered exception: {exc}", level="WARNING"
                )

        background_thread = threading.Thread(target=background_wrapper)
        background_thread.start()

        self.log(f"Starting foreground limb... ", depth_increment=1, level="DEBUG")
        self.front.run(skull, run_id)

        self.back.interrupt()
        self.log(
            f"Waiting on background limb exit... ", depth_increment=1, level="DEBUG"
        )
        background_thread.join()
        self.store_metadata(skull, run_id)
        self.log("OK, exiting", level="SUCCESS")

    def prepare_environment(
        self, output_dir: str, shared_dir: str, name: str = "n0"
    ) -> None:
        """Sets up the :py:class:`Limb` environment: private output directory, shared directory, hierarchical name.
        This overrides the :py:meth:`Limb.prepare_environment()` method to set the :py:attr:`front` and :py:attr:`back` children :py:class:`Limb`\s environments.

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
        self.back.prepare_environment(
            self.output_dir, self.shared_dir, name + "." + "b"
        )
        self.front.prepare_environment(
            self.output_dir, self.shared_dir, name + "." + "f"
        )

    def interrupt(self) -> None:
        """Sends an interruption signal to the Limb. No assumption is taken on its response to this signal.
        This overrides the :py:meth:`Limb.interrupt()` method to propagate signal to :py:attr:`front` and :py:attr:`back` children :py:class:`Limb`\s.
        """
        self.back.interrupt()
        self.front.interrupt()
