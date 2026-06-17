# notificationSystem

To run the app, first install all requirements specified in requirements.txt, then go to the directory where main.py is located and run:
>  uvicorn main:app

To enable sending warning messages to a slack channel, edit the config file or create an environment variable with name SLACK_WEBHOOK_URL. Also, edit the SIMULATION_MODE variable or create an environment variable with name SIMULATION_MODE.

Example commands to use to check the system
# POST a Warning (forwarded to Slack)
curl -X POST http://127.0.0.1:8000/notifications \
  -H "Content-Type: application/json" \
  -d "{\"Type\": \"Warning\", \"Name\": \"Backup Failure\", \"Description\": \"The backup failed\"}"

# POST an Info (stored only)
curl -X POST http://127.0.0.1:8000/notifications \
  -H "Content-Type: application/json" \
  -d "{\"Type\": \"Info\", \"Name\": \"Quota Exceeded\", \"Description\": \"Compute quota exceeded\"}"

# GET all notifications
curl http://127.0.0.1:8000/notifications

# GET only Warnings
curl "http://127.0.0.1:8000/notifications?type=Warning"

# GET only Info
curl "http://127.0.0.1:8000/notifications?type=Info"

# GET only forwarded ones
curl "http://127.0.0.1:8000/notifications?forwarded=true"

# GET only non-forwarded
curl "http://127.0.0.1:8000/notifications?forwarded=false"

# GET single notification (paste a real UUID from a previous response)
curl http://127.0.0.1:8000/notifications/PASTE-UUID-HERE

# DELETE all notifications
curl -X DELETE http://127.0.0.1:8000/notifications
