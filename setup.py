from setuptools import find_packages,setup

hypen_dot_e = "-e ."
def get_requirements(filepath: str) -> list[str]:
    """
    Returns the list of requirements
    """
    with open(filepath) as file_obj:
        requirement = file_obj.readlines()
        requirement = [req.replace("\n", "") for req in requirement]

        if hypen_dot_e in requirement:
            requirement.remove(hypen_dot_e)
        return requirement

setup(
    name='Agentic_credit_risk',
    packages=find_packages(),
    version='0.0.1',
    description='Building agentic tool for credit risk evaluation',
    author='Mrinal',
    author_email='rmmrinal.q@gmail.com',
    license='MIT',
    install_requires= get_requirements('requirements.txt'),
)