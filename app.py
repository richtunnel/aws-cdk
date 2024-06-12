from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_eks as eks,
    aws_s3 as s3,
    aws_elasticloadbalancingv2 as elb,
    aws_lambda as _lambda,
    aws_kinesis as kinesis
)

class MyInfrastructureStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC
        vpc = ec2.Vpc(
            self, "MyVpc",
            max_azs=3
        )

        # EC2 Instance
        ec2_instance = ec2.Instance(
            self, "MyEC2Instance",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=vpc
        )

        # EKS Cluster
        eks_cluster = eks.Cluster(
            self, "MyEKSCluster",
            version=eks.KubernetesVersion.V1_21,
            vpc=vpc
        )

        # S3 Bucket
        s3_bucket = s3.Bucket(
            self, "MyS3Bucket",
            versioned=True
        )

        # Elastic Load Balancer
        lb = elb.ApplicationLoadBalancer(
            self, "MyLB",
            vpc=vpc,
            internet_facing=True
        )

        listener = lb.add_listener("Listener", port=80)
        listener.add_targets("Target", port=80, targets=[ec2_instance])

        # Kinesis Stream
        kinesis_stream = kinesis.Stream(
            self, "MyKinesisStream",
            shard_count=1
        )

        # Lambda Function
        lambda_function = _lambda.Function(
            self, "MyLambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.handler",
            code=_lambda.Code.from_inline(
                """
                import json

                def handler(event, context):
                    print("Event: ", event)
                    return {
                        'statusCode': 200,
                        'body': json.dumps('Hello from Lambda!')
                    }
                """
            )
        )

        # Grant the Lambda function permissions to read from the Kinesis stream
        kinesis_stream.grant_read(lambda_function)

app = core.App()
MyInfrastructureStack(app, "MyInfrastructureStack")
app.synth()
