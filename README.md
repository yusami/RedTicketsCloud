# RedTicketsCloud

## Features

* Extract text from all issues in Redmine.
* Draw WordCloud image for each project.

## Requirement

* Python 3.9

## Installation

* Install the required libraries.

~~~
$ pip3 install python-redmine python-dotenv janome wordcloud gensim
~~~

* Set Redmine API key.

~~~
$ cp .env.example .env
$ vim .env
REDMINE_API_KEY=xxx
~~~

* Change the Redmine url. (optional, default: http://localhost/redmine/)

~~~
$ cp config/projects.json.example config/projects.json
$ vim config/projects.json
REDMINE_URL=http://server/redmine
~~~

* Change the Japanse font path. (optional, already set for macOS and Windows)

~~~
$ vim creator.py
fpath = '$HOME/Library/Fonts/ipagp.ttf'
~~~

## Usage

* Call the command below.

~~~
$ python3 main.py
~~~

* Issue text is exported in `data` folder.
  * `data/<PROJECT_ID>/<ISSUE_ID>.json`

~~~
{
  "id": xxx,
  "subject": "...",
  "description": "...",
  "notes": [
    "..."
  ]
}
~~~

* WordCloud image is exported in `image` folder.
  * `image/<PROJECT_ID>.png`

## Unit test

* Call the command below.

~~~
$ python3 -m unittest discover tests
~~~

## Acknowledgments

* [amueller/word_cloud](https://github.com/amueller/word_cloud)
* [maxtepkeev/python-redmine](https://github.com/maxtepkeev/python-redmine)

## Licence

* Copyright (c) 2020-2021, [Yasushi Usami](https://github.com/yusami)
* Licensed under the [Apache License, Version 2.0][Apache]

[Apache]: http://www.apache.org/licenses/LICENSE-2.0
