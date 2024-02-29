from metagpt.actions import Action
from metagpt.config2  import config
import aiohttp
from bs4 import BeautifulSoup
from typing import Any

class CrawlOSSTrending(Action):
    """Crawl trending repositories from GitHub."""
    name :str =  "CrawlOSSTrending"

    async def run(self, url: str = "https://github.com/trending"):
        async with aiohttp.ClientSession() as client:
            async with client.get(url) as response:
                response.raise_for_status()
                html = await response.text()
 
        soup = BeautifulSoup(html, 'html.parser')
    
        repositories = []
    
        for article in soup.select('article.Box-row'):
            repo_info = {}
            
            repo_info['name'] = article.select_one('h2 a').text.strip().replace("\n", "").replace(" ", "")
            repo_info['url'] = "https://github.com" + article.select_one('h2 a')['href'].strip()
    
            # Description
            description_element = article.select_one('p')
            repo_info['description'] = description_element.text.strip() if description_element else None
    
            # Language
            language_element = article.select_one('span[itemprop="programmingLanguage"]')
            repo_info['language'] = language_element.text.strip() if language_element else None
    
            # Stars and Forks
            stars_element = article.select('a.Link--muted')[0]
            forks_element = article.select('a.Link--muted')[1]
            repo_info['stars'] = stars_element.text.strip()
            repo_info['forks'] = forks_element.text.strip()
    
            # Today's Stars
            today_stars_element = article.select_one('span.d-inline-block.float-sm-right')
            repo_info['today_stars'] = today_stars_element.text.strip() if today_stars_element else None
    
            repositories.append(repo_info)
    
        return repositories
    
class CrawHuggingPaper(Action):
    """Crawl papers from Hugging Face's model hub. As I am in China, I use a mirror site to avoid the GFW."""
    name :str= "CrawHuggingPaper"
    
    async def run(self, url: str = "https://hf-mirror.com/papers"):
        async with aiohttp.ClientSession() as client:
            async with client.get(url) as response:
                response.raise_for_status()
                html = await response.text()
 
        soup = BeautifulSoup(html, 'html.parser')
    
        papers = []
    
        for article in soup.select('div.acticle'):
            paper_info = {}
            
            paper_info['title'] = article.select_one('h3').text.strip()
            paper_info['url'] = "https://hf-mirror.com" + article.select_one('a')['href'].strip()

            # 获取url中的内容
            async with client.get(paper_info['url']) as response:
                response.raise_for_status()
                paper_html = await response.text()
                paper_soup = BeautifulSoup(paper_html, 'html.parser')
                # Abstract
                paper_info['abstract'] = paper_soup.select_one('p.abstract').text.strip()
                # Authors
                # 先定位到div.relative块
                authors_div = paper_soup.select('div.relative')
                # 在authors_div查找类别为underline和writespace-nowrap的a标签和button标签
                paper_info['authors'] = []
                for author in authors_div:
                    authors_element = author.select('.underline.writespace-nowrap')
                    authors_group = [author.text.strip() for author in authors_element]
                    paper_info['authors'].append(authors_group)
                # 重整authors
                paper_info['authors'] = [item for sublist in paper_info['authors'] for item in sublist]
    
            papers.append(paper_info)
    
        return papers
    
TRENDING_ANALYSIS_PROMPT = """# Requirements
You are a GitHub Trending Analyst, aiming to provide users with insightful and personalized recommendations based on the latest
GitHub Trends. Based on the context, fill in the following missing information, generate engaging and informative titles, 
ensuring users discover repositories aligned with their interests.

# The title about Today's GitHub Trending
## Today's Trends: Uncover the Hottest GitHub Projects Today! Explore the trending programming languages and discover key domains capturing developers' attention. From ** to **, witness the top projects like never before.
## The Trends Categories: Dive into Today's GitHub Trending Domains! Explore featured projects in domains such as ** and **. Get a quick overview of each project, including programming languages, stars, and more.
## Highlights of the List: Spotlight noteworthy projects on GitHub Trending, including new tools, innovative projects, and rapidly gaining popularity, focusing on delivering distinctive and attention-grabbing content for users.
---
# Format Example

```
# [Title]

## Today's Trends
Today, ** and ** continue to dominate as the most popular programming languages. Key areas of interest include **, ** and **.
The top popular projects are Project1 and Project2.

## The Trends Categories
1. Generative AI
    - [Project1](https://github/xx/project1): [detail of the project, such as star total and today, language, ...]
    - [Project2](https://github/xx/project2): ...
...

## Highlights of the List
1. [Project1](https://github/xx/project1): [provide specific reasons why this project is recommended].
...
```

---
# Github Trending
{results}
"""

HUGGINGFACE_ANALYSIS_PROMPT = """# Requirements
You are a Hugging Face Papers Analyst, aiming to provide users with insightful and personalized recommendations based on the latest
Hugging Face Papers. Based on the context, fill in the following missing information, generate engaging and informative titles,
ensuring users discover papers aligned with their interests.

# The title about Today's huggingface Papers
---
# Format Example

```
# [Title]

## Today's Great Papers
Today, ** and ** ...

## The Papers Brief
1. [Paper1](https://huggingface.co/xx/paper1): [detail of the paper, such as authors, abstract, ...]
2. [Paper2](https://huggingface.co/xx/paper2): ...
...

## Highlights of the List
1. [Paper1](https://huggingface.co/xx/paper1): [provide specific reasons why this paper is recommended].
...

---
# Huggingface Papers
{results}
"""

class Summary(Action):
    """Summarize the papers. Make a future look for the papers."""
    name :str= "Summary"

    async def run(self, action: str, result: Any) -> str:
        if action == "CrawlOSSTrending":
            return self._generate_report(result, TRENDING_ANALYSIS_PROMPT)
        elif action == "CrawHuggingPaper":
            return self._generate_report(result, HUGGINGFACE_ANALYSIS_PROMPT)
    
    @staticmethod
    async def _generate_report(self, result: Any, prompt: str) -> str:
        """use llm to generate report from the given infomation."""
        full_prompt = prompt.format(results=result)
        # ask llm to generate report
        return await self._aask(full_prompt)
        