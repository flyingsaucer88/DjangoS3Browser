from pathlib import Path

from setuptools import find_namespace_packages, setup
from setuptools.command.build_py import build_py as _build_py

here = Path(__file__).parent
README = (here / "README.rst").read_text(encoding="utf-8")

class build_py(_build_py):
    def check_package(self, package, package_dir):
        # Suppress namespace package warnings for non-code asset directories
        return


setup(
    name="DjangoS3Browser",
    version="0.3.1",
    packages=find_namespace_packages(
        include=("djangoS3Browser", "djangoS3Browser.*"),
        exclude=(
            "tests",
            "build",
            "dist",
        ),
    ),
    package_data={
        "djangoS3Browser": [
            "templates/*.html",
            "static/css/*",
            "static/js/*",
            "static/images/*",
        ],
    },
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
    cmdclass={"build_py": build_py},
)
