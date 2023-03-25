from setuptools import setup, find_packages 

setup(
name="WebInterface", 
version = "1.0.0", 
description="web interface for social media", 
packages = find_packages(exclude=["docs"]), 
python_requires=">=3.7, <4",
#entry_points={"console_scripts": ["oatools=oatools.main:main"]},
)
 