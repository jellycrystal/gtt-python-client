from setuptools import setup, find_packages

setup(
    name='gtt-python-client',
    version='0.2a2',
    description='Python bindings for Google Translator Toolkit API.',
    long_description=open('README.md').read(),
    author='Yury Yurevich',
    author_email='yyurevich@jellycrystal.com',
    url='https://github.com/jellycrystal/gtt-python-client',
    license='BSD',
    packages=find_packages(),
    include_package_data=False,
    install_requires=['gdata>=2.0.13'],
    zip_safe=True,
    # Get more strings from http://www.python.org/pypi?:action=list_classifiers
    classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)


