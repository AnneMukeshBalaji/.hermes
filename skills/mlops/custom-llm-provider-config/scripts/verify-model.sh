#!/usr/bin/env bash
# Quick model verification script for custom LLM providers
# Usage: ./verify-model.sh <MODEL_ID> [BASE_URL] [API_KEY]

set -euo pipefail

MODEL_ID="${1:-}"
BASE_URL="${2:-https://integrate.api.nvidia.com/v1}"
API_KEY="${3:-${NVIDIA_API_KEY:-}}"

if [[ -z "$MODEL_ID" ]]; then
    echo "Usage: $0 <MODEL_ID> [BASE_URL] [API_KEY]"
    echo "  MODEL_ID  - Model identifier (e.g., nvidia/nemotron-3-ultra-550b-a55b)"
    echo "  BASE_URL  - OpenAI-compatible endpoint (default: NVIDIA NIM)"
    echo "  API_KEY   - API key (default: NVIDIA_API_KEY env var)"
    exit 1
fi

if [[ -z "$API_KEY" ]]; then
    echo "Error: API key required. Set NVIDIA_API_KEY env var or pass as 3rd arg."
    exit 1
fi

echo "Testing model: $MODEL_ID"
echo "Endpoint: $BASE_URL"
echo "---"

response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d "{
        \"model\": \"$MODEL_ID\",
        \"messages\": [{\"role\": \"user\", \"content\": \"Hello, respond with just OK\"}],
        \"max_tokens\": 10,
        \"temperature\": 0
    }")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)

if [[ "$http_code" -eq 200 ]]; then
    content=$(echo "$body" | jq -r '.choices[0].message.content // "NO_CONTENT"')
    echo "✅ SUCCESS (HTTP 200)"
    echo "Response: $content"
    exit 0
else
    echo "❌ FAILED (HTTP $http_code)"
    echo "$body" | jq . 2>/dev/null || echo "$body"
    exit 1
fi