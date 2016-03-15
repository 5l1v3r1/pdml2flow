from setuptools import setup, find_packages

# Setup the project
setup(
    name = "pdml2flow",
    version = '1.0',
    packages = find_packages(),
    install_requires = [
        "dict2xml"
    ],
    # other arguments here...
    entry_points={
        'console_scripts': [
            'pdml2flow = pdml2flow:main',
        ]
    },
    # metadata
    author = "Mischa Lehmann",
    author_email = "ducksource@duckpond.ch",
    description = "Aggregates wireshark pdml to flows",
    license = "Apache 2.0",
    url = "https://github.com/Enteee/pdml2flow",
)
