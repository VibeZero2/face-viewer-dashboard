from setuptools import setup, find_packages

setup(
    name="face-viewer-dashboard",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Flask==2.3.3",
        "Flask-Login==0.6.2",
        "Flask-WTF==1.1.1",
        "Werkzeug==2.3.7",
        "numpy==1.26.4",
        "pandas==2.0.3",
        "plotly==5.18.0",
        "dash==2.14.1",
        "dash-bootstrap-components==1.5.0",
        "cryptography==41.0.3",
        "python-dotenv==1.0.0",
        "gunicorn==21.2.0",
        "requests==2.31.0",
    ],
    python_requires=">=3.12,<3.13",
)
