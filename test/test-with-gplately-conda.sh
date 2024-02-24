#!/bin/bash

# in the "test" folder
# ./test-with-gplately-conda.sh test-dev-server.sh
# run the testcases in "gplately" mamba environment. you need to have the "gplately" env in your local computer.
#You need have the "gplately" mamba env ready.

source ~/.init_mamba

export PATH="$PATH:./"

micromamba run -n gplately $1