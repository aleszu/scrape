# scrape
lets you scrape multiple urls for text from a csv file

### Setup dependencies
```
make init
```

### Sample execution
test.csv
| Name | Url |
| --- | --- |
| nytimes | https://www.nytimes.com |
| cnn | http://www.cnn.com |
| buzzfeed | https://www.buzzfeed.com |

```
relative path to the file: test.csv
does file have column headers(y/n): y
which column has the url [0-n]: 1
which column has article name (press enter if none): 0
path of where to store text files: data/
```
