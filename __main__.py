import json
import mimetypes
import os


from pulumi import export, FileAsset, AssetArchive, FileArchive
from pulumi_aws import s3
import pulumi_aws as aws

web_bucket = s3.Bucket('s3-website-bucket',
    website=s3.BucketWebsiteArgs(
        index_document="index.html",
    ))

# content_dir = "www"
# for file in os.listdir(content_dir):
#     filepath = os.path.join(content_dir, file)
#     if os.path.isfile(filepath):
#         mime_type, _ = mimetypes.guess_type(filepath)
#         obj = s3.BucketObject(file,
#             bucket=web_bucket.id,
#             source=FileAsset(filepath),
#             content_type=mime_type)


#
#
#

def public_read_policy_for_bucket(bucket_name):
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                f"arn:aws:s3:::{bucket_name}/*",
            ]
        }]
    })

bucket_name = web_bucket.id
bucket_policy = s3.BucketPolicy("bucket-policy",
    bucket=bucket_name,
    policy=bucket_name.apply(public_read_policy_for_bucket))
s3_origin_id = "myS3Origin"


s3_distribution = aws.cloudfront.Distribution("s3Distribution",
    origins=[aws.cloudfront.DistributionOriginArgs(
        domain_name=web_bucket.bucket_regional_domain_name,
        origin_id=s3_origin_id,
    )],
    enabled=True,
    is_ipv6_enabled=False,
    comment="Some comment",
    default_root_object="index.html",
    default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
        allowed_methods=[
            "DELETE",
            "GET",
            "HEAD",
            "OPTIONS",
            "PATCH",
            "POST",
            "PUT",
        ],
        cached_methods=[
            "GET",
            "HEAD",
        ],
        target_origin_id=s3_origin_id,
        forwarded_values=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
            query_string=False,
            cookies=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                forward="none",
            ),
        ),
        viewer_protocol_policy="allow-all",
        min_ttl=0,
        default_ttl=3600,
        max_ttl=86400,
    ),
    ordered_cache_behaviors=[
        aws.cloudfront.DistributionOrderedCacheBehaviorArgs(
            path_pattern="/content/immutable/*",
            allowed_methods=[
                "GET",
                "HEAD",
                "OPTIONS",
            ],
            cached_methods=[
                "GET",
                "HEAD",
                "OPTIONS",
            ],
            target_origin_id=s3_origin_id,
            forwarded_values=aws.cloudfront.DistributionOrderedCacheBehaviorForwardedValuesArgs(
                query_string=False,
                headers=["Origin"],
                cookies=aws.cloudfront.DistributionOrderedCacheBehaviorForwardedValuesCookiesArgs(
                    forward="none",
                ),
            ),
            min_ttl=0,
            default_ttl=86400,
            max_ttl=31536000,
            compress=True,
            viewer_protocol_policy="redirect-to-https",
        ),
        aws.cloudfront.DistributionOrderedCacheBehaviorArgs(
            path_pattern="/content/*",
            allowed_methods=[
                "GET",
                "HEAD",
                "OPTIONS",
            ],
            cached_methods=[
                "GET",
                "HEAD",
            ],
            target_origin_id=s3_origin_id,
            forwarded_values=aws.cloudfront.DistributionOrderedCacheBehaviorForwardedValuesArgs(
                query_string=False,
                cookies=aws.cloudfront.DistributionOrderedCacheBehaviorForwardedValuesCookiesArgs(
                    forward="none",
                ),
            ),
            min_ttl=0,
            default_ttl=3600,
            max_ttl=86400,
            compress=True,
            viewer_protocol_policy="redirect-to-https",
        ),
    ],
    price_class="PriceClass_200",

    restrictions=aws.cloudfront.DistributionRestrictionsArgs(
        geo_restriction=aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
            restriction_type="none",
        ),
    ),
    viewer_certificate=aws.cloudfront.DistributionViewerCertificateArgs(
        cloudfront_default_certificate=True,
    ))




# Export the name of the bucket
export('bucket_name', web_bucket.id)
export('website_url_s3', web_bucket.website_endpoint)
export('website_url_cloudfront', s3_distribution.domain_name)

