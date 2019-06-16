import setuptools


def long_description():
    with open("README.md", "rb") as fh:
        long_description = fh.read().decode()
    return long_description


setuptools.setup(
    name="discoecs",
    version="2.2.1",
    author="bindreturn",
    author_email="bindreturn@protonmail.ch",
    description="Easy to setup AWS ECS autodiscovery for Prometheus",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/bindreturn/discoecs",
    packages=setuptools.find_packages(),
    install_requires=[
        'boto3',
    ],
    classifiers=(
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ),
    entry_points={
        'console_scripts': [
            'discoecs=discoecs.discoecs:main',
        ]
    }
)
