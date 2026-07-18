import os
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import anthropic

from app.deps import get_current_customer
from app.models import Customer

router = APIRouter(prefix="/ai", tags=["ai"])

SECURITY_SYSTEM_PROMPT = """You are ThreatSense AI, a senior cybersecurity expert and educator embedded in the ThreatSense security platform.

Your role is to:
- Help users understand their security findings and vulnerabilities in plain, accessible language
- Explain the real-world risk and impact of each issue
- Provide specific, actionable remediation steps
- Educate clients about security concepts, attack techniques, and best practices
- Answer any cybersecurity questions — from basics to advanced topics
- Reference OWASP, NIST, CVE, and CWE standards where relevant

Tone: professional, clear, and educational. Adapt technical depth to the user's apparent level.
Always be thorough but concise — avoid padding."""


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    include_findings: bool = True


class CodeAnalysisRequest(BaseModel):
    code: str
    language: Optional[str] = "auto-detect"
    filename: Optional[str] = None


def _findings_context(customer_id: str | None = None) -> str:
    from sqlmodel import Session, select
    from app.database import engine
    from app.models import Finding

    with Session(engine) as session:
        q = select(Finding).order_by(Finding.created_at.desc()).limit(60)
        if customer_id:
            q = q.where(Finding.customer_id == customer_id)
        rows = session.exec(q).all()
    if not rows:
        return ""
    lines = ["## Active findings in ThreatSense (your context)\n"]
    for f in rows:
        line = f"- [{f.severity.upper()}] {f.title} | status: {f.status}"
        if f.cve_id:
            line += f" | {f.cve_id}"
        if f.affected_resource:
            line += f" | resource: {f.affected_resource}"
        lines.append(line)
    return "\n".join(lines)


def _get_client() -> Optional[anthropic.AsyncAnthropic]:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    return anthropic.AsyncAnthropic(api_key=key)


async def _no_key_stream():
    yield 'data: {"text": "⚠️ ANTHROPIC_API_KEY is not set. Add it to your environment variables to enable AI features."}\n\n'
    yield "data: [DONE]\n\n"


@router.post("/chat")
async def chat(req: ChatRequest, customer: Customer = Depends(get_current_customer)):
    """Stream an AI security advisor response."""
    client = _get_client()
    if not client:
        return StreamingResponse(_no_key_stream(), media_type="text/event-stream")

    system = SECURITY_SYSTEM_PROMPT
    if req.include_findings:
        ctx = _findings_context(customer.id)
        if ctx:
            system += f"\n\n{ctx}"

    messages = [{"role": m.role, "content": m.content} for m in (req.history or [])]
    messages.append({"role": "user", "content": req.message})

    async def stream():
        try:
            async with client.messages.stream(
                model="claude-opus-4-6",
                max_tokens=2048,
                system=system,
                messages=messages,
            ) as s:
                async for text in s.text_stream:
                    yield f"data: {json.dumps({'text': text})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.post("/analyze-code")
async def analyze_code(
    req: CodeAnalysisRequest,
    customer: Customer = Depends(get_current_customer),
):
    """Analyze source code for security vulnerabilities."""
    _ = customer
    client = _get_client()
    if not client:
        return StreamingResponse(_no_key_stream(), media_type="text/event-stream")

    lang = f" ({req.language})" if req.language and req.language != "auto-detect" else ""
    file_hint = f" from `{req.filename}`" if req.filename else ""

    prompt = f"""Perform a thorough security code review on the following source code{lang}{file_hint}.

For each vulnerability found, provide:
1. **Title & Severity** (Critical / High / Medium / Low / Info)
2. **Location** — line number(s) if identifiable
3. **What it is** — clear explanation of the vulnerability
4. **Attack scenario** — how an attacker could exploit it
5. **Fix** — specific, code-level remediation

After listing all issues, give a brief overall security rating and the top priority fix.

```
{req.code}
```"""

    async def stream():
        try:
            async with client.messages.stream(
                model="claude-opus-4-6",
                max_tokens=4096,
                thinking={"type": "adaptive"},
                system=SECURITY_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            ) as s:
                async for text in s.text_stream:
                    yield f"data: {json.dumps({'text': text})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
