#!/bin/bash

#You need have the "gplately" mamba env ready.

source ~/.init_mamba

export PATH="$PATH:./"

micromamba run -n gplately $1