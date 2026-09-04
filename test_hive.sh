#!/bin/bash
source ~/.bashrc
beeline -u "jdbc:hive2://localhost:10000" --silent=true --outputformat=table -e "SHOW DATABASES;" 2>/dev/null
