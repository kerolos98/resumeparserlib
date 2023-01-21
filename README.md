# resumeparserlib

***resumeparser***  is a Python library for dealing with different resume templates and organize it based on font size and style and text structure it addition of using ner model to extract entites from each section.

## Installation

first of all, you will need to install libreoffice if you are using Linux.
```bash
sudo apt-get update
sudo apt-get install libreoffice inkscape ffmpeg xvfb
```
then close the repository.
```bash
git clone https://github.com/kerolos98/resumeparserlib
```
then install <requirements.txt> file within the repo .
```bash
pip -r requirements.txt
```

## Usage

```python
import resumeparser

# generates json files in the project directory
resumeparser.file_extraction(file_path)

```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.
