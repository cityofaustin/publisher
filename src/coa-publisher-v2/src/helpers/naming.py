import re

# Convert github branch_name to a legal name for an aws container
# Replaces any non letter, number or "-" characters with "-"
# 255 character limit
def github_to_aws(branch_name):
    return re.sub('[^\w\d-]','-',branch_name)[:255]
