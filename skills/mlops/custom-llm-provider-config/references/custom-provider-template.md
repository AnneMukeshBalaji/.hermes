# Custom Provider Documentation Template

Use this template when adding a new OpenAI-compatible provider to the skill.

---

## Provider: <PROVIDER_NAME>

### Endpoint
```
<BASE_URL>
```

### Authentication
- Type: `API Key` / `Bearer Token` / `OAuth` / `None`
- Header: `Authorization: Bearer <KEY>` / `x-api-key: <KEY>` / etc.
- Env var: `<PROVIDER>_API_KEY`

### Configuration
```bash
hermes config set model.provider custom
hermes config set model.base_url <BASE_URL>
hermes config set model.api_key <API_KEY>
hermes config set model.default <MODEL_ID>
```

### Tested Models

| Model ID | Status | Notes |
|---|---|---|
| `<model-id-1>` | ✅ Works | |
| `<model-id-2>` | ❌ 404 | Not available |
| `<model-id-3>` | 🔒 401 | Requires paid tier |

### Rate Limits
- Requests/min: <X>
- Tokens/min: <Y>
- Concurrent: <Z>

### Context Window
- Default: <N> tokens
- Max: <M> tokens

### Known Issues
- <Any quirks, auto-detection conflicts, etc.>

### Last Verified
- Date: YYYY-MM-DD
- Account tier: Free / Paid / Enterprise

---

## Adding to the Skill

1. Add provider to the "Common Endpoints" table in SKILL.md
2. Create a reference file: `references/<provider-slug>-models.md` using this template
3. Update the "References" section in SKILL.md to link the new file