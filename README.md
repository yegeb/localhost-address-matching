# Localhost Address Matching

> **A hybrid address matching and normalization library for Turkish addresses.**

This project captures the **matching**, **normalization**, and **parsing** of address strings. It was developed to handle complex address data, leveraging both standard rule-based parsing and custom Named Entity Recognition (NER) models.

---

## 🏆 About the Project

This project was developed for the **TEKNOFEST 2025 Hepsiburada AI Hackathon**.

Our goal was to solve the challenge of unstructured address data by building a robust pipeline that can parse, normalize, and match addresses with high accuracy.

### Key Features
- **Normalization**: Standardizes address text (lowercasing, abbreviation expansion, removing noise).
- **Hybrid Parsing**: Combines a standard static parser with a custom NER-based model.
- **Synthetic Data**: The NER model was trained using a large corpus of synthetically generated address data, grouped by data categories to ensure robustness.
- **Address Matching**: Matches parsed addresses against a reference dataset (e.g., PTT database).

---

## 🚀 Installation

### Prerequisites
- Python 3.8+

### Install Dependencies

It is recommended to use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 💻 Usage

matches can be performed using the `StaticAddressParser` or the NER-based parser.

### Basic Example (Static Parser)

```python
from src.address_matching.parsing.static_parser import StaticAddressParser

# Initialize the parser
parser = StaticAddressParser()

# Parse an address string
address_text = "Caferağa Mah., Kadıköy / İstanbul No:12 D:5"
result = parser.parse(address_text)

print(result)
# Output:
# Province: İstanbul
# District: Kadıköy
# Neighbourhood: Caferağa
# ...
```

### Dynamic Parsing (NER Model)

To use the custom Named Entity Recognition model, you need a trained model directory.

```python
from src.address_matching.parsing.ner_address_parser import load_pipeline, process_batch

# Load the trained model
model_dir = "models/BERTurk_stage1_out"  # Path to your fine-tuned model
pipe = load_pipeline(model_dir)

# Address to parse
address_text = "Barbaros Bulvarı No:12 Beşiktaş İstanbul"

# Process
results = process_batch(pipe, [address_text], max_length=512)

# View extracted entities
print(results[0]['entities_json'])
# Output example:
# [{"type": "district", "text": "Beşiktaş", ...}, {"type": "province", "text": "İstanbul", ...}]
```

---

## 👥 Contributors

This project was brought to you by the **localhost** team:

*   **Yüksel Ege Boyacı (me)**
*   **Barış Çakmak**
*   **Tuğçe Yücel**
*   **Ömer Ozan Mart**