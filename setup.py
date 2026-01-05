from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent
README = (here / "README.rst").read_text(encoding="utf-8")

setup(
    name="DjangoS3Browser",
    version="0.3.1",
    packages=find_packages(exclude=("tests", "build", "dist")),
    include_package_data=True,
    description="S3 browser for Django",
    long_description=README,
    long_description_content_type="text/x-rst",
    author="mkaykisiz",
    author_email="m.kaykisiz@gmail.com",
    url="https://github.com/mkaykisiz/DjangoS3Browser",
    license="MIT",
    python_requires=">=3.8",
    install_requires=[
        "Django>=4.2,<6.0",
        "boto3>=1.35,<2.0",
    ],
)
