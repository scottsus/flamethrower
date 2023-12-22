from setuptools import setup, find_packages

setup(
    name='flamethrower',
    version='0.1.0',
    author='Scott Susanto',
    author_email='scottsus@usc.edu',
    description='The ultimate debugging experience 🔥',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/scottsus/flamethrower',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.9',
    install_requires=[
        'openai',
        'rich',
    ],
)
