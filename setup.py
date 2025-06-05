from setuptools import setup, find_packages

setup(
    name="sefa-streamlit",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.32.0",
        "pandas==2.2.0",
        "openpyxl==3.1.2",
        "xlsxwriter==3.1.9",
        "PyPDF2==3.0.1",
        "numpy==1.26.4",
        "python-docx==1.1.0"
    ],
) 