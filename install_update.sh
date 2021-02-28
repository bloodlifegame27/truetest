pulumi stack init $1 || pulumi stack select $1
pulumi config set aws:region $2
pulumi up -y
aws s3 sync ./public s3://$(pulumi stack output bucket_name)/ 