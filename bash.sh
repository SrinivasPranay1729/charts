# Example values
SERVER_HOST="https://example-mwaa-server.amazonaws.com"
ENV_NAME="my-airflow-env"
WEB_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
VARIABLES='{"Variables": {"AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION": "True", "MY_CUSTOM_VARIABLE": "custom_value"}}'

# Make the API request using curl
curl -X POST \
  "$SERVER_HOST/environments/$ENV_NAME/variables" \
  -H "Authorization: Bearer $WEB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$VARIABLES"
