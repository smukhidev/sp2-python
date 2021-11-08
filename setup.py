import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shurjopay-V2",
    version="0.0.2",
    author="Tareq Anam",
    author_email="tareq.anam@shurjomukhi.com.bd",
    description="shurjopay version 2 payment gateway integration package for python users.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/smukhidev/sp2-python.git",
    project_urls={
        "Bug Tracker": "https://github.com/smukhidev/sp2-python.git",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests'],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
