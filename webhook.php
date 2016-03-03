<?php
set_time_limit(300); // 5mins

echo shell_exec("/usr/bin/git pull 2>&1");