from setuptools import setup, find_packages

setup(
    name="stim",
    version="1.0.0",
    description="Caffeine Intake Tracker",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Michael Kirsanov",
    author_email="michael@lofilabs.xyz",
    url="https://github.com/lofimichael/stim",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'stim=stim.stim:main',
        ],
    },
    install_requires=[
        "plotext==5.3.2",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
) 