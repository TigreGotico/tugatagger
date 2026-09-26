import os

from setuptools import setup, find_packages

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def get_version():
    """ Find the version of the package"""
    version_file = os.path.join(BASEDIR, 'tugatagger', 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if alpha and int(alpha) > 0:
        version += f"a{alpha}"
    return version


setup(
    name="tugatagger",
    version=get_version(),
    description="A unified wrapper for Portuguese POS tagging and benchmarking.",
    # long_description=open("README.md").read(),
    # long_description_content_content_type="text/markdown",
    author="JarbasAI",
    url="https://github.com/TigreGotico/tugatagger",
    packages=find_packages(),
    install_package_data=True,
    extras_require={
        "spacy": ["spacy"],
        "stanza": ["stanza"],
        "lexicon": ["tugalex"],
        "brill": ["brill_postagger"],
        "tugamorph": ["tugamorph"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Natural Language :: Portuguese",
    ],
    python_requires='>=3.7',
)
