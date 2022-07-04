from setuptools import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
    long_description = long_description.replace("\r", "")
except:
    long_description = ''

setup(
    name='sanic_compress_plus',
    version='0.1.1',
    description='An extension which allows you to easily gzip and brotli your Sanic responses.',
    long_description=long_description,
    url='https://github.com/hansonkim/sanic_compress_plus',
    author='Hanson Kim',
    license='MIT',
    packages=['sanic_compress_plus'],
    install_requires=('sanic', 'brotli'),
    zip_safe=False,
    keywords=['sanic', 'gzip', 'brotli'],
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Session',
    ]
)
