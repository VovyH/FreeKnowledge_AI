from setuptools import setup, find_packages

setup(
    name="sues_knowledge",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.1',
        'beautifulsoup4>=4.9.3',
        'jieba>=0.42.1',
        'matplotlib>=3.3.4'
    ],
    author="Yuhang-Wu",
    author_email="m325124620@sues.edu.cn",
    description="An agent that provides free and flexible access to external knowledge.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/VovyH/FreeKnowledge_AI",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)