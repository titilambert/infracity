import sys
from setuptools import setup
from infracity.__version__ import VERSION

if sys.version_info < (3, 4):
    sys.exit("Sorry, Python < 3.4 is not supported")

install_requires = list(val.strip() for val in open("requirements.txt"))
tests_require = list(val.strip() for val in open("test_requirements.txt"))

setup(
    name="infracity",
    version=VERSION,
    description="Generate world based on your infra",
    author="Thibault Cohen",
    author_email="titilambert@gmail.com",
    url="https://github.com/titilambert/infracity",
    include_package_data=True,
    packages=["infracity"],
    entry_points={
        "console_scripts": [
            "infracity = infracity.__main__:main",
        ]
    },
    data_files=[
    ],
    license="Apache 2.0",
    install_requires=install_requires,
    tests_require=tests_require,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
