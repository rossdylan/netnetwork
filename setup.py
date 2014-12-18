from setuptools import setup, find_packages

setup(name='netnetwork',
      version='0.1.0',
      description='Graph the network connections to your box',
      author='Ross Delinger',
      author_email='rossdylan@csh.rit.edu',
      install_requires=['tornado', 'pyzmq'],
      zip_safe=False,
      include_package_data=True,
      packages=find_packages(),
      entry_points="""
      [console_scripts]
      netnetwork_server=netnetwork:server
      netnetwork_aggregator=netnetwork.graph:aggregator
      netnetwork_collector=netnetwork.graph:collector
      """)
