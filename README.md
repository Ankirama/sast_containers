# docker_security
Dockerfile and so on for security purpose

## SAST PHP

`sast_php` will help you to find high / critical vulnerabilities in your php code.

```bash
$> cd sast_php
$> docker build . -t phpcs
$> docker run phpcs:latest phpcs --help
$> docker run -v /path/to/repo/to/check:/opt/data phpcs:latest phpcs
$> jq . /path/to/repo/to/check/report.json
```
