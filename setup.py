import setuptools

setuptools.setup(
    name="codomain",
    version="0.0.1",
    author="Logan Bontrager",
    description="A small and limited static site generator",
    url="https://github.com/loganbon/codomain",
    py_modules=["codomain"],
    install_requires=[
        'python-frontmatter',
        'bottle',
        'paste',
        'markdown',
    ],
    entry_points={
        'console_scripts': [
            'codomain=codomain:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
