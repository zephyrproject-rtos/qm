
# Plugin for thirdparty report

This is the guide for thirdparty report plugin support

## Document generation

using sphinx style please refer to [sphinx](http://www.sphinx-doc.org/en/master/)

```
pip install Sphinx
```

## How to add a new plugin

1. create a folder in plugin
2. modify the plugin/__init__.py to add your plugin folder name
3. implement two function in your class and export them in __init__.py of your created folder
   for example:
```
def get_plugin_name():
	logging.info('check nxp plugin')
	return "nxp"

def get_class_name():
	return "NXP"
```
4. modify the report.py add one line at import plugins, e.g.
```
import plugins
from plugins import nxp
```

5. references
* please refer to nxp folder for examples
* a helper base class testrail.py is provide for easy of use 

## Run
please use this command to check your plugin functions
```
python ./report.py -P nxp -m 0 -B "Zephyr Sandbox,batch_plan,frdm_k64f,Master,kernel.device.dummy_device,1,log.txt" 
```

## Test

```
python ./report.py -P nxp -T 1
```

## query informations

### query projects
```
python ./report.py -P nxp -q projects

```
### query boards
```
python ./report.py -P nxp -q boards

```
### query test suites
```
python ./report.py -P nxp -q suites

```
### query status id
```
python ./report.py -P nxp -q status_ids

```
### query case ref id
```
python ./report.py -P nxp -q "kernel.device.dummy_device"
```
### query section id
```
python ./report.py -P nxp -q "kernel.device"
```
### query board id
```
python ./report.py -P nxp -q "frdm_k64f"

```

## get help
ignore the error
```
python ./report.py -P nxp -H
```
