# Hero Video Optimization (Performance)

For smooth scroll-driven video on the hero section:

## Recommended video specs
- **File size:** 3–5 MB (compress with HandBrake, FFmpeg, or similar)
- **Resolution:** ~1920px width (1080p or 1920×1080)
- **Format:** MP4 (H.264)

## Preload setting
The hero video uses `preload="metadata"` so the browser loads only metadata (duration, dimensions) initially. Full video loads as the user scrolls. This improves initial page load.

## Compress with FFmpeg (example)
```bash
ffmpeg -i input.mp4 -vcodec libx264 -crf 28 -preset medium -vf "scale=1920:-2" -movflags +faststart output.mp4
```

## Compress with HandBrake
- Preset: Web > Gmail
- Resolution: 1920 width, auto height
- Target: ~4 MB
