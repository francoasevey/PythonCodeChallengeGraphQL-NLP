import anthropic

from data_service.config import settings

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


def ask(question: str, context: str) -> str:
    client = _get_client()
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=context,
        messages=[{"role": "user", "content": question}],
    )
    return message.content[0].text
