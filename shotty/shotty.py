import boto3
import click
import botocore

session = boto3.Session(profile_name='acg-python')
ec2 = session.resource('ec2')


def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name': 'tag:Project', 'Values': [project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances


def has_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'


@click.group()
def cli():
    """Shotty manages snapshots"""


@cli.group('snapshots')
def snapshots():
    """Command for snapshots"""


@snapshots.command('list')
@click.option('--project', default=None,
              help="Only snapshots for project (tag Project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True,
              help="List all snapshots for all volumes, not just the recent one.")
def list_snapshots(project, list_all):
    "List ec2 snapshots"
    instances = filter_instances(project)

    for i in instances:
        tags = {t['Key']: t['Value'] for t in i.tags or []}
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c"),
                    tags.get('Project', '<no project>')
                )))

                if s.state == 'completed' and not list_all:
                    break

    return


@cli.group('volumes')
def volumes():
    """Command for volumes"""


@volumes.command('list')
@click.option('--project', default=None,
              help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List ec2 volumes"
    instances = filter_instances(project)
    for i in instances:
        tags = {t['Key']: t['Value'] for t in i.tags or []}
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted",
                tags.get('Project', '<no project>')
            )))
    return


@cli.group('instances')
def instances():
    """Commands for instances"""


@instances.command('list')
@click.option('--project', default=None,
              help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List ec2 instances"
    instances = filter_instances(project)

    for i in instances:
        tags = {t['Key']: t['Value'] for t in i.tags or []}
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.private_dns_name,
            tags.get('Project', '<no project>')
        )))
    return


@instances.command('stop')
@click.option('--project', default=None,
              help="Only instances for project (tag Project:<name>)")
def stop_instances(project):
    "Stop EC2 instances"
    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as err:
            print(" Could not stop {0}. ".format(i.id) + str(err))
            continue

    return


@instances.command('start')
@click.option('--project', default=None,
              help="Only instances for project (tag Project:<name>)")
def start_instances(project):
    "Start EC2 instances"
    instances = filter_instances(project)

    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as err:
            print(" Could not start {0}. ".format(i.id) + str(err))
            continue

    return


@instances.command('snapshot',
                   help="Create snapshot for all volumes")
@click.option('--project', default=None,
              help="Only instances for project (tag Project:<name>)")
def create_snapshots(project):
    "Create snapshots for all volumes of EC2 instances"
    instances = filter_instances(project)
    for i in instances:
        print("Stopping {0}...".format(i.id))
        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print("Skipping {0}, snapshot already in progress.".format(v.id))
                continue
            print(" Creating snapshot of {}".format(v.id))
            v.create_snapshot(Description="Created by SnapshotAlyzer30000")

        print("Starting {0}...".format(i.id))
        i.start()
        i.wait_until_running()

    print("Jobs done!!")

    return


if __name__ == '__main__':
    # list_instances()
    cli()
