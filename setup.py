from setuptools import setup, find_packages

setup(
    name="cursor2cape",
    version="2.0.0",
    description="Conversor de temas de cursor Xcursor (Linux) para capas do Mousecape (macOS)",
    author="Ubuntu / Yaru Team / Carlos",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "Pillow>=10.0.0",
        "rich>=13.0.0",
        "questionary>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cursor2cape=cursor2cape.__main__:main",
        ],
    },
)
