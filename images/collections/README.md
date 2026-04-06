# Collection Images Structure

Add your product renders to the appropriate series folder:

```
images/collections/
├── onyx-series/          (has products: crystal-ash, marigold, trinity, luminous-gold, nectar)
│   ├── crystal-ash/      render.png, render-1.png, render-2.png
│   ├── marigold/
│   ├── trinity/
│   ├── luminous-gold/
│   └── nectar/
├── pastel-series/
├── plain-series/         meraki, frost-white, glacier-white
├── calacatta-series/     includes narina-grey, perla-venata (+ existing)
├── budget-series/        black-starlight, brown-starlight, cream-mirror, crema, gracio, grey-starlight, grey-terrazo, halo, snowflake, walnut, white-starlight, white-terrazo
└── carrara-series/        includes blaze (+ existing)
```

**To add a new product:**
1. Create a folder: `images/collections/<series-name>/<product-name>/`
2. Add render images: `render.png`, `render-1.png`, etc.
3. Create product page: `collection-domestic-<series>-<product>.html`
4. Add product card to series page: `collection-domestic-<series>.html`
