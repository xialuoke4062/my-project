# Instagram Media Downloader

Agentic browser automation tool for downloading Instagram images and videos by monitoring network requests (simulating the manual DevTools Network tab method).

## What This Does

This tool automates the process you described:
1. Opens Instagram in a browser (mobile view for better quality)
2. Logs in with your credentials
3. Monitors network requests (like the Network tab in DevTools)
4. Clicks through Instagram posts
5. Captures media URLs (images and videos from Instagram CDN)
6. Downloads all captured media automatically

## Files Included

1. **`instagram_media_downloader.ipynb`** - Full-featured Jupyter notebook with detailed documentation
2. **`instagram_downloader_simple.py`** - Standalone Python script for quick use

## Installation

### Option 1: Quick Setup
```bash
pip install playwright requests instaloader
playwright install chromium
```

### Option 2: Using Requirements File
Create a `requirements.txt`:
```
playwright>=1.40.0
requests>=2.31.0
instaloader>=4.11.0
```

Then install:
```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

### Method 1: Jupyter Notebook (Recommended for Interactive Use)

1. Open the notebook:
   ```bash
   jupyter notebook instagram_media_downloader.ipynb
   ```

2. Update the configuration cell:
   ```python
   INSTAGRAM_USERNAME = "your_username"
   INSTAGRAM_PASSWORD = "your_password"
   ```

3. Run the cells to start downloading

### Method 2: Python Script (Quick Automation)

1. Edit the script and update credentials:
   ```python
   USERNAME = "your_username"
   PASSWORD = "your_password"
   PROFILE_URL = "https://www.instagram.com/profile_to_download/"
   NUM_POSTS = 5
   ```

2. Run the script:
   ```bash
   python instagram_downloader_simple.py
   ```

### Method 3: Using Instaloader (Simplest, No Browser)

```python
import instaloader

L = instaloader.Instaloader(
    download_videos=True,
    download_video_thumbnails=False,
    download_comments=False,
)

# Optional: Login for private accounts
L.login("username", "password")

# Download from profile
profile = instaloader.Profile.from_username(L.context, "natgeo")
for post in profile.get_posts():
    L.download_post(post, target="natgeo_downloads")
```

## Features

### Browser Automation Approach
- ✅ Real browser automation (like doing it manually)
- ✅ Network request monitoring (captures media URLs from CDN)
- ✅ Mobile view support (often provides better quality)
- ✅ Handles carousels (multiple images/videos in one post)
- ✅ Automatic login and popup handling
- ✅ Click-through navigation between posts
- ✅ Video and image support

### Instaloader Approach
- ✅ Simple command-line tool
- ✅ No browser needed
- ✅ Supports hashtags, stories, profiles
- ✅ Download metadata and comments
- ✅ Fast and efficient

## How It Works (Browser Automation Method)

This replicates your manual process:

1. **Opens Browser** - Launches Chromium in mobile view
2. **Network Monitoring** - Listens to all network responses (like DevTools Network tab)
3. **Login** - Automatically logs in to your Instagram account
4. **Navigate** - Clicks through posts like you would manually
5. **Capture** - When images/videos load, captures their URLs from `cdninstagram.com`
6. **Download** - Downloads all captured media to a folder

### Network Tab Simulation

The script monitors these patterns (just like filtering in Network tab):
- **Images**: `cdninstagram.com` + `content-type: image/*`
- **Videos**: `.mp4` URLs or `content-type: video/*`

## Manual Method (Reference)

If you prefer doing it manually as you described:

1. Open Instagram in browser
2. Press **F12** (Developer Tools)
3. Go to **Network** tab
4. Filter by: `media` or `video`
5. Navigate to a post
6. Refresh the page
7. Look for requests:
   - Images: from `cdninstagram.com`
   - Videos: ending in `.mp4`
8. Right-click → "Open in new tab"
9. Save the media file

**The automation above does this for you!**

## Configuration Options

### Jupyter Notebook
```python
# Instagram credentials
INSTAGRAM_USERNAME = "your_username"
INSTAGRAM_PASSWORD = "your_password"

# Download settings
DOWNLOAD_FOLDER = "instagram_downloads"
USE_MOBILE_VIEW = True  # Mobile view = better quality
HEADLESS = False  # Set True to hide browser
```

### Python Script
```python
downloader = InstagramMediaDownloader(
    username="your_username",
    password="your_password",
    download_folder="downloads"
)

await downloader.browse_and_download(
    profile_url="https://www.instagram.com/username/",
    num_posts=10
)
```

## Output

Downloads are saved to `instagram_downloads/` folder:
```
instagram_downloads/
├── image_20241022_143022_1234.jpg
├── video_20241022_143025_5678.mp4
├── image_20241022_143030_9012.jpg
└── ...
```

## Tips & Best Practices

1. **Rate Limiting**: Don't download too many posts at once (Instagram may flag)
2. **Mobile View**: Often provides higher quality media URLs
3. **Delays**: The script includes delays between actions to appear more human
4. **Error Handling**: Built-in retry logic for network failures
5. **Terms of Service**: Only download content you have permission to access

## Troubleshooting

### Login Issues
- Check username/password
- Instagram may require 2FA (you'll need to manually verify)
- Try running with `headless=False` to see what's happening

### No Media Captured
- Increase wait times between posts
- Check that posts contain images/videos
- Verify network monitoring is working

### Downloads Fail
- Check internet connection
- Some URLs may expire quickly
- Try downloading immediately after capture

## Advanced Usage

### Custom Post Selection
```python
# Download specific post
await page.goto("https://www.instagram.com/p/POST_ID/")
await asyncio.sleep(3)
# Media will be captured automatically
```

### Filter Media Types
```python
# In MediaCollector class, modify capture logic
if media_type == 'video' and '.mp4' in url:
    self.media_urls.add(('video', url))
```

## Legal & Ethical Considerations

- ⚠️ Respect Instagram's Terms of Service
- ⚠️ Only download content you have rights to access
- ⚠️ Don't use for scraping public data at scale
- ⚠️ Respect copyright and intellectual property
- ✅ Good for: Personal backups, archiving your own content
- ❌ Bad for: Unauthorized redistribution, bulk scraping

## Comparison: Browser Automation vs Instaloader

| Feature | Browser Automation | Instaloader |
|---------|-------------------|-------------|
| Setup | More complex | Simple |
| Speed | Slower (real browser) | Faster |
| Like Manual Process | Yes ✓ | No |
| Network Monitoring | Yes ✓ | No |
| Stories Support | Limited | Yes ✓ |
| Metadata | Limited | Yes ✓ |
| Detection Risk | Higher | Lower |

## Support

For issues related to:
- **Playwright**: https://playwright.dev/python/docs/intro
- **Instaloader**: https://instaloader.github.io/
- **Instagram API changes**: May break automation (update selectors)

## License

Use at your own risk. This tool is for educational and personal use only.
