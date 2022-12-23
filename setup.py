import setuptools


def long_description():
    with open('README.md', 'r') as file:
        return file.read()


setuptools.setup(
    name='stream-unzip',
    version='0.0.72',
    author='Department for International Trade',
    author_email='sre@digital.trade.gov.uk',
    description='Python function to stream unzip all the files in a ZIP archive, without loading the entire ZIP file into memory or any of its uncompressed files',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/uktrade/stream-unzip',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: System :: Archiving :: Compression',
    ],
    python_requires='>=3.5.1',
    install_requires=[
        'pycryptodome>=3.10.1',
        'stream-inflate>=0.0.12',
    ],
    py_modules=[
        'stream_unzip',
    ],
)
