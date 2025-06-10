import asyncio
from typing import Optional
from semantic_kernel.functions import kernel_function
from playwright.async_api import async_playwright
from playwright_mcp import MCP

class BrowserNavigation:
    """Class for browser navigation using Playwright with MCP support."""
    def __init__(self) -> None:
        self.mcp = None
        self.browser = None
        self.context = None
        self.page = None

    async def _ensure_connection(self):
        if not self.mcp:
            self.mcp = MCP()
            await self.mcp.connect()
            self.browser = await self.mcp.playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()

    @kernel_function(description="Navigate to a URL using Playwright browser.")
    async def navigate(self, url: str) -> str:
        """Navigate to a specified URL and return the page content.
        Args:
            url (str): The URL to navigate to.
        Returns:
            str: The content of the page after navigation.
        """
        try:
            await self._ensure_connection()
            await self.page.goto(url)
            content = await self.page.content()
            return content
        except Exception as e:
            return f"Error navigating to {url}: {e}"
        
    @kernel_function(description="Extract text content from current page.")
    async def extract_text(self) -> str:
        """Extract text content from the current page.
        Returns:
            str: The text content of the page, or None if extraction fails.
        """
        try:
            await self._ensure_connection()
            text_content = await self.page.evaluate("document.body.innerText")
            return text_content
        except Exception as e:
            return f"Error extracting text: {e}"
        
    async def cleanup(self):
        """Clean up browser resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.mcp:
            await self.mcp.dispose()