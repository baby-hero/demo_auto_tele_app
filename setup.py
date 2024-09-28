from pathlib import Path

from setuptools import find_namespace_packages, setup

# Load packages from requirements.txt
BASE_DIR = Path(__file__).parent
with open(Path(BASE_DIR) / "requirements.txt") as file:
    required_packages = [ln.strip() for ln in file.readlines()]
setup(
    name="src",
    version="0.1",
    description="auto_tele",
    author_email="",
    url="",
    python_requires=">=3.8,<3.11",
    packages=find_namespace_packages(exclude=("tests", "docs")),
    include_package_data=True,
    install_requires=required_packages,
)
