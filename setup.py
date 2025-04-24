from setuptools import setup, find_packages

setup(
    name="jester",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "psycopg2-binary",
    ],
) 