from DataWriter.DataWriterBase import DataWriterBase
import os
import boto3


class AWSS3DataWriter(DataWriterBase):
    def __init__(self, dst_bucket:str):
        super(AWSS3DataWriter, self).__init__()
        self.dst_bucket = dst_bucket
        self.s3 = boto3.resource('s3')
        self.client = boto3.client('s3')
        
    def write_data(self, path, filename, acl='public-read'):
        with open(filename, 'rb') as f:
            o_filename = filename.split('/')[-1]
            new_path = os.path.join(path, o_filename)
            data = f.read()
            self.s3.Bucket(self.dst_bucket).put_object(Key=new_path, Body=data, ACL=acl)
        
    def health_check(self) -> bool:
        content = self.client.list_objects_v2(Bucket=self.dst_bucket, MaxKeys=10)
        if len(content['Contents']) == 0:
            return False
        return True