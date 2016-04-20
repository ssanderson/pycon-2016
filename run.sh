#!/bin/bash

venv_name="pycon-2016"
config_dir="jupyter-config"

if [[ -z "$(type -t workon)" ]];
then
    echo "No function named 'workon' found. Did you execute ./run.sh instead of 'source'-ing?"
    echo "See https://virtualenvwrapper.readthedocs.org/en/latest/install.html"
elif [[ -z "$(lsvirtualenv -b | grep $venv_name)" ]];
then
    echo "No virtualenv named $venv_name found."
else
    workon $venv_name

    # Install module and dependencies editably.
    pip install -e ./codetransformer

    export JUPYTER_CONFIG_DIR=$config_dir
    jupyter nbextension install RISE/livereveal --symlink --nbextensions $config_dir/nbextensions
    jupyter nbextension enable livereveal/main
    jupyter notebook notebooks
fi
