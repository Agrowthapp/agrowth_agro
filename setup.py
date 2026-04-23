from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

setup(
	name="agrowth_agro",
	version="0.1.0",
	description="Módulo de agricultura para ERPNext",
	author="Agrowth",
	author_email="info@agrowth.app",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
