import requests

# Check if janis_branch is a real janis branch on our github repo
def validate_janis_branch(janis_branch):
    is_branch_valid = False
    more_branches = True
    github_pagination = 1
    while more_branches:
        # Paginated query for github branches on cityofaustin repo
        github_res = requests.get(
            url=f"https://api.github.com/repos/cityofaustin/janis/branches?per_page=100&page={github_pagination}"
        )

        # Check if there is another page of branches to query
        github_res_link = requests.utils.parse_header_links(github_res.headers["link"])
        more_branches = False
        for x in github_res_link:
            if x["rel"] == "next":
                more_branches=True
                github_pagination=github_pagination+1
                break

        # Check if janis_branch param is one of the queried branches
        branches = github_res.json()
        for x in branches:
            if x["name"] == janis_branch:
                is_branch_valid = True
                break

        # If branch was found, break out of while loop
        # Else, the loop continues if there are more paginated results to be queried
        if is_branch_valid: break

    return is_branch_valid
