import codecs
from os.path import join as join_path, dirname
from setuptools import setup, find_packages


def setup_package():
    setup(
        name='wxviews',
        version=_get_version(),
        long_description=_get_long_description(),
        long_description_content_type='text/markdown',
        url='https://github.com/eumis/wxviews',
        author='eumis(Eugen Misievich)',
        author_email='misievich@gmail.com',
        license='MIT',
        classifiers=[
            #   2 - Pre-Alpha
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.6'
        ],
        python_requires='>=3.6',
        install_requires=['pyviews>=2.0.4', 'wxpython'],
        keywords='binding wxpython pyviews python mvvm wx',
        packages=find_packages(exclude=['sandbox', '*.tests']))


_HERE = dirname(__file__)


def _get_version():
    about = {}
    with open(join_path(_HERE, "wxviews", "__version__.py")) as f:
        exec(f.read(), about)
    return about['__version__']


def _get_long_description():
    readme_path = join_path(_HERE, "README.md")
    with codecs.open(readme_path, encoding="utf-8") as f:
        return "\n" + f.read()


if __name__ == '__main__':
    setup_package()
