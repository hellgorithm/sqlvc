# SQLVC
Cross platform version control for SQL server. 

## Current Features

* Currently supported SQL Server
* Open connection via Windows or SQL Authentication
* Track DDL changes
* Compare versions via external difftool (Diffmerge is currently supported)
* Apply merged changes in database
* Commit database changes
* Apply commit to other server as long as the target server is SQLVC enabled
* Commit the applied changes in other server
* Save and restore workspace though shelf


There are still features that are not yet implemented

### Dependencies
* Diffmerge
* SQL Server Driver 13 (tested in Linux and Windows)

### Build Dependencies 
* Python2.7/3
* PyQt5
* Pyinstaller

### Feedback

https://github.com/hellgorithm/sqlvc

### Binary 
[Windows 64bit](https://drive.google.com/file/d/1NL4hp4rmapRWGzOpnqRHJjPOEQgATO8J/view?usp=sharing)

[Linux 64bit](https://drive.google.com/file/d/1TIMGGXTpLzzG5xpE06B2cz_S5_DTOObM/view?usp=sharing)


