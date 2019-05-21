import pathlib

from setuptools import setup, find_packages

try:
    from pip.req import parse_requirements
except ImportError:  # pip >= 10.0.0
    from pip._internal.req import parse_requirements

WORK_DIR = pathlib.Path(__file__).parent

with open('README.md', 'r') as file:
    readme = file.read()

requirements_file = WORK_DIR / 'requirements.txt'

install_reqs = parse_requirements(str(requirements_file), session='hack')
parsed_requirements = [str(ir.req) for ir in install_reqs]

setup(
    name='aiospbstu',
    version='1.0.0',
    author='MrMrRobat',
    author_email='appkiller16@gmail.com',
    description='Asynchronous API wrapper for PolyTech Schedule API',
    long_description=readme,
    requires_python='>=3.7',
    long_description_content_type='text/markdown',
    url='https://github.com/MrMrRobat/aiospbstu˙',
    packages=find_packages(),
    install_requires=parsed_requirements,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
