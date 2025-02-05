
### Run in CLI

```
1) python text2timeline.py -cli
2) follow instructions
```

### Size disclaimer

If aiming to run the project locally please keep in mind that some of the language models in the requirements are quite bulky, the virtual environments will end up taking multiple gigabytes of storage space.



### Dependencies 

# Check the DockerFile for most up to date build steps

If installing with poetry (run poetry install in the foldder), after getting all dependencies and creating the venv, make sure you've selected it by checking `poetry venv list` and then running:

```
poetry add boto3
poetry run python -m spacy download en_core_web_sm
```

and manually set scipy to version 1.12 if another dependency sets it to something else

## Known issues
Lots!


## Building with docker
```
docker run -d -p 5001:5000 text2timeline  
docker buildx build --tag text2timeline  .

# Manually rebuild image
docker compose up -d --no-deps --build text2timeline
```

### Docker memory usage
For some reason, when running the application through docker took more than 5 times the RAM usage of running it normally. Apparently this is a
WSL 2 issue quite a few people are experiencing - if you have this problem a possible (though not perfect) fix is to create a .wslconfig file under
%UserProfile% with the following

```
[wsl2]
# Adjust according to your machine specs
memory=6GB   
processors=2 
```

