import os
from dotenv import load_dotenv
from groq import Groq

from embed_and_retrieve import retrieve, get_collection

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
collection = get_collection()


def ask(question):
    # 1. retrieve relevant chunks
    hits = retrieve(question, collection, top_k=5)

    context = "\n\n".join(
        f"[Source: {h['source']}]\n{h['text']}"
        for h in hits
    )

    sources = list(set(h["source"] for h in hits))

    # 2. grounded prompt
    prompt = f"""
Answer ONLY using the context.

For every claim, reference a specific review snippet.

Do NOT summarize across reviews unless the same idea appears in multiple chunks.

If you cannot point to evidence, say "not enough information."
Context:
{context}

Question:
{question}

Return:
1. Answer
2. Sources used (from context)
"""

    # 3. call LLM
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": sources
    }
import gradio as gr

def handle_query(q):
    result = ask(q)
    return result["answer"], "\n".join(result["sources"])

with gr.Blocks() as demo:
    inp = gr.Textbox(label="Ask a question")
    btn = gr.Button("Search")
    out1 = gr.Textbox(label="Answer", lines=10)
    out2 = gr.Textbox(label="Sources")

    btn.click(handle_query, inp, [out1, out2])
    inp.submit(handle_query, inp, [out1, out2])

demo.launch()