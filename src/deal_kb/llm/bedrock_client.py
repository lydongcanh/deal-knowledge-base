"""Client wrapper for invoking Anthropic models via AWS Bedrock's Converse API."""

import boto3

from deal_kb.config import settings


class BedrockChatClient:
    """Thin wrapper around the Bedrock Runtime `converse` API for chat completions."""

    def __init__(self, model_id: str | None = None, region: str | None = None) -> None:
        self._model_id = model_id or settings.bedrock_model_id
        self._client = boto3.client("bedrock-runtime", region_name=region or settings.aws_region)

    def ask(self, question: str, context: str, system_prompt: str) -> str:
        """Send a grounded question + retrieved graph context to the model and return its reply."""
        response = self._client.converse(
            modelId=self._model_id,
            system=[{"text": system_prompt}],
            messages=[
                {
                    "role": "user",
                    "content": [{"text": f"Context from the deal graph:\n{context}\n\nQuestion: {question}"}],
                }
            ],
            inferenceConfig={"temperature": 0.2, "maxTokens": 1024},
        )
        return response["output"]["message"]["content"][0]["text"]
