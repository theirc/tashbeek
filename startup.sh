#! /bin/bash
touch .env && printenv | sed 's/^\(.*\)$/export \1/g' > .env && source .env && /usr/bin/supervisord
