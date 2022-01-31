# HTTPServerDebug

![Python][python-shield] [![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]

``` bash
docker build . -t httpserverdebug
docker run -d -p 28080:80 -v "$(pwd)/config.json:/app/config.json" --name httpserverdebug httpserverdebug
```


[cc-by-sa]: /LICENSE.md
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg
[python-shield]: https://img.shields.io/badge/Python-14354C?style=flat&logo=python&logoColor=white
