import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="server",
    version="0.0.1",
    author="Zomatree",
    author_email="fuck@off.com",
    description="small http server",
    url="https://github.com/fast-bin/server-backend",
    packages=["server"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GLPv2 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
