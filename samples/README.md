# Sample Files

This directory contains sample files for testing the Brand Engine.

## Synthetic Sample Generator

Since we don't include real brand documents, we provide a synthetic generator that creates minimal test files.

Run the generator:

```bash
cd samples
python generate_samples.py
```

This will create:
- `sample.pptx` - A minimal PowerPoint with theme colors and fonts
- `sample.pdf` - A minimal PDF with text content

## Using Samples

1. Start the services: `docker compose up -d`
2. Register a user and create a brand
3. Upload the sample files
4. Trigger analysis

See the main README for detailed curl examples.
