# AWS ECS autodiscovery for Prometheus


## Installation:

```

    $ pip install discoecs

```


## Usage examples - commandline:


Scan ECS tasks every 70 seconds, outputting Prometheus config to `ecs-targets.json` with 8080 as default Prometheus metrics port.
 
```
    
    $ discoecs -v -f ecs-targets.json -p 8080 -i 70

```

Important note: provide AWS credentials and default region in any of the boto3 library standard locations, such as ~/.aws/credentials or using environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`.


## Programmatic use


```
    >>> import boto3
    >>> import discoecs.get_cluster_tasks
    >>> ecs_client = boto3.client('ecs')
    >>> ecs_tasks = get_cluster_tasks(ecs_client)

```

