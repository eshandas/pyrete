from setuptools import find_packages, setup
# Read more here: https://www.codementor.io/arpitbhayani/host-your-python-package-using-github-on-pypi-du107t7ku

setup(
    name='pyrete',
    packages=find_packages(),
    include_package_data=True,
    version='0.2.0',
    description='Rete algorithm based Rule Engine built on Python',
    author='Eshan Das',
    author_email='eshandasnit@gmail.com',
    url='https://github.com/eshandas/pyrete',  # use the URL to the github repo
    download_url='https://github.com/eshandas/pyrete/archive/0.2.0.tar.gz',  # Create a tag in github
    keywords=['rete', 'net', 'network', 'rule', 'engine'],
    classifiers=[],
)
