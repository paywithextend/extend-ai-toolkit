from setuptools import setup, find_packages

setup(
    name='extend_ai_toolkit',
    version='0.0.1',
    package_dir={'': 'extend_ai_toolkit'},
    packages=find_packages(where='extend_ai_toolkit',
                           include=['modelcontextprotocol', 'modelcontextprotocol.*', 'langchain', 'langchain.*']),
    install_requires=[
        'build',
        'requests==2.32.3',
        'mcp==1.4.1',
        'colorama==0.4.6',
        'langchain==0.3.20',
        'starlette>=0.40.0,<0.46.0',
    ],
)
