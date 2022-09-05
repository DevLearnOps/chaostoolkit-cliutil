from setuptools import setup, find_packages

setup(
    name="chaostoolkit-cliutil",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "boto3==1.24.66",
        "botocore==1.27.66",
        "jinja2==3.1.2",
        "jmespath==1.0.1; python_version >= '3.7'",
        "logzero==1.7.0",
        "markupsafe==2.1.1; python_version >= '3.7'",
        "python-dateutil==2.8.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "pyyaml==6.0",
        "s3transfer==0.6.0; python_version >= '3.7'",
        "six==1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "urllib3==1.26.12; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5' and python_version < '4'",
    ],
    entry_points={
        "console_scripts": [
            "chaoscli=chaoscli.main:cli",
        ],
    },
)
