import setuptools

from concat import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Source Code Concater",
    author="MapleCCC",
    author_email="littlelittlemaple@gmail.com",
    description="...",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MapleCCC/Source-Concater",
    version=__version__,
    packages=setuptools.find_packages(),
    license="WTFPL 2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=open("requirements.txt", "r").read().splitlines(),
    entry_points={
        "console_scripts": [
            "concat=concat.__main__:main",
            # "concat-build=concat.__main__:",
        ]
    },
)
