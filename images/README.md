# Species photos

Photos mirror the `birds/` folder: the species `birds/passeriformes/paridae/parus-major.md` has its photos in
`images/passeriformes/paridae/parus-major/1.jpg`, `2.jpg`, `3.jpg` ... (1 = the first / main photo). Each species file
lists them under `images:` (and the first as `image:`) with author, licence and a link to the original; the website
shows them as a small gallery. If a species is ever moved to another family, its photos stay where `images:` points.

Filled by (run from the repo root):

```bash
python _scripts/enrich.py fetch gbif -w 2 --delay 0.1       # remembers up to 30 open-licence photos per species (a photo-only lookup for species already cached)
python _scripts/enrich.py fetch photos -v --max-photos 5    # downloads the first 5 of each (0 = all remembered); PHOTO_WIDTH=480 PHOTO_QUALITY=70
python _scripts/enrich.py apply photos                      # writes image / images into the species files (rerun after changing --max-photos)
```

Only CC0 and CC BY photos are used (iNaturalist research-grade observations through GBIF), different photographers first.
Photos average about 28 KB at the default size. Git keeps every version forever, so check `du -sh images` before
committing and choose `--max-photos` accordingly.
