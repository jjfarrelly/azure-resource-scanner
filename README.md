# Foobar
Azure Disk Scanner is a python program written to help query enterprise scale Azure estates. 

The program scans across all subscriptions in your estate and pulls out managed disks that are currently in an unattached state. The program has also been extended to use the ado_manager class which automates the Azure DevOps ticket creation of these resources so you are able to keep track of remediation items in your change management schedule.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all dependecies. Just run the following command in the route directory of the program:

```bash
pip install -r requirements.txt
```

## Usage
First ensure all python files have the executable privalege in your console and the simply start the program by running the following command and passing in the required variables.

```python
python ./main.py
```


## License
[MIT](https://choosealicense.com/licenses/mit/)

## Author 
joe.j.farrelly@outlook.com