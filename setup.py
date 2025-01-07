from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="indent-tools",
    version="2.0",
    description="Tools for text indentation and XML/HTML markup generation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lainproliant/indent-tools",
    author="Lain Musgrove (lainproliant)",
    author_email="lainproliant@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Programming Language :: Python :: 3",
    ],
    keywords="indent text formatting xml html",
    packages=find_packages(),
    install_requires=[],
    extras_require={},
    package_data={"indent-tools": ["LICENSE"]},
    data_files=[],
    entry_points={"console_scripts": []},
)
