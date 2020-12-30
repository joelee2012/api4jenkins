#!/bin/bash

HERE=$(readlink -f "${BASH_SOURCE[0]}" | xargs dirname)

function start {
  set -e
  local ip port password
  sudo docker run -dt --rm --name jenkins-master jenkins/jenkins
  echo 'Waiting for Jenkins to start...'
  until sudo docker logs jenkins-master | grep -q 'Jenkins is fully up and running'; do
    sleep 1
  done
  ip=$(sudo docker inspect --format='{{.NetworkSettings.IPAddress}}' jenkins-master)
  password=$(sudo docker exec jenkins-master cat /var/jenkins_home/secrets/initialAdminPassword)
  port=8080
  cat <<EOF | tee "${HERE}"/setup_jenkins.py
#!python
URL = 'http://${ip}:${port}'
USER = 'admin'
PASSWORD = '${password}'

def install_plugins(*names):
    import re
    import time
    import os
    from api4jenkins import Jenkins
    jenkins = Jenkins(URL, auth=(USER, PASSWORD))
    if os.getenv('HTTPS_PROXY'):
        matcher = re.match(r'(?P<ip>.*):(?P<port>\d+)$', os.getenv('HTTPS_PROXY'))
        jenkins.plugins.set_proxy(matcher['ip'], port=matcher['port'])
    jenkins.plugins.check_updates_server()
    jenkins.plugins.install(*names, block=True)
    if jenkins.plugins.restart_required:
        jenkins.system.safe_restart()
        while not jenkins.exists():
            time.sleep(2)
    for name in names:
        if not jenkins.plugins.get(name):
            raise RuntimeError(f'{name} was not installed')

if __name__ == '__main__':
    import logging
    import sys
    logging.basicConfig(level=logging.DEBUG)
    install_plugins(*sys.argv[1:])
EOF
  python "${HERE}"/setup_jenkins.py ${PLUGINS//,/ }
}

function stop {
  sudo docker stop jenkins-master
}

"$@"