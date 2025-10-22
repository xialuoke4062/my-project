#!/usr/bin/env python3
"""
Simple Instagram Media Downloader using Browser Network Monitoring
This script automates the process you described: inspecting network tab and downloading media
"""

import asyncio
import os
import requests
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright


class InstagramMediaDownloader:
    def __init__(self, username, password, download_folder="instagram_downloads"):
        self.username = username
        self.password = password
        self.download_folder = download_folder
        self.media_urls = set()
        self.downloaded_urls = set()
        Path(download_folder).mkdir(exist_ok=True)

    def capture_media_url(self, response):
        """Capture media URLs from network responses (like Network tab in DevTools)"""
        url = response.url
        content_type = response.headers.get('content-type', '')

        # Capture images from Instagram CDN
        if 'image' in content_type and 'cdninstagram.com' in url:
            self.media_urls.add(('image', url))
            print(f"📷 Captured image: {url[:80]}...")

        # Capture videos
        elif 'video' in content_type or '.mp4' in url:
            self.media_urls.add(('video', url))
            print(f"🎥 Captured video: {url[:80]}...")

    def download_media(self, media_type, url):
        """Download a media file"""
        if url in self.downloaded_urls:
            return

        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ext = '.mp4' if media_type == 'video' else '.jpg'
            url_hash = abs(hash(url)) % 10000
            filename = f"{media_type}_{timestamp}_{url_hash}{ext}"
            filepath = os.path.join(self.download_folder, filename)

            response = requests.get(url, stream=True, timeout=30)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                self.downloaded_urls.add(url)
                file_size = os.path.getsize(filepath) / 1024 / 1024  # MB
                print(f"✓ Downloaded: {filename} ({file_size:.2f} MB)")
                return filepath
        except Exception as e:
            print(f"✗ Error downloading {url[:50]}: {str(e)}")
        return None

    async def login(self, page):
        """Login to Instagram"""
        print("\n🔐 Logging in to Instagram...")

        await page.goto('https://www.instagram.com/')
        await asyncio.sleep(3)

        try:
            await page.wait_for_selector('input[name="username"]', timeout=10000)
            await page.fill('input[name="username"]', self.username)
            await page.fill('input[name="password"]', self.password)
            await page.click('button[type="submit"]')
            await asyncio.sleep(5)

            # Handle popups
            for button_text in ["Not now", "Not Now"]:
                try:
                    button = page.locator(f'button:has-text("{button_text}")')
                    if await button.count() > 0:
                        await button.first.click()
                        await asyncio.sleep(2)
                except:
                    pass

            print("✓ Logged in successfully\n")
            return True
        except Exception as e:
            print(f"✗ Login failed: {str(e)}")
            return False

    async def browse_and_download(self, profile_url, num_posts=5):
        """Browse Instagram and download media (simulating your manual process)"""
        async with async_playwright() as p:
            # Launch browser in mobile view (better quality as you mentioned)
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={'width': 375, 'height': 812},
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15'
            )
            page = await context.new_page()

            # Set up network monitoring (like Network tab in DevTools)
            page.on('response', self.capture_media_url)

            try:
                # Login
                if not await self.login(page):
                    return

                # Navigate to profile
                print(f"📱 Opening profile: {profile_url}")
                await page.goto(profile_url)
                await asyncio.sleep(3)

                # Click first post
                first_post = page.locator('article a').first
                await first_post.click()
                await asyncio.sleep(3)

                # Navigate through posts
                for i in range(num_posts):
                    print(f"\n--- Post {i+1}/{num_posts} ---")
                    await asyncio.sleep(3)

                    # Handle carousel posts (multiple images/videos)
                    try:
                        next_carousel = page.locator('button[aria-label="Next"]').first
                        carousel_count = 0
                        while carousel_count < 10:
                            if await next_carousel.is_visible():
                                await next_carousel.click()
                                await asyncio.sleep(2)
                                carousel_count += 1
                            else:
                                break
                    except:
                        pass

                    # Move to next post
                    if i < num_posts - 1:
                        try:
                            next_post = page.locator('a:has-text("Next")').first
                            await next_post.click()
                            await asyncio.sleep(3)
                        except:
                            print("No more posts")
                            break

                # Download all captured media
                print("\n" + "="*60)
                print(f"📥 Starting downloads... ({len(self.media_urls)} media items)")
                print("="*60 + "\n")

                for media_type, url in self.media_urls:
                    self.download_media(media_type, url)

                print(f"\n✅ Complete! Downloaded {len(self.downloaded_urls)} files to '{self.download_folder}'")

            except Exception as e:
                print(f"Error: {str(e)}")
            finally:
                await browser.close()


async def main():
    # Configuration
    USERNAME = "your_username"  # Replace with your Instagram username
    PASSWORD = "your_password"  # Replace with your Instagram password
    PROFILE_URL = "https://www.instagram.com/natgeo/"  # Profile to download from
    NUM_POSTS = 5  # Number of posts to download

    # Create downloader and run
    downloader = InstagramMediaDownloader(USERNAME, PASSWORD)
    await downloader.browse_and_download(PROFILE_URL, NUM_POSTS)


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║   Instagram Media Downloader - Network Monitoring       ║
    ║   Automates the browser inspection method you described ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    asyncio.run(main())
