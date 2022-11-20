from setuptools import setup, find_packages


install_requires = [
    'asyncpg',
    'pydantic',
    'fastapi',
    'uvicorn',
    'sqlalchemy',
    'pytest',
    'requests'

]

setup(
    name='async_lyceum_api',
    version="0.0.0.dev1",
    description='Lyceum API on aiohttp',
    platforms=['POSIX'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False
)
