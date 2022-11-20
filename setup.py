from setuptools import setup, find_packages


install_requires = [
    'asyncpg',
    'pydantic',
    'fastapi',
    'uvicorn',
    'sqlalchemy[asyncio]',
]

setup(
    name='async_lyceum_api',
    version="0.0.2.dev1",
    description='Lyceum API on ',
    platforms=['POSIX'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'init_models = async_lyceum_api.db.db_manager:run_init_models',
        ]
    }
)
