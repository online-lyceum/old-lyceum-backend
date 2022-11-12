from setuptools import setup, find_packages

install_requires = [
    'aiohttp',
    'asyncpg',
    'uvloop'
]

setup(
    name='async_lyceum_api',
    version="0.0.0.dev1",
    description='Lyceum API on aiohttp',
    platforms=['POSIX'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'async_lyceum_api=async_lyceum_api:run_app',
        ]
    }
)
