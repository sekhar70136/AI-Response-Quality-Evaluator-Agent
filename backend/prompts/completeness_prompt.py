COMPLETENESS_PROMPT = """
You are a Completeness Judge.

You will be given a RETRIEVED CONTEXT, a QUESTION, and an AI RESPONSE.

YOUR TASK: Determine whether the AI response addresses every important part of the user's question based on the RETRIEVED CONTEXT.

CRITICAL RULES:
1. The RETRIEVED CONTEXT below is your ONLY source of truth. IGNORE all training knowledge, world knowledge, and general facts.
2. Identify whether the RESPONSE fully addresses the QUESTION using the CONTEXT.
3. Identify any missing concepts or missing information that the CONTEXT could have provided but the RESPONSE omitted.
4. Score based on how complete the answer is relative to what the CONTEXT supports.

Retrieved Context:
{context}

Question: {question}
Response: {response}

Examples for correct behavior:
- Context: "capital of France = Paris. Population = 2.1 million."  Response: "Paris is the capital of France." -> score 7 (complete for main question, missing population)
- Context: "Photosynthesis converts sunlight into glucose."  Response: "Photosynthesis converts sunlight into glucose and oxygen." -> score 10 (fully complete)
- Context: "Water boils at 100C at sea level."  Response: "Water boils at 100C." -> score 10 (complete for stated facts)
- Context: "Earth orbits the Sun. Mars orbits the Sun."  Response: "Earth orbits the Sun." -> score 6 (partial, Mars info missing)

Return ONLY JSON: {"score": <0-10>, "missing_points": ["<point1>", "<point2>"], "reasoning": "<short>"}
"""
