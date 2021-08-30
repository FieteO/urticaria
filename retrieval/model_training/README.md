## Training a custom model

### Install necessary python dependencies
``` bash
pip install -r requirements
```
Install the scispacy model
``` bash
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_ner_bc5cdr_md-0.4.0.tar.gz
```
### Export the dataset
In Doccano, go to the Datasets page and export the dataset. This will create a zip file containing the annotations per user, i.e `admin.jsonl` and `unknown.jsonl` which contains all the sections that have not been annotated yet.

In the `data` folder, create an `exported` folder and copy over the `admin.jsonl` file.

### Create a `.spacy` training file
The training file is used by spacy in the `spacy train` command. Run the `generate_train_file.py` script, to generate the file based on the `admin.jsonl`.
``` bash
python generate_train_file.py
```

### Run the training
``` bash
python -m spacy train custom-model/config.cfg --output ./custom-model
```
SciSpacy
``` bash
python -m spacy train custom-model/scispacy/config.cfg --output ./custom-model/scispacy/ --paths.train ./custom-model/train.spacy --paths.dev ./custom-model/train.spacy
```
If everything was successfull, you should now have a `model-best` and `model-last` folder in the `custom-model` directory.

### Rebuild the image
If the containers are still running, use `docker-compose stop` to stop them. Now we can recreate them with:
``` bash
docker-compose up --build
```
