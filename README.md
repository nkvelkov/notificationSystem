# notificationSystem

To run the app go to the directory where main.py is located and run:
>  uvicorn main:app

# POST a Warning (forwarded to Teams)
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
