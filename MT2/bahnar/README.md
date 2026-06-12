# Bahnar Translation Experiments
## Zero-shot Vietnamese ↔ Bahnar Translation

This directory contains code for translating between Vietnamese and Bahnar using GPT-4o via Azure OpenAI.

### Structure

```
bahnar/
├── data/
│   └── vi_bahnar.jsonl          # Source data with Vi-Bahnar pairs
├── results/                     # Output translation results
├── translate_vi_to_bahnar_zeroshot.py
├── translate_bahnar_to_vi_zeroshot.py
├── setup.py                     # Setup verification script
└── README.md                    # This file
```

### Data Format

Input JSONL format:
```json
{
  "id": 68942,
  "text": "Vietnamese text here",
  "topic": "TOPIC_NAME",
  "order": 1.0,
  "label": ["Bahnar translation here"],
  "Comments": []
}
```

Output JSONL format:
```json
{
  "id": 68942,
  "source_vi": "Vietnamese text",
  "reference_bahnar": "Reference Bahnar",
  "predicted_bahnar": "Model predicted Bahnar",
  "topic": "TOPIC_NAME",
  "order": 1.0
}
```

### Setup

#### 1. Environment Variables

Make sure `.env` file exists in the parent directory with:
```
AZURE_TENANT_ID=<your_tenant_id>
APPLICATION_AI_VOS_USERS_ID=<your_client_id>
APPLICATION_AI_VOS_USERS_SECRET=<your_client_secret>
AZURE_OPENAI_ENDPOINT=<your_endpoint>
AZURE_API_VERSION=2024-05-01-preview
AZURE_CHAT_DEPLOYMENT=gpt-4o-RTA_Configurator
HTTPS_PROXY=<proxy_if_needed>
```

#### 2. Install Dependencies

```bash
pip install python-dotenv openai azure-identity httpx sacrebleu
```

#### 3. Verify Setup

Run the setup verification script:
```bash
python setup.py
```

Expected output:
- ✓ All environment variables set
- ✓ Data file found (vi_bahnar.jsonl)
- ✓ Output directory created
- ✓ All dependencies installed

### Usage

#### Translate Vietnamese → Bahnar

```bash
python translate_vi_to_bahnar_zeroshot.py
```

**What it does:**
1. Loads Vietnamese texts from `data/vi_bahnar.jsonl`
2. Sends each Vietnamese text to GPT-4o with a zero-shot prompt
3. Collects Bahnar translations
4. Computes BLEU and chrF++ metrics against references
5. Saves results to `results/vi_to_bahnar_zeroshot_TIMESTAMP.jsonl`

**Output:**
- Console: Translation progress and metrics
- File: JSONL with all translations and references

#### Translate Bahnar → Vietnamese

```bash
python translate_bahnar_to_vi_zeroshot.py
```

**What it does:**
1. Loads Bahnar texts from the `label` field in `data/vi_bahnar.jsonl`
2. Sends each Bahnar text to GPT-4o with a zero-shot prompt
3. Collects Vietnamese translations
4. Computes BLEU and chrF++ metrics against references (original Vietnamese)
5. Saves results to `results/bahnar_to_vi_zeroshot_TIMESTAMP.jsonl`

### Zero-shot Approach

Both scripts use **zero-shot translation** without few-shot examples:
- Single system prompt defining the translation task
- No example translations provided
- Directly translates using model's linguistic knowledge
- Relies on GPT-4o's multilingual capabilities

### System Prompts

**Vi → Bahnar:**
```
"You are an expert translator specializing in Vietnamese-Bahnar translation. 
You have deep knowledge of Bahnar language, culture, and linguistic patterns. 
Translate the following Vietnamese text into Bahnar (a language spoken in Vietnam's Central Highlands). 
Preserve cultural nuances and ensure the translation sounds natural in Bahnar. 
Output ONLY the Bahnar translation, nothing else."
```

**Bahnar → Vi:**
```
"You are an expert translator specializing in Bahnar-Vietnamese translation. 
You have deep knowledge of Bahnar language, culture, and linguistic patterns. 
Translate the following Bahnar text (a language spoken in Vietnam's Central Highlands) into Vietnamese. 
Preserve cultural nuances and ensure the translation sounds natural in Vietnamese. 
Output ONLY the Vietnamese translation, nothing else."
```

### Evaluation Metrics

The scripts compute:
- **BLEU**: Bilingual Evaluation Understudy (lexical precision)
- **chrF++**: Character n-gram F-score with word order (handles morphology better)
- **Sample count**: Number of translations

### Troubleshooting

**Error: "Data file not found"**
- Check that `data/vi_bahnar.jsonl` exists
- Verify the file has valid JSONL format

**Error: "Azure authentication failed"**
- Verify environment variables are set correctly in `.env`
- Check Azure credentials haven't expired
- Verify proxy settings if behind corporate firewall

**Error: "Rate limited"**
- Azure OpenAI may throttle requests
- Script has automatic retry logic with exponential backoff
- Consider reducing batch size

**Low BLEU/chrF++ scores**
- Zero-shot approach may not capture all nuances
- Consider implementing few-shot examples (see `experiments/gpt4o/`)
- Explore prompt engineering improvements

### Next Steps

After zero-shot baseline, consider:

1. **Few-shot Translation** (`experiments/gpt4o/experiment_*.py` for reference)
   - Add 3-5 representative examples to prompts
   - May improve quality on similar types of text

2. **Context-aware Translation**
   - Use dialogue context for conversational texts
   - Preserve cultural terms across multi-turn dialogues

3. **Prompt Engineering**
   - Experiment with different system prompts
   - Add cultural background information
   - Include domain-specific terminology

4. **Evaluation**
   - Manual evaluation of cultural entity preservation
   - Fluency assessment by native speakers
   - Error analysis and pattern identification

### References

- [sacrebleu Documentation](https://github.com/mjpost/sacrebleu)
- [Azure OpenAI API](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference)
- [Machine Translation Evaluation](https://aclanthology.org/)

### Author Notes

- Data path: `C:\Users\HOY9HC\Desktop\Code\Learning\MT2\bahnar\data\vi_bahnar.jsonl`
- Results are time-stamped for easy tracking
- All output in UTF-8 encoding for proper Bahnar character support
- Temperature set to 0.0 for deterministic translations
