from setuptools import setup, find_packages

setup(
    name="VTubeBridge",
    version="0.2.2",
    packages=find_packages(),
    install_requires=[
        "websockets",
    ],
    author="Araxyso",
    author_email="zinedinarnaut085@gmail.com",
    description="A fully featured Python wrapper for the VTube Studio API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://v0-tesst-bf8bpxqdsin.vercel.app/",  # Main website
    project_urls={
        "Homepage": "https://v0-tesst-bf8bpxqdsin.vercel.app/",
        "Source": "https://github.com/Zinedinarnaut/VTubeBridge",
        "Bug Tracker": "https://github.com/Zinedinarnaut/VTubeBridge/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Multimedia :: Graphics",
    ],
    python_requires='>=3.11',
)