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
Clone the repository and install the required packages:

```bash
git clone https://github.com/yegeb/localhost-address-matching.git
cd localhost-address-matching
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

---

## ⚙️ Methodology

We employed a multi-stage approach to tackle address matching:

1.  **Normalization**: Pre-processing the input string to handle common typos and format variations.
2.  **Parsing**:
    *   **Standard Parser**: Uses rule-based logic and lookup trees (e.g., city/district lists) for high-precision matching of known entities.
    *   **Custom NER Model**: A Deep Learning model trained on **synthetic data** to generalize and extract entities from unstructured or noisy inputs.
3.  **Matching**: The extracted components are validated and matched against the official hierarchical address database.

---

## 👥 Contributors

This project was brought to you by the **Localhost** team:

*   **Barış Çakmak**
*   **Tuğçe Yücel**
*   **Ömer Ozan Mart**

---

## 📄 License

[MIT](LICENSE)
