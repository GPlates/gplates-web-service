#!/bin/bash

source ~/.init_mamba

export PATH="$PATH:./"

micromamba run -n gplately $1