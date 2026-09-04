#!/bin/bash
source ~/.bashrc
beeline -u "jdbc:hive2://localhost:10000" --silent=true --outputformat=table -e "
SHOW TABLES IN ods;
SHOW TABLES IN analytics;
SHOW TABLES IN default;
" 2>/dev/null
