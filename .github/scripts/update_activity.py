import os
import requests
import re
from datetime import datetime

USERNAME = "suraz404"
README = "README.md"
TOKEN = os.environ["GITHUB_TOKEN"]

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

url = f"https://api.github.com/users/{USERNAME}/events/public"

response = requests.get(url, headers=headers)

if response.status_code != 200:
    raise Exception(
        f"GitHub API error: {response.status_code} {response.text}"
    )

events = response.json()

activities = []

for event in events:

    event_type = event["type"]
    repo = event["repo"]["name"]

    if event_type == "PushEvent":
        commits = event["payload"].get("commits", [])
        count = len(commits)

        activities.append(
            f"🟢 **Pushed {count} commit{'s' if count != 1 else ''}** to [`{repo}`](https://github.com/{repo})"
        )

    elif event_type == "PullRequestEvent":
        action = event["payload"]["action"]
        number = event["payload"]["number"]

        activities.append(
            f"🔀 **{action.capitalize()} PR #{number}** in [`{repo}`](https://github.com/{repo})"
        )

    elif event_type == "IssuesEvent":
        action = event["payload"]["action"]
        number = event["payload"]["issue"]["number"]

        activities.append(
            f"🐛 **{action.capitalize()} issue #{number}** in [`{repo}`](https://github.com/{repo})"
        )

    elif event_type == "IssueCommentEvent":
        number = event["payload"]["issue"]["number"]

        activities.append(
            f"💬 **Commented on issue #{number}** in [`{repo}`](https://github.com/{repo})"
        )

    elif event_type == "CreateEvent":
        ref_type = event["payload"]["ref_type"]

        if ref_type == "repository":
            activities.append(
                f"🚀 **Created repository** [`{repo}`](https://github.com/{repo})"
            )

    elif event_type == "ReleaseEvent":
        release = event["payload"]["release"]["tag_name"]

        activities.append(
            f"📦 **Released `{release}`** in [`{repo}`](https://github.com/{repo})"
        )

    elif event_type == "ForkEvent":
        activities.append(
            f"🍴 **Forked** [`{repo}`](https://github.com/{repo})"
        )

    elif event_type == "WatchEvent":
        activities.append(
            f"⭐ **Starred** [`{repo}`](https://github.com/{repo})"
        )

    elif event_type == "PublicEvent":
        activities.append(
            f"🌍 **Made repository public** [`{repo}`](https://github.com/{repo})"
        )


# Remove duplicates while preserving order
unique_activities = []

for activity in activities:
    if activity not in unique_activities:
        unique_activities.append(activity)


# Keep latest 8 activities
unique_activities = unique_activities[:8]


if not unique_activities:
    unique_activities = [
        "💻 No recent public activity yet — time to build something!"
    ]


activity_block = "\n".join(
    f"{i + 1}. {activity}"
    for i, activity in enumerate(unique_activities)
)


with open(README, "r", encoding="utf-8") as f:
    readme = f.read()


pattern = r"<!--START_SECTION:activity-->.*?<!--END_SECTION:activity-->"

replacement = (
    "<!--START_SECTION:activity-->\n"
    + activity_block
    + "\n<!--END_SECTION:activity-->"
)

updated_readme = re.sub(
    pattern,
    replacement,
    readme,
    flags=re.DOTALL,
)


if updated_readme == readme:
    raise Exception(
        "Could not find activity markers in README.md"
    )


with open(README, "w", encoding="utf-8") as f:
    f.write(updated_readme)


print("README activity updated successfully.")
print()
print(activity_block)
