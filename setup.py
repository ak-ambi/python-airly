import setuptools

REQUIRES = [
    'aiohttp>=3.5.4',
]

with open("README.rst") as fh:
    long_description = fh.read()

setuptools.setup(
    name='airly',
    version='1.1.0',
    description=
    'Python wrapper for getting air quality data from Airly sensors.',
    long_description=long_description,
    url='https://github.com/ak-ambi/python-airly',
    license='MIT',
    packages=['airly'],
    install_requires=REQUIRES,
    python_requires='>=3.6.0',
    author='Paweł Stankowski',
    author_email='ak_ambi@op.pl',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    test_suite='tests',
)
