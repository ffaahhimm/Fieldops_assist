"""
LLM service — configurable provider interface.

Supported providers: openai | anthropic | none
If LLM_PROVIDER=none or the API key is missing, returns a retrieval-only summary.
Never pretends the LLM is working when it has failed.
"""

import logging
from typing import List, Dict, Any, Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)


def generate_answer(
    question: str,
    chunks: List[Dict[str, Any]],
    context: str | None = None,
) -> Tuple[str, bool]:
    """
    Generate an answer grounded in retrieved chunks.

    Returns:
        (answer: str, llm_available: bool)
    """
    if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return _openai_answer(question, chunks, context)
    elif settings.LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
        return _anthropic_answer(question, chunks, context)
    else:
        return _retrieval_only_answer(question, chunks), False


def _build_context_block(chunks: List[Dict]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(
            f"[Source {i}: {c['document_title']}, chunk {c['chunk_index']}]\n{c['content']}"
        )
    return "\n\n---\n\n".join(parts)


SYSTEM_PROMPT = (
    "You are a technical support assistant for an IT and security field service company. "
    "Answer the technician's question using ONLY the documentation excerpts provided below. "
    "If the documentation does not contain enough information, say so clearly — do not invent information. "
    "Always cite the source document name when you quote or reference it. "
    "Recommend safe, non-destructive preliminary checks before any reconfiguration or reset."
)


def _openai_answer(question: str, chunks: List[Dict], context: str | None) -> Tuple[str, bool]:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        context_block = _build_context_block(chunks)
        user_msg = f"Context from ticket/asset: {context}\n\n" if context else ""
        user_msg += f"Documentation:\n{context_block}\n\nQuestion: {question}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=800,
            temperature=0.2,
        )
        return response.choices[0].message.content or "No response from model.", True
    except Exception as e:
        logger.error("OpenAI call failed: %s", e)
        return f"[LLM ERROR] OpenAI call failed: {e}\n\n{_retrieval_only_answer(question, chunks)}", False


def _anthropic_answer(question: str, chunks: List[Dict], context: str | None) -> Tuple[str, bool]:
    try:
        import anthropic as ant
        client = ant.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        context_block = _build_context_block(chunks)
        user_msg = f"Context: {context}\n\n" if context else ""
        user_msg += f"Documentation:\n{context_block}\n\nQuestion: {question}"

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=800,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        return message.content[0].text, True
    except Exception as e:
        logger.error("Anthropic call failed: %s", e)
        return f"[LLM ERROR] Anthropic call failed: {e}\n\n{_retrieval_only_answer(question, chunks)}", False


def _retrieval_only_answer(question: str, chunks: List[Dict]) -> str:
    """
    When no LLM is configured, return a transparent retrieval-only summary.
    Clearly labelled so the user knows this is not AI-generated synthesis.
    """
    lines = [
        "⚠️  AI language model not configured (LLM_PROVIDER=none). "
        "Showing retrieved documentation excerpts only — no AI synthesis.\n",
        f"**Your question:** {question}\n",
        "**Relevant documentation excerpts found:**\n",
    ]
    for i, c in enumerate(chunks, 1):
        lines.append(
            f"**[{i}] {c['document_title']}** (chunk {c['chunk_index']}):\n"
            f"> {c['content'][:500]}{'...' if len(c['content']) > 500 else ''}\n"
        )
    lines.append(
        "\nTo enable AI-generated answers, set LLM_PROVIDER=openai or anthropic "
        "and provide the corresponding API key in your .env file."
    )
    return "\n".join(lines)
