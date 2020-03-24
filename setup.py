import setuptools


def read_content(file: str) -> str:
    with open(file, 'r') as f:
        return f.read().strip()


version_number = read_content('version.txt')

# development_status = 'Development Status :: 3 - Alpha'
development_status = 'Development Status :: 4 - Beta'
# development_status = 'Development Status :: 5 - Production/Stable'


setuptools.setup(
    name='stx',
    version=version_number,
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
            'stx=stx.app:cli'
        ]
    },
    # See: https://pypi.org/classifiers/
    classifiers=[
        development_status,
        'Topic :: Documentation',
        'Topic :: Text Processing :: Markup',
        'Topic :: Software Development :: Documentation',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
