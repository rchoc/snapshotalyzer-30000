import boto3

#print("test")


if __name__ == '__main__':

    session = boto3.Session(profile_name='acg-python')
    ec2 = session.resource('ec2')
    
    for i in ec2.instances.all():
        print (i)
