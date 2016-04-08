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
            'pdml2flow = pdml2flow:pdml2flow',
            'pdml2json = pdml2flow:pdml2json',
            'pdml2xml = pdml2flow:pdml2xml',
        ]
    },
    # metadata
    author = "Mischa Lehmann",
    author_email = "ducksource@duckpond.ch",
    description = "Aggregates wireshark pdml to flows",
    license = "Apache 2.0",
    url = "https://github.com/Enteee/pdml2flow",
    # testing
    test_suite="test",
)
