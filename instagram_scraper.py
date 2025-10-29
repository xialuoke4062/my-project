#!/usr/bin/env python3
"""
Modern Instagram Post Scraper
Downloads all media from Instagram posts with stats tracking
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import requests
from pathlib import Path
import json
import hashlib
from datetime import datetime


class InstagramScraper:
    def __init__(self, download_dir="instagram_downloads"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.driver = None
        self.downloaded_hashes = set()
        self.stats_log = []

    def setup_driver(self):
        """Setup Chrome with mobile emulation and DevTools"""
        options = webdriver.ChromeOptions()
        options.add_argument('--auto-open-devtools-for-tabs')
        options.add_experimental_option('mobileEmulation', {
            'deviceName': 'iPhone 12 Pro'
        })
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        self.driver = webdriver.Chrome(options=options)
        print("✓ Browser opened with DevTools enabled")

    def extract_post_stats(self):
        """Extract likes, comments, and paid partnership status"""
        likes = "0"
        comments = "0"
        is_paid = False

        try:
            # Get likes
            like_spans = self.driver.find_elements(
                By.CSS_SELECTOR,
                'span.x1ypdohk.x1s688f.x2fvf9.xe9ewy2[role="button"]'
            )
            if like_spans:
                likes = like_spans[0].text
        except:
            pass

        try:
            # Get comments
            comment_spans = self.driver.find_elements(
                By.CSS_SELECTOR,
                'span.xdj266r.x14z9mp.xat24cr.x1lziwak.xexx8yu.xyri2b.x18d9i69.x1c1uobl.x1hl2dhg.x16tdsg8.x1vvkbs'
            )
            for span in comment_spans:
                text = span.text
                if text.isdigit():
                    comments = text
                    break
        except:
            pass

        try:
            # Check for paid partnership
            if "Paid partnership with " in self.driver.page_source:
                is_paid = True
        except:
            pass

        return likes, comments, is_paid

    def click_through_carousel(self):
        """Click next button until no more items"""
        click_count = 0
        while True:
            try:
                next_btn = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((
                        By.CSS_SELECTOR,
                        'button[aria-label="Next"], button[aria-label="next"]'
                    ))
                )
                next_btn.click()
                click_count += 1
                time.sleep(0.5)
            except (TimeoutException, NoSuchElementException):
                break

        return click_count

    def extract_media_urls(self):
        """Extract media URLs from network logs"""
        logs = self.driver.get_log('performance')
        media_urls = set()

        for log in logs:
            try:
                message = json.loads(log['message'])['message']
                if message['method'] == 'Network.responseReceived':
                    response = message['params']['response']
                    url = response['url']
                    mime_type = response.get('mimeType', '')

                    if 'image/' in mime_type or 'video/' in mime_type:
                        if 'cdninstagram.com' in url:
                            media_urls.add(url)
            except:
                continue

        return media_urls

    def download_media(self, media_urls, post_dir):
        """Download media files, skipping duplicates and bad URLs"""
        success_count = 0

        for idx, url in enumerate(media_urls, 1):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                # Check for duplicates by content hash
                content_hash = hashlib.md5(response.content).hexdigest()
                if content_hash in self.downloaded_hashes:
                    print(f"  Skipped {idx}/{len(media_urls)}: Duplicate")
                    continue

                self.downloaded_hashes.add(content_hash)

                ext = '.jpg' if 'image/' in response.headers.get('content-type', '') else '.mp4'
                success_count += 1
                filename = post_dir / f"item_{success_count}{ext}"

                filename.write_bytes(response.content)
                print(f"  Downloaded {success_count}: {filename.name}")
            except Exception as e:
                print(f"  Skipped {idx}/{len(media_urls)}: {str(e)[:40]}")

        return success_count

    def scrape_post(self, post_url):
        """Scrape a single Instagram post"""
        print(f"\n{'='*60}")
        print(f"Scraping: {post_url}")
        print('='*60)

        # Navigate and refresh
        self.driver.get(post_url)
        time.sleep(3)
        self.driver.refresh()
        time.sleep(2)

        # Extract stats
        likes, comments, is_paid = self.extract_post_stats()
        print(f"Stats: Likes={likes}, Comments={comments}, Paid={is_paid}")

        # Click through carousel
        click_count = self.click_through_carousel()
        if click_count > 0:
            print(f"Clicked next {click_count} times")

        # Extract media URLs
        media_urls = self.extract_media_urls()
        print(f"Found {len(media_urls)} potential media items")

        # Create directory for this post
        post_id = post_url.rstrip('/').split('/')[-1]
        post_dir = self.download_dir / post_id
        post_dir.mkdir(exist_ok=True)

        # Download media
        success_count = self.download_media(media_urls, post_dir)

        # Log stats
        self.stats_log.append({
            'timestamp': datetime.now().isoformat(),
            'post_url': post_url,
            'post_id': post_id,
            'likes': likes,
            'comments': comments,
            'paid_partnership': is_paid,
            'media_downloaded': success_count
        })

        print(f"✓ Downloaded {success_count} unique items to '{post_dir}'")

    def scrape_user_posts(self, username, max_posts=None):
        """Scrape all posts from a user's profile"""
        profile_url = f"https://www.instagram.com/{username}/"
        print(f"\n{'='*60}")
        print(f"Scraping user profile: {username}")
        print('='*60)

        self.driver.get(profile_url)
        time.sleep(3)

        # Find all post links
        try:
            post_links = []
            articles = self.driver.find_elements(By.CSS_SELECTOR, 'article a[href*="/p/"]')

            for article in articles:
                href = article.get_attribute('href')
                if href and '/p/' in href:
                    post_links.append(href)

            # Remove duplicates while preserving order
            post_links = list(dict.fromkeys(post_links))

            if max_posts:
                post_links = post_links[:max_posts]

            print(f"Found {len(post_links)} posts")

            # Scrape each post
            for i, post_url in enumerate(post_links, 1):
                print(f"\nPost {i}/{len(post_links)}")
                self.scrape_post(post_url)
                time.sleep(2)

        except Exception as e:
            print(f"Error scraping user posts: {e}")

    def save_stats_log(self):
        """Save stats to JSON file"""
        stats_file = self.download_dir / "scrape_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats_log, f, indent=2)
        print(f"\n✓ Stats saved to {stats_file}")

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("✓ Browser closed")


def main():
    print("Instagram Post Scraper")
    print("="*60)

    # Get user input
    choice = input("Scrape (1) Single post or (2) User profile? [1/2]: ").strip()

    scraper = InstagramScraper()
    scraper.setup_driver()

    try:
        if choice == "1":
            post_url = input("Enter post URL: ").strip()
            scraper.scrape_post(post_url)

        elif choice == "2":
            username = input("Enter username: ").strip()
            max_posts_input = input("Max posts to scrape (press Enter for all): ").strip()
            max_posts = int(max_posts_input) if max_posts_input else None
            scraper.scrape_user_posts(username, max_posts)

        else:
            print("Invalid choice")

        # Save stats
        scraper.save_stats_log()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        scraper.close()

    print("\n✓ Done!")


if __name__ == "__main__":
    main()
