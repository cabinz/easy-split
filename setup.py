from setuptools import setup, find_packages
import os

authors = [
    'Cabin Zhu',
]

if __name__ == '__main__':
    # Read the requirements from the requirements.txt file
    with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
        requirements = f.read().splitlines()

    setup(
        name='easy-split',
        version='1.0.0',
        description='Easily splitting bill with your friends.',
        author=', '.join(authors),
        author_email='cabin_zhu@foxmail.com',
        license='Apache 2.0',
        url='https://github.com/cabinz/easy-split',
        package_dir={'': 'src'},
        packages=find_packages(
            where='src',
            exclude=['tests', 'tests.*'],
            # include=['utils', 'utils.*'],
        ),
        entry_points={
            'console_scripts': [
                'splitbill = easysplit.__main__:main',
            ],
        },
        python_requires='>=3.10',
        install_requires=requirements,
    )
