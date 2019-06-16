import argparse
import boto3
import json
import logging
import sys
import time


logger = logging.getLogger(__name__)


def get_cluster_tasks(ecs_client) -> dict:
    cluster_arns_paginator = ecs_client.get_paginator('list_clusters').paginate()
    cluster_tasks = {}
    cluster_arns = []
    for page in cluster_arns_paginator:
        cluster_arns.extend(page['clusterArns'])
    for cluster_arn in cluster_arns:
        logger.info("Cluster ARN %s", cluster_arn)
        cluster_task_arns_paginator = ecs_client.get_paginator('list_tasks').paginate(cluster=cluster_arn)
        cluster_task_definitions = []
        for page in cluster_task_arns_paginator:
            cluster_task_arns = page['taskArns']
            if len(cluster_task_arns) == 0:
                cluster_page_task_definitions = {'tasks': []}
            else:
                cluster_page_task_definitions = ecs_client.describe_tasks(
                    cluster=cluster_arn, tasks=cluster_task_arns
                )
            cluster_task_definitions.extend(cluster_page_task_definitions['tasks'])
        cluster_tasks[cluster_arn] = cluster_task_definitions
    return cluster_tasks


def to_config_items(cluster_tasks, default_port) -> list:
    items = []
    for cluster_arn in cluster_tasks.keys():
        cluster_task_definitions = cluster_tasks[cluster_arn]
        for task in cluster_task_definitions:
            port = default_port
            labels = dict(
                (k, task.get(k, '')) for k in [
                    'clusterArn',
                    'taskArn',
                    'taskDefinitionArn',
                    'lastStatus',
                    'cpu',
                    'memory',
                    'startedBy',
                    'group',
                    'launchtype',
                ]
            )
            ip_address = None
            for container in task.get('containers', []):
                for network_interface in container.get('networkInterfaces', []):
                    ip_address = network_interface.get('privateIpv4Address')
            if ip_address is None:
                logger.info("Skipping task: no IP address %s", str(labels))
            else:
                items.append(
                    dict(
                        targets=[f"{ip_address}:{port}"],
                        labels=labels
                    )
                )
    return items


def main():
    parser = argparse.ArgumentParser(description='ECS Discovery for Prometheus')
    parser.add_argument('-v', action="store_true", default=False)
    parser.add_argument('-f', type=str, required=False, default="ecs-tasks.json",
                        help="Output directory to write Prometheus ECS configs to")
    parser.add_argument('-p', type=int, required=False, default=80,
                        help="Default metrics port")
    parser.add_argument('-i', type=int, required=False, default=60,
                        help="Poll interval, seconds")
    args = parser.parse_args()

    if args.v:
        level = logging.INFO
    else:
        level = logging.WARNING
    logging.basicConfig(level=level)

    ecs_client = boto3.client('ecs')

    if args.p is None:
        default_metrics_port = os.environ.get("DEFAULT_METRICS_PORT", 80)
    else:
        default_metrics_port = args.p

    while True:
        try:
            cluster_tasks = get_cluster_tasks(ecs_client)
            items = to_config_items(cluster_tasks, default_port=default_metrics_port)
            configuration = json.dumps(items, indent=4)
            with open(args.f, "w+") as fo:
                fo.write(configuration)
        except ecs_client.exceptions.AccessDeniedException as e:
            logger.error("Access denied: %s", str(e))
            sys.exit(10)
        except Exception as e:
            logger.error(str(e))
            sys.exit(20)
        else:
            logger.debug("Sleeping for %d seconds before next run...", args.i)
            time.sleep(args.i)


if __name__ == "__main__":
    main()

