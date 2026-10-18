# Species photos

One photo per species, `images/<slug>.jpg` (slug = the species file name, e.g. `parus-major.jpg`).

Filled by (run from the repo root, after `python _scripts/enrich.py fetch gbif`):

```bash
python _scripts/enrich.py fetch photos -v       # downloads and shrinks the photos (PHOTO_WIDTH=480 PHOTO_QUALITY=70)
python _scripts/enrich.py apply photos          # writes author / licence / source into each species file (`image:`)
```

Only CC0 and CC BY photos are used (iNaturalist research-grade observations through GBIF). The author, licence and
a link to the original are stored in each species file and shown under the photo on the website.
Check the size before committing: `du -sh images`.
