import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyepidemics", # Replace with your own username
    version="0.0.2",
    author = 'Theo Alves Da Costa',
    author_email = 'theo.alvesdacosta@ekimetrics.com',
    description = 'Open source epidemiological modeling in Python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/collectif-codata/pyepidemics",
    packages=setuptools.find_packages(),
    install_requires=[
        "scipy==1.4.1",
        "numpy==1.18.4",
        "pandas>=1.0.0",
        "scikit_learn==0.23.1",
        "matplotlib==3.1.3",
        "optuna==1.3.0",
        "pydeck==0.3.0b2",
        "requests==2.22.0",
        "plotly==4.6.0",
        "tqdm==4.46.0",
        "statsmodels==0.10.1",
        "networkx>=2.2",
        "PyYAML==5.3.1",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        'Documentation': 'https://collectif-codata.github.io/pyepidemics/',
    },
    python_requires='>=3.6',
)