

### Size disclaimer

If aiming to run the project locally please keep in mind that some of the language models in the requirements are quite bulky, the virtual environments will end up taking multiple gigabytes of storage space.



### Dependencies

If installing with poetry, after getting all dependencies and creating the venv, make sure you've selected it by checking `poetry venv list` and then running:

```
poetry add boto3
poetry run python -m spacy download en_core_web_sm
```

and manually set scipy to version 1.12 if another dependency sets it to something else

## Issues/Todo

Make models in parsers not re-load for each instance