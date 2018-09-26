from setuptools import setup

setup(
    name='gmpy_ctypes',
    version='0.1',
    author="Sergey B Kirpichev",
    author_email="skirpichev@gmail.com",
    license="3-clause BSD",
    description="GMP ctypes wrapper",
    keywords=["PyPy", "GMP"],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    packages=['gmpy_ctypes'],
    zip_safe=True)
