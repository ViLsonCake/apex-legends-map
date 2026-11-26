# Apex Legends Map

Telegram bot running on AWS Lambda. It tells you the current Apex Legends map for each game mode, when it changes, and which map comes next. The data comes from the [apexlegendsstatus.com](https://apexlegendsstatus.com) map rotation API.

| Command | Reply |
|---|---|
| `/start` | What the bot does |
| `/pubs` | Battle Royale map, time left, next map |
| `/ranked` | Ranked map, time left, next map |
| `/wildcard` | Wildcard map, or the current event (name, fixed map, time until it ends) |
| `/mixtape` | Mixtape mode (TDM / Control / Gun Run …) and map |

All user-facing text, including the command descriptions shown in Telegram's menu, is in [`src/bot/templates.json`](src/bot/templates.json).

## How it works

Telegram sends each update to a **Lambda Function URL**. The handler first checks the `X-Telegram-Bot-Api-Secret-Token` header. It then fetches `https://api.apexlegendsstatus.com/maprotation?version=2` with your API key in the `Authorization` header. Finally it sends the map image with the reply as its caption (`sendPhoto`), falling back to a plain text message if the image can't be sent. The runtime uses only the Python standard library.

```
src/bot/          Lambda code + templates.json
tests/            pytest suite (uses the sample API response)
scripts/          register_webhook.py (setWebhook + setMyCommands)
infra/            Terraform: Lambda, Function URL, IAM, logs
infra/bootstrap/  Terraform, applied once: state bucket + GitHub OIDC deploy role
.github/workflows CI (tests + terraform validate) and Deploy (on push to main)
```

## Setup

1. **Bootstrap AWS.** Do this once, locally, with admin credentials:
   ```sh
   cd infra/bootstrap
   terraform init
   terraform apply -var github_repo=<owner>/<repo> -var region=us-east-1
   ```
   The bootstrap keeps its own state locally (`infra/bootstrap/terraform.tfstate`, which is gitignored), so keep that file safe.

2. **Configure GitHub.** In *Settings → Secrets and variables → Actions*, add:
   - Variables: `AWS_ROLE_ARN`, `TF_STATE_BUCKET` and `AWS_REGION`, taken from the bootstrap outputs. `AWS_REGION` is optional and defaults to `us-east-1`.
   - Secrets:
     - `TELEGRAM_BOT_TOKEN`: from @BotFather
     - `APEX_API_KEY`: from apexlegendsapi.com
     - `TELEGRAM_WEBHOOK_SECRET`: any random string of 1–256 characters from `A-Z a-z 0-9 _ -`, for example `openssl rand -hex 32`

3. **Deploy.** Push to `main`, or run the *Deploy* workflow by hand. The workflow runs the tests, runs `terraform apply`, then registers the webhook and the command menu with Telegram.

## Development

```sh
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```
