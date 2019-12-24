import argparse
import collections
import subprocess
import sys
import time
import typing


import boto3


ExecuteResult = collections.namedtuple('ExecuteResult', ['start', 'end', 'duration', 'retcode'])


def execute(cmdline: typing.List[str]) -> ExecuteResult:

    start = time.time()
    p = subprocess.Popen(cmdline)
    retcode = p.wait()
    end = time.time()

    return ExecuteResult(
        start=start,
        end=end,
        duration=end-start,
        retcode=retcode
    )


def make_parser() -> argparse.ArgumentParser:

    a = argparse.ArgumentParser()

    a.add_argument('--namespace', type=str, default='CommandDuration')
    a.add_argument('--command-name', type=str, required=True)
    a.add_argument('commands', type=str, nargs='+')

    return a


def put_metric(namespace: str, command_name: str, result: ExecuteResult, cwclient):

    data = dict(
        Namespace=namespace,
        MetricData=[
            {
                'MetricName': 'Duration',
                'Dimensions': [
                    {
                        'Name': 'CommandName',
                        'Value': command_name
                    }
                ],
                'Value': result.duration * 1000,
                'Unit': 'Milliseconds'
            },
            {
                'MetricName': 'StatusCode',
                'Dimensions': [
                    {
                        'Name': 'CommandName',
                        'Value': command_name
                    }
                ],
                'Value': result.retcode
            }
        ]
    )

    response = cwclient.put_metric_data(**data)


def main(cmdline: typing.List[str], namespace: str, command_name: str, client) -> ExecuteResult:
    result = execute(cmdline)
    put_metric(namespace, command_name, result, client)

    return result



def entry(args: typing.List[str]=sys.argv[1:]):

    client = boto3.client('cloudwatch')

    arg = make_parser().parse_args(args)

    r = main(arg.commands, arg.namespace, arg.command_name, client)

    sys.exit(r.retcode)




if __name__ == '__main__':
    entry()
