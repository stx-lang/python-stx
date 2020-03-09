import setuptools


def read_content(file: str) -> str:
    with open(file, 'r') as f:
        return f.read().strip()


setuptools.setup(
    name='stx',
    version=read_content('version.txt'),
    author='Sergio Pedraza',
    author_email='sergio.uriel.ph@gmail.com',
    description='Python implementation of the STX Language',
    long_description=read_content('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/stx-lang/python-stx',
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
    license='MIT',
    install_requires=read_content('requirements-main.txt'),
    entry_points={
        'console_scripts': [
            'stx = stx.__main__:main'
        ]
    },
    # See: https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Documentation',
        'Topic :: Text Processing :: Markup',
        'Topic :: Software Development :: Documentation',
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
