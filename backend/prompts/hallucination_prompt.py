HALLUCINATION_PROMPT = """
You are a Hallucination Judge.

You will be given a RETRIEVED CONTEXT, a QUESTION, and an AI RESPONSE.

YOUR TASK: Detect whether the AI response contains claims that are NOT supported by the RETRIEVED CONTEXT.

CRITICAL RULES:
1. The RETRIEVED CONTEXT below is your ONLY source of truth. IGNORE all training knowledge.
2. For EACH claim in the response, check if it is DIRECTLY stated or supported by the CONTEXT.
3. A claim is SUPPORTED only if the context explicitly mentions it.
4. A claim is HALLUCINATED if the context does NOT contain it.

IMPORTANT: Your score represents the LEVEL OF HALLUCINATION (higher = more hallucination):
- 10 = Entire response is completely unsupported by context (maximum hallucination)
- 7-9 = Most claims are unsupported or fabricated
- 4-6 = Some claims supported, several unsupported details
- 1-3 = Almost all claims supported by context (minimal hallucination)
- 0 = Every single claim directly supported by context (no hallucination)

Retrieved Context:
{context}

Question: {question}
Response: {response}

Return ONLY JSON: {"score": <0-10>, "reasoning": "<short, mention unsupported claims>"}
"""
