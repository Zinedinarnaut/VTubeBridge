from setuptools import setup, find_packages

setup(
    name="vtstudio",  # The name of your package
    version="0.1.0",  # Your package version
    packages=find_packages(),
    install_requires=[
        "websockets",
    ],
    author="Your Name",
    author_email="zinedinarnaut085@gmail.com",
    description="A fully featured Python wrapper for the VTube Studio API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zinedinarnaut/vtstudio",  # Replace with your GitHub URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)