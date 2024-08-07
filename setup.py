from setuptools import find_packages, setup

from skelet0wn import __version__

setup(
    name="skelet0wn",
    version=__version__,
    description="A pentesting automation framework designed to streamline and automate the entire cyber kill chain, based on docker containers and python orchestration.",
    url="https://github.com/Powett/skelet0wn/tree/master",
    author="Powett",
    author_email="p0w3tt@gmail.com",
    packages=find_packages(),
    install_requires=[
        "certifi==2024.7.4",
        "charset-normalizer==3.3.2",
        "dnspython==2.6.1",
        "docker==7.1.0",
        "idna==3.7",
        "Jinja2==3.1.4",
        "loguru==0.7.2",
        "MarkupSafe==2.1.5",
        "pyaml==24.4.0",
        "pymongo==4.8.0",
        "PyYAML==6.0.1",
        "requests==2.32.3",
        "types-cffi==1.16.0.20240331",
        "types-docker==7.1.0.20240703",
        "types-pyOpenSSL==24.1.0.20240425",
        "types-pyside2==5.15.2.1.7",
        "types-PyYAML==6.0.12.20240311",
        "types-requests==2.32.0.20240622",
        "types-setuptools==70.2.0.20240704",
        "urllib3==2.2.2",
        "setuptools",
    ],
    include_package_data=True,
    package_data={"": ["*.yml"], "": ["*Dockerfile"], "": ["*entrypoint.sh"]},
)
