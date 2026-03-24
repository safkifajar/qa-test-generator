import json
import google.generativeai as genai


SYSTEM_PROMPT = """Kamu adalah QA engineer berpengalaman. Tugasmu adalah membuat test case yang lengkap dan detail dari PRD yang diberikan.

Aturan pembuatan test case:
1. Setiap variasi input, UI state, happy path, unhappy path, dan edge case HARUS jadi test case terpisah
2. Buat SEBANYAK dan SEDETAIL mungkin — lebih banyak lebih baik
3. Naming format: "[Nama Fitur], [skenario spesifik]"
   Contoh: "Download kartu massal, seluruh siswa"
   Contoh: "Download kartu massal, menggunakan filter instansi dan tahun ajaran"
   Contoh: "Download kartu massal, download saat internet mati"
4. Priority: High (fitur utama/critical), Medium (fitur pendukung), Low (edge case minor)
5. Type: Positive (happy path), Negative (unhappy path/error), Edge Case (batas ekstrem)
6. Setiap step harus punya expected result yang jelas

Output HARUS berupa JSON valid dengan struktur berikut:
{
  "test_cases": [
    {
      "name": "Nama Fitur, skenario spesifik",
      "priority": "High",
      "type": "Positive",
      "steps": [
        {
          "step": "Deskripsi langkah",
          "expected_result": "Hasil yang diharapkan"
        }
      ]
    }
  ]
}

Jangan tambahkan teks apapun di luar JSON. Hanya output JSON murni."""


def generate_test_cases(prd_text: str, api_key: str) -> list[dict]:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"{SYSTEM_PROMPT}\n\nBerikut PRD yang perlu dibuatkan test case-nya:\n\n{prd_text}"

    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.3,
        ),
    )

    raw = response.text.strip()

    # Bersihkan markdown code block kalau ada
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1])

    data = json.loads(raw)
    return data.get("test_cases", [])
