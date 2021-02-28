aws s3 rm s3://$(pulumi stack output bucket_name)/ --recursive
pulumi destroy -y 
pulumi stack rm $1  