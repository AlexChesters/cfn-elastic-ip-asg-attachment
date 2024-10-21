set -e

export PATH="${HOME}/.poetry/bin:${PATH}"
export VENV_PATH=$(poetry env info -p)

poetry install --only main
mkdir build
cp -R ${VENV_PATH}/lib/python3.*/site-packages/* build/
cp -R cfn_elastic_ip_asg_attachment/ build/
