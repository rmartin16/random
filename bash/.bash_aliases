alias ls='ls -lho --color=auto'
alias la='ls -A'

function act ()
{
    env=$1
    if [ "${env: -1}" == "/" ]; then
        env=${env::-1}
    fi
    if [[ env -eq "" ]]; then
        env='venv'
    fi
    source "./$env/bin/activate"
}

function fresh () {
    if [ ! "$VIRTUAL_ENV" == "" ]; then
        source deactivate
    fi
    if [ -d ./venv ]; then
        echo "Deleting venv..."
        rm -rf venv
    fi
    echo "Creating venv for $(pyenv version-name)..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Updating venv..."
    python -m pip -q install -U pip wheel setuptools
    if [ -f ./requirements-dev.txt ]; then
        echo "Installing requirements-dev.txt..."
        python -m pip -q install -U -r requirements-dev.txt
    elif [ -f ./requirements.txt ]; then
        echo "Installing requirements.txt..."
        python -m pip -q install -U -r requirements.txt
    fi
}

function bpython_install() {
    if [ "$VIRTUAL_ENV" == "" ]; then
        echo ">>> fyi...no virtual env activated <<<"
    fi
    python -m pip install -U bpython
}
