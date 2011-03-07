from setuptools import setup, find_packages
setup(
    name= "jhs_dbn",
    version = 0.1,
    packages=find_packages(),
    entry_points="""
        [console_scripts]
        jdbn = jhs_dbn.commands:main
    """
)
