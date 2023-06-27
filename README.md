
## MLPipeline package

###  Initialize a project

You can initialize a project by running:

```sh
mlp init
```

### Sync & update the dvc files in main project

The ML pipeline in the main project can be synced (intializing or updating the dvc files inside the root directory) by running:

```sh
mlp sync -n "[notebooks/data_preprocess.ipynb, notebooks/train.ipynb]"
```

### Create a pipeline

A new pipeline can be created by running:

```sh
mlp create -p "myfirstpipeline"
```

### Link notebooks to a pipeline

To link a list of notebooks for a specific pipeline:

```sh
mlp link -p "myfirstpipeline" -n "[notebooks/data_preprocess.ipynb, notebooks/train.ipynb]"
```

**NOTE**: If you already know the list of notebooks to link as you create the pipeline you can directly run the command:

```sh
mlp create -p "myfirstpipeline" -n "[notebooks/data_preprocess.ipynb, notebooks/train.ipynb]"
```

### Sync & package a pipeline

The ML pipeline can be packaged into it's own git repository using the following command:

```sh
mlp sync -p "myfirstpipeline"
```

### Pipelines list

To display the list of all created pipelines:

```sh
mlp list
```

### Delete a pipeline

To delete a pipeline from the pipeline registry:

```sh
mlp delete -p "myfirstpipeline"
```

It is also possible to delete all pipelines created from the registry:

```sh
mlp delete  --all or -a
```
### Publishing a pipeline or project

To publish a pipeline you can run the following command:
```sh
mlp publish -p "myfirstpipeline" -m "Message of the publish event"
```

To publish a complete project you can run:

```sh
mlp publish  -m "Message of the publish event"
```


### Run in the cloud

To execute your pipeline in the cloud:
```sh
mlp run_cloud -p "myfirstpipeline" -i c6in.xlarge -s 150
```

The instance type "-i" and the size "-s" is optional and has default values of respectively t2.micro and 30 G.