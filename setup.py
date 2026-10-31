"""Compatibility fallback for packaging toolchains that ignore PEP 621 metadata."""
from setuptools import find_packages, setup

setup(
    name="frameforge-community",
    version="0.1.0",
    description="Optional project framework discovery and standards advisory",
    license="Apache-2.0",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={"frameforge.manifests": ["*.json"]},
    entry_points={"console_scripts": ["frameforge=frameforge.cli:main"]},
)
