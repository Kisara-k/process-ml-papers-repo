import requests

url = "https://raw.githubusercontent.com/dair-ai/ML-Papers-of-the-Week/main/README.md"
output_file = "papers.md"

response = requests.get(url)
response.raise_for_status()  # Raise an error for bad status codes

with open(output_file, "w", encoding="utf-8") as f:
    f.write(response.text)

with open(output_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

start = next(i for i, line in enumerate(lines) if line.startswith("## Top ML Papers "))
end = max(i for i, line in enumerate(lines) if line.strip() == "---")
cleaned_lines = lines[start:end]

with open(output_file, "w", encoding="utf-8") as f:
    f.writelines(cleaned_lines)
