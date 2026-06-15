from __future__ import annotations

import argparse
import asyncio
import hashlib
import html as html_lib
import json
import logging
import math
import random
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence
from urllib.parse import parse_qs, parse_qsl, unquote, urlencode, urljoin, urlsplit, urlunsplit

import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag

try:
    import torch
    from transformers import AutoModel, AutoTokenizer
except ImportError:  # pragma: no cover - optional runtime dependency
    torch = None
    AutoModel = None
    AutoTokenizer = None


LOGGER = logging.getLogger("vov_parallel_scraper")

USER_AGENTS: tuple[str, ...] = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Edge/125.0.0.0 Safari/537.36",
)

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "vi,en-US;q=0.8,en;q=0.6",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

# Adjust these section seeds when VOV changes category slugs or when you want to
# scrape a deeper news slice. The VI defaults avoid sections that redirect to
# the homepage and focus on VOVWorld branches that more often produce Khmer
# counterparts.
DEFAULT_VI_SECTION_URLS: tuple[str, ...] = (
    "https://vovworld.vn/vi-VN/chinh-tri",
    "https://vovworld.vn/vi-VN/kinh-te",
    "https://vovworld.vn/vi-VN/tin-moi-cap-nhat",
)

DEFAULT_KM_SECTION_URLS: tuple[str, ...] = (
    "https://vov.vn/km-KH/%E1%9E%9C%E1%9E%94%E1%9F%92%E1%9E%94%E1%9E%92%E1%9E%98%E1%9F%8D%E1%9E%9C%E1%9F%80%E1%9E%8F%E1%9E%8E%E1%9E%B6%E1%9E%98/43977.vov",
    "https://vov.vn/km-KH/%E1%9E%80%E1%9E%B6%E1%9E%9A%E1%9E%9A%E1%9E%80%E1%9E%83%E1%9E%BE%E1%9E%89%E1%9E%9C%E1%9F%80%E1%9E%8F%E1%9E%8E%E1%9E%B6%E1%9E%98/43477.vov",
    "https://vov.vn/km-KH/%E1%9E%96%E1%9F%90%E1%9E%8F%E1%9F%8D%E1%9E%98%E1%9E%B6%E1%9E%93/43509.vov",
)

BODY_SELECTORS: tuple[str, ...] = (
    "div.content.mt-10.body-detail.fs-15.lh-24",
    "div.article-body",
    "div.row.article-content",
    "div.text-long",
    "div.detail__content",
    "div.detail-content",
    "div[itemprop='articleBody']",
    "article[itemprop='articleBody']",
    "article.detail div.content",
    "article.detail",
    "main article",
    "article",
)

PRIMARY_HEADLINE_SELECTORS: tuple[str, ...] = (
    "h1",
    "article h1",
    "main h1",
)

SECONDARY_HEADLINE_SELECTORS: tuple[str, ...] = (
    "main .fs-30.mb-0",
    "main .fs-30",
    "main [class*='title']",
    ".article-title",
    ".detail-title",
)

DROP_CLASS_KEYWORDS: tuple[str, ...] = (
    "share",
    "social",
    "related",
    "tag",
    "ads",
    "advert",
    "banner",
    "breadcrumb",
    "comment",
    "toolbar",
    "audio",
    "video",
    "podcast",
)

TRACKING_QUERY_KEYS = {
    "fbclid",
    "gclid",
    "output",
    "resize",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}

TITLE_SUFFIX_RE = re.compile(
    r"\s*[-|]\s*(?:VOV(?:\.VN|WORLD)?|B[aA]o\s+.*?Ti[eê]ng\s+n[oó]i\s+Vi[eệ]t\s+Nam).*$",
    re.IGNORECASE,
)
ARTICLE_URL_RE = re.compile(r"(?:post)?\d+\.vov\d*$", re.IGNORECASE)
NUMERIC_SECTION_RE = re.compile(r"^\d+\.vov\d*$", re.IGNORECASE)
NON_ARTICLE_PATH_RE = re.compile(r"/(?:amp|audio|author|podcast|search|tag|video)/", re.IGNORECASE)
ISO_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
SLASH_DATE_RE = re.compile(r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})")
IMAGE_PATH_RE = re.compile(r"\.(?:bmp|gif|jpe?g|png|svg|webp)$", re.IGNORECASE)
GENERIC_PAGE_TITLE_RE = re.compile(r"^(?:VOV(?:\.VN| World)?|B[aA]o\s+.*?Ti[eê]ng\s+n[oó]i\s+Vi[eệ]t\s+Nam)$")
ARTICLE_ID_RE = re.compile(r"-(\d+)\.vov\d*$", re.IGNORECASE)
ANCHOR_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9.+/-]{2,}")

COMMON_ANCHOR_STOPWORDS = {
    "bao",
    "bai",
    "bnews",
    "campuchia",
    "content",
    "ha",
    "hanoi",
    "khmer",
    "kinh",
    "lam",
    "news",
    "nguyen",
    "page",
    "phat",
    "post",
    "quan",
    "quoc",
    "radio",
    "tieng",
    "thanh",
    "viet",
    "viet",
    "vietnnaam",
    "vietnam",
    "voice",
    "vov",
    "vovworld",
    "world",
}

SEMANTIC_BATCH_SIZE = 16
SEMANTIC_TEXT_LIMIT = 1800

DECORATIVE_IMAGE_BASENAMES = {
    "facebook.svg",
    "google_news.png",
}

DECORATIVE_IMAGE_PATH_KEYWORDS: tuple[str, ...] = (
    "/_next/static/",
    "/themes/custom/",
    "/icons/",
    "/logo",
)


@dataclass(slots=True)
class ArticleRecord:
    id: str
    url: str
    language: str
    title: str
    published_date: str
    images: list[str]
    image_filenames: list[str]
    content: str


@dataclass(slots=True)
class ArticleAlignmentFeatures:
    media_uuids: list[str]
    source_image_paths: list[str]


@dataclass(slots=True)
class ScrapedArticle:
    record: ArticleRecord
    alignment: ArticleAlignmentFeatures


@dataclass(slots=True)
class AlignmentCandidate:
    vi_id: str
    km_id: str
    final_score: float
    semantic_score: float
    anchor_score: float
    media_score: float
    date_diff: int
    matching_images: list[str]
    shared_anchors: list[str]


@dataclass(slots=True)
class ScraperConfig:
    vi_sections: list[str]
    km_sections: list[str]
    output_dir: Path
    log_level: str = "INFO"
    max_list_pages: int = 2
    max_articles_per_section: int = 25
    request_timeout: float = 20.0
    retries: int = 3
    max_connections: int = 12
    concurrency: int = 6
    date_window_days: int = 3
    semantic_model_name: str = "intfloat/multilingual-e5-small"
    min_alignment_score: float = 0.7
    min_alignment_margin: float = 0.04


def configure_logging(level_name: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level_name.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    cleaned = html_lib.unescape(value)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def unique_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def stable_hash(value: str, prefix: str = "") -> str:
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()
    return f"{prefix}{digest[:16]}"


def strip_diacritics(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.replace("đ", "d").replace("Đ", "D"))
    return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize_anchor_text(text: str) -> str:
    ascii_text = strip_diacritics(text).lower().replace("-", " ").replace("/", " ")
    ascii_text = re.sub(r"[^a-z0-9\s.+]", " ", ascii_text)
    return clean_text(ascii_text)


def extract_article_suffix_id(url: str) -> str:
    match = ARTICLE_ID_RE.search(url)
    return match.group(1) if match else ""


def extract_slug_text(url: str) -> str:
    path = unquote(urlsplit(url).path).strip("/")
    if not path:
        return ""

    slug = path.rsplit("/", 1)[-1]
    slug = re.sub(r"\.vov\d*$", "", slug, flags=re.IGNORECASE)
    slug = re.sub(r"-\d+$", "", slug)
    return slug.replace("-", " ")


def build_anchor_tokens(article: ScrapedArticle) -> set[str]:
    anchor_source = " ".join(
        filter(
            None,
            [
                article.record.title,
                extract_slug_text(article.record.url),
                extract_article_suffix_id(article.record.url),
                article.record.content[:1200],
            ],
        )
    )
    normalized = normalize_anchor_text(anchor_source)
    tokens: set[str] = set()
    for token in ANCHOR_TOKEN_RE.findall(normalized):
        if token.isdigit():
            if len(token) >= 2:
                tokens.add(token)
            continue

        if len(token) < 4 or token in COMMON_ANCHOR_STOPWORDS:
            continue

        if token.startswith("http"):
            continue

        tokens.add(token)

    return tokens


def build_anchor_weights(anchor_map: dict[str, set[str]]) -> dict[str, float]:
    document_frequency: Counter[str] = Counter()
    for tokens in anchor_map.values():
        for token in tokens:
            document_frequency[token] += 1

    total_documents = max(1, len(anchor_map))
    return {
        token: math.log1p(total_documents / frequency)
        for token, frequency in document_frequency.items()
    }


def semantic_text_for_article(article: ScrapedArticle, model_name: str) -> str:
    text = clean_text(" ".join(filter(None, [article.record.title, article.record.content[:SEMANTIC_TEXT_LIMIT]])))
    if not text:
        return ""
    if "e5" in model_name.lower():
        return f"passage: {text}"
    return text


def mean_pool_embeddings(token_embeddings: Any, attention_mask: Any) -> Any:
    expanded_mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    summed = (token_embeddings * expanded_mask).sum(dim=1)
    counts = expanded_mask.sum(dim=1).clamp(min=1e-9)
    return summed / counts


def build_semantic_embeddings(
    articles: Sequence[ScrapedArticle],
    model_name: str,
) -> dict[str, tuple[float, ...]]:
    if not articles:
        return {}

    if AutoTokenizer is None or AutoModel is None or torch is None:
        LOGGER.warning("Semantic alignment disabled because transformers/torch is unavailable")
        return {}

    try:
        LOGGER.info("Loading semantic alignment model %s", model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        model.eval()
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Semantic alignment disabled because %s could not be loaded: %s", model_name, exc)
        return {}

    article_ids = [article.record.id for article in articles]
    texts = [semantic_text_for_article(article, model_name) for article in articles]
    embeddings: dict[str, tuple[float, ...]] = {}

    with torch.no_grad():
        for start in range(0, len(texts), SEMANTIC_BATCH_SIZE):
            batch_ids = article_ids[start : start + SEMANTIC_BATCH_SIZE]
            batch_texts = texts[start : start + SEMANTIC_BATCH_SIZE]
            encoded = tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            outputs = model(**encoded)
            pooled = mean_pool_embeddings(outputs.last_hidden_state, encoded["attention_mask"])
            normalized = pooled / pooled.norm(dim=1, keepdim=True).clamp(min=1e-12)
            for article_id, vector in zip(batch_ids, normalized.tolist()):
                embeddings[article_id] = tuple(float(value) for value in vector)

    return embeddings


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    return sum(lhs * rhs for lhs, rhs in zip(left, right))


def content_length_similarity(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    return min(len(left), len(right)) / max(len(left), len(right))


def normalize_url(url: str, *, drop_query: bool = False) -> str:
    parsed = urlsplit(url.strip())
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc.lower()
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/" and path.endswith("/") and parsed.path.endswith(".vov"):
        path = path.rstrip("/")

    query = ""
    if not drop_query and parsed.query:
        filtered_query = [
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if key.lower() not in TRACKING_QUERY_KEYS
        ]
        query = urlencode(filtered_query, doseq=True)

    return urlunsplit((scheme, netloc, path, query, ""))


def normalize_article_url(url: str) -> str:
    normalized = normalize_url(url, drop_query=True)
    if normalized.endswith("/") and normalized != "/":
        normalized = normalized.rstrip("/")
    return normalized


def is_supported_language_url(url: str, language: str) -> bool:
    parsed = urlsplit(url)
    netloc = parsed.netloc.lower()
    path = parsed.path

    if language == "km":
        return netloc == "vov.vn" and path.startswith("/km-KH/")
    if language == "vi":
        return netloc == "vovworld.vn" and path.startswith("/vi-VN/")
    return False


def is_candidate_article_url(url: str, language: str) -> bool:
    parsed = urlsplit(url)
    if not is_supported_language_url(url, language):
        return False

    path = parsed.path
    if NON_ARTICLE_PATH_RE.search(path) or not re.search(r"\.vov\d*$", path, re.IGNORECASE):
        return False

    last_segment = path.rsplit("/", 1)[-1]
    if NUMERIC_SECTION_RE.fullmatch(last_segment):
        return False

    return bool(ARTICLE_URL_RE.search(last_segment))


def section_prefix(url: str) -> str:
    parts = [part for part in urlsplit(url).path.split("/") if part]
    if parts and NUMERIC_SECTION_RE.fullmatch(parts[-1]):
        parts = parts[:-1]
    if not parts:
        return "/"
    return "/" + "/".join(parts) + "/"


def group_key(url: str, language: str) -> str:
    parts = [part for part in urlsplit(url).path.split("/") if part]
    if not parts:
        return "/"
    if language == "km":
        return "/" + "/".join(parts[:2])
    return "/" + "/".join(parts[:2])


def iter_json_ld_objects(soup: BeautifulSoup) -> Iterator[dict[str, Any]]:
    for script_tag in soup.find_all("script", attrs={"type": re.compile("ld\\+json", re.IGNORECASE)}):
        raw_text = script_tag.string or script_tag.get_text(strip=True)
        if not raw_text:
            continue
        try:
            loaded = json.loads(raw_text)
        except json.JSONDecodeError:
            continue
        yield from flatten_json_ld(loaded)


def flatten_json_ld(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, list):
        for item in value:
            yield from flatten_json_ld(item)
        return
    if not isinstance(value, dict):
        return

    yield value
    graph = value.get("@graph")
    if isinstance(graph, list):
        for item in graph:
            yield from flatten_json_ld(item)


def clean_title(raw_title: str) -> str:
    title = clean_text(raw_title)
    title = TITLE_SUFFIX_RE.sub("", title)
    return clean_text(title)


def is_likely_headline_text(text: str) -> bool:
    cleaned = clean_text(text)
    if not cleaned or len(cleaned) < 12 or len(cleaned) > 280:
        return False
    if normalize_date(cleaned):
        return False
    if cleaned.lower().startswith("[vovworld]"):
        return False
    return not GENERIC_PAGE_TITLE_RE.fullmatch(cleaned)


def normalize_date(raw_value: str | None) -> str:
    if not raw_value:
        return ""

    text = clean_text(raw_value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text).date().isoformat()
    except ValueError:
        pass

    iso_match = ISO_DATE_RE.search(text)
    if iso_match:
        try:
            return datetime.strptime(iso_match.group(1), "%Y-%m-%d").date().isoformat()
        except ValueError:
            pass

    slash_match = SLASH_DATE_RE.search(text)
    if slash_match:
        candidate = slash_match.group(1).replace("-", "/")
        try:
            return datetime.strptime(candidate, "%d/%m/%Y").date().isoformat()
        except ValueError:
            pass

    return ""


def parse_iso_date(raw_value: str) -> date | None:
    if not raw_value:
        return None
    try:
        return datetime.strptime(raw_value, "%Y-%m-%d").date()
    except ValueError:
        return None


def select_best_body_container(soup: BeautifulSoup) -> Tag | None:
    best_node: Tag | None = None
    best_score = -1
    seen_signatures: set[int] = set()

    for selector in BODY_SELECTORS:
        for candidate in soup.select(selector):
            candidate_id = id(candidate)
            if candidate_id in seen_signatures:
                continue
            seen_signatures.add(candidate_id)

            text_length = len(clean_text(candidate.get_text(" ", strip=True)))
            paragraph_count = len(candidate.find_all("p"))
            image_count = len(candidate.find_all("img"))
            score = text_length + (paragraph_count * 200) + (image_count * 25)

            if text_length < 150 and paragraph_count < 2:
                continue

            if score > best_score:
                best_score = score
                best_node = candidate

    return best_node


def prune_container(node: Tag) -> BeautifulSoup:
    cloned = BeautifulSoup(str(node), "html.parser")
    for selector in ("script", "style", "noscript", "iframe", "svg", "button", "form", "nav", "aside"):
        for element in cloned.select(selector):
            element.decompose()

    for element in list(cloned.find_all(True)):
        if getattr(element, "attrs", None) is None:
            continue

        raw_classes = element.get("class") or []
        if isinstance(raw_classes, str):
            class_values = [raw_classes]
        else:
            class_values = [class_name for class_name in raw_classes if isinstance(class_name, str)]

        element_classes = " ".join(class_values)
        element_marker = f"{element.get('id', '')} {element_classes}".lower()
        if any(keyword in element_marker for keyword in DROP_CLASS_KEYWORDS):
            element.decompose()

    return cloned


def iter_media_embed_nodes(node: Tag) -> Iterator[Tag]:
    seen: set[int] = set()
    for candidate in node.select("[data-entity-uuid]"):
        candidate_id = id(candidate)
        if candidate_id in seen:
            continue
        seen.add(candidate_id)
        yield candidate


def extract_content(node: Tag | None, json_ld_objects: Sequence[dict[str, Any]]) -> str:
    if node is not None:
        pruned = prune_container(node)
        blocks: list[str] = []
        for candidate in pruned.find_all(["p", "h2", "h3", "li"]):
            block_text = clean_text(candidate.get_text(" ", strip=True))
            if not block_text:
                continue
            if block_text.lower().startswith("tag:"):
                continue
            blocks.append(block_text)

        if not blocks:
            raw_lines = [clean_text(line) for line in pruned.get_text("\n", strip=True).splitlines()]
            blocks = [line for line in raw_lines if len(line) >= 40]

        return "\n".join(unique_preserve_order(blocks))

    for obj in json_ld_objects:
        article_body = obj.get("articleBody")
        if isinstance(article_body, str):
            return clean_text(article_body)

    return ""


def normalize_image_url(raw_url: str | None, page_url: str) -> str | None:
    if not raw_url:
        return None
    cleaned = raw_url.strip()
    if not cleaned or cleaned.startswith("data:"):
        return None

    absolute_url = normalize_url(urljoin(page_url, cleaned), drop_query=False)
    parsed = urlsplit(absolute_url)

    if parsed.path.endswith("/_next/image") or parsed.path.endswith("/_next/image/"):
        nested = parse_qs(parsed.query).get("url", [None])[0]
        if nested:
            absolute_url = normalize_url(urljoin(page_url, unquote(nested)), drop_query=True)
            parsed = urlsplit(absolute_url)

    if IMAGE_PATH_RE.search(parsed.path):
        return absolute_url

    lowered_path = parsed.path.lower()
    if any(marker in lowered_path for marker in ("/sites/default/files/", "/public/", "/uploaded/", "/media/")):
        return absolute_url

    return None


def is_decorative_image_url(image_url: str) -> bool:
    parsed = urlsplit(image_url)
    lowered_path = parsed.path.lower()
    basename = Path(unquote(parsed.path)).name.lower()
    if basename in DECORATIVE_IMAGE_BASENAMES:
        return True
    return any(keyword in lowered_path for keyword in DECORATIVE_IMAGE_PATH_KEYWORDS)


def collect_media_image_candidates(media_node: Tag) -> list[str | None]:
    candidates: list[str | None] = [
        media_node.get("data-large-src"),
        media_node.get("data-medium-src"),
        media_node.get("src"),
        media_node.get("data-src"),
    ]

    nested_image = media_node.find("img")
    if nested_image is not None:
        candidates.extend(
            [
                nested_image.get("src"),
                nested_image.get("data-src"),
                nested_image.get("data-original"),
                nested_image.get("data-lazy-src"),
            ]
        )

    return candidates


def extract_images(node: Tag | None, page_url: str, json_ld_objects: Sequence[dict[str, Any]]) -> list[str]:
    image_urls: list[str] = []

    if node is not None:
        for media_node in iter_media_embed_nodes(node):
            for candidate in collect_media_image_candidates(media_node):
                normalized = normalize_image_url(candidate, page_url)
                if normalized and not is_decorative_image_url(normalized):
                    image_urls.append(normalized)
                    break

        for image_tag in node.find_all("img"):
            marker = f"{image_tag.get('alt', '')} {' '.join(image_tag.get('class', []))}".lower()
            if any(keyword in marker for keyword in ("icon", "logo", "avatar", "share")):
                continue

            candidates = [
                image_tag.get("src"),
                image_tag.get("data-src"),
                image_tag.get("data-original"),
                image_tag.get("data-lazy-src"),
            ]

            srcset = image_tag.get("srcset") or image_tag.get("data-srcset")
            if srcset:
                first_source = srcset.split(",", 1)[0].strip().split(" ", 1)[0]
                candidates.append(first_source)

            for candidate in candidates:
                normalized = normalize_image_url(candidate, page_url)
                if normalized and not is_decorative_image_url(normalized):
                    image_urls.append(normalized)
                    break

    if image_urls:
        return unique_preserve_order(image_urls)

    for obj in json_ld_objects:
        image_field = obj.get("image")
        normalized_urls = coerce_json_ld_images(image_field, page_url)
        if normalized_urls:
            image_urls.extend(normalized_urls)

    return unique_preserve_order(image_urls)


def coerce_json_ld_images(value: Any, page_url: str) -> list[str]:
    raw_urls: list[str] = []
    if isinstance(value, str):
        raw_urls.append(value)
    elif isinstance(value, list):
        for item in value:
            raw_urls.extend(coerce_json_ld_images(item, page_url))
        return unique_preserve_order(raw_urls)
    elif isinstance(value, dict):
        if isinstance(value.get("url"), str):
            raw_urls.append(value["url"])
        if isinstance(value.get("contentUrl"), str):
            raw_urls.append(value["contentUrl"])

    normalized = [normalize_image_url(url, page_url) for url in raw_urls]
    return unique_preserve_order([url for url in normalized if url and not is_decorative_image_url(url)])


def extract_image_filenames(image_urls: Sequence[str]) -> list[str]:
    filenames: list[str] = []
    for image_url in image_urls:
        file_name = Path(unquote(urlsplit(image_url).path)).name.lower()
        if file_name:
            filenames.append(file_name)
    return unique_preserve_order(filenames)


def normalize_source_image_path(image_url: str) -> str | None:
    parsed = urlsplit(image_url)
    if not parsed.path:
        return None

    parts = [part.lower() for part in unquote(parsed.path).split("/") if part]
    normalized_parts: list[str] = []
    skip_next = False
    for part in parts:
        if skip_next:
            skip_next = False
            continue
        if part == "styles":
            skip_next = True
            continue
        normalized_parts.append(part)

    if not normalized_parts:
        return None

    return "/" + "/".join(normalized_parts)


def extract_alignment_features(node: Tag | None, image_urls: Sequence[str]) -> ArticleAlignmentFeatures:
    if node is None:
        return ArticleAlignmentFeatures(media_uuids=[], source_image_paths=[])

    media_uuids: list[str] = []
    for media_node in iter_media_embed_nodes(node):
        media_uuid = clean_text(media_node.get("data-entity-uuid"))
        if media_uuid:
            media_uuids.append(media_uuid.lower())

    source_paths = unique_preserve_order(
        path
        for path in (normalize_source_image_path(image_url) for image_url in image_urls)
        if path
    )
    return ArticleAlignmentFeatures(
        media_uuids=unique_preserve_order(media_uuids),
        source_image_paths=source_paths,
    )


def iter_body_adjacent_title_candidates(body_node: Tag | None) -> Iterator[str]:
    if body_node is None:
        return

    current: Tag | None = body_node
    for _ in range(4):
        if current is None:
            break
        for sibling in reversed(list(current.previous_siblings)):
            if not isinstance(sibling, Tag):
                continue
            direct_text = clean_text(sibling.get_text(" ", strip=True))
            if is_likely_headline_text(direct_text):
                yield direct_text
            for nested in sibling.find_all(["div", "h1", "h2", "h3", "p"], recursive=True):
                nested_text = clean_text(nested.get_text(" ", strip=True))
                if is_likely_headline_text(nested_text):
                    yield nested_text
        parent = current.parent
        current = parent if isinstance(parent, Tag) else None


def extract_title(
    soup: BeautifulSoup,
    body_node: Tag | None,
    json_ld_objects: Sequence[dict[str, Any]],
) -> str:
    for selector in PRIMARY_HEADLINE_SELECTORS:
        for title_tag in soup.select(selector):
            title = clean_title(title_tag.get_text(" ", strip=True))
            if is_likely_headline_text(title):
                return title

    for candidate in iter_body_adjacent_title_candidates(body_node):
        title = clean_title(candidate)
        if is_likely_headline_text(title):
            return title

    for selector in SECONDARY_HEADLINE_SELECTORS:
        for title_tag in soup.select(selector):
            title = clean_title(title_tag.get_text(" ", strip=True))
            if is_likely_headline_text(title):
                return title

    for obj in json_ld_objects:
        for key in ("headline", "name"):
            if isinstance(obj.get(key), str):
                title = clean_title(obj[key])
                if is_likely_headline_text(title):
                    return title

    for meta in soup.find_all("meta"):
        meta_key = " ".join(
            filter(None, [meta.get("property"), meta.get("name"), meta.get("itemprop")])
        ).lower()
        if not any(keyword in meta_key for keyword in ("title", "headline", "og:title", "twitter:title")):
            continue
        content = clean_title(meta.get("content", ""))
        if is_likely_headline_text(content):
            return content

    if soup.title and soup.title.string:
        title = clean_title(soup.title.string)
        if is_likely_headline_text(title):
            return title
    return ""


def extract_published_date(soup: BeautifulSoup, json_ld_objects: Sequence[dict[str, Any]]) -> str:
    candidates: list[str] = []

    for obj in json_ld_objects:
        for key in ("datePublished", "dateCreated", "uploadDate", "dateModified"):
            if isinstance(obj.get(key), str):
                candidates.append(obj[key])

    for meta in soup.find_all("meta"):
        meta_key = " ".join(
            filter(None, [meta.get("property"), meta.get("name"), meta.get("itemprop")])
        ).lower()
        if any(keyword in meta_key for keyword in ("published", "publish", "created", "date", "time", "updated")):
            content = meta.get("content")
            if content:
                candidates.append(content)

    for time_tag in soup.find_all(["time", "span", "div", "p"]):
        marker = f"{time_tag.get('id', '')} {' '.join(time_tag.get('class', []))}".lower()
        if any(keyword in marker for keyword in ("date", "time", "publish", "created", "clock")):
            datetime_attr = time_tag.get("datetime")
            if datetime_attr:
                candidates.append(datetime_attr)
            text = clean_text(time_tag.get_text(" ", strip=True))
            if text:
                candidates.append(text)

    heading = soup.find("h1")
    if heading is not None:
        candidates.append(clean_text(heading.parent.get_text(" ", strip=True)))
        sibling = heading.find_next_sibling()
        sibling_steps = 0
        while sibling is not None and sibling_steps < 4:
            candidates.append(clean_text(sibling.get_text(" ", strip=True)))
            sibling = sibling.find_next_sibling()
            sibling_steps += 1

    candidates.append(clean_text(soup.get_text(" ", strip=True)[:2500]))

    for candidate in candidates:
        normalized = normalize_date(candidate)
        if normalized:
            return normalized

    return ""


def extract_metadata(page_url: str, language: str, html: str) -> ScrapedArticle | None:
    soup = BeautifulSoup(html, "html.parser")
    json_ld_objects = list(iter_json_ld_objects(soup))
    body_node = select_best_body_container(soup)
    title = extract_title(soup, body_node, json_ld_objects)
    content = extract_content(body_node, json_ld_objects)

    if not title or len(content) < 80:
        return None

    published_date = extract_published_date(soup, json_ld_objects)
    images = extract_images(body_node, page_url, json_ld_objects)
    image_filenames = extract_image_filenames(images)
    alignment = extract_alignment_features(body_node, images)

    return ScrapedArticle(
        record=ArticleRecord(
            id=stable_hash(page_url, prefix=f"{language}_"),
            url=page_url,
            language=language,
            title=title,
            published_date=published_date,
            images=images,
            image_filenames=image_filenames,
            content=content,
        ),
        alignment=alignment,
    )


def extract_article_links(
    soup: BeautifulSoup,
    page_url: str,
    section_url: str,
    language: str,
) -> list[str]:
    candidate_urls: list[str] = []
    for anchor in soup.select("a[href]"):
        raw_href = anchor.get("href", "")
        if not raw_href or raw_href.startswith(("javascript:", "mailto:", "tel:")):
            continue

        absolute_url = normalize_article_url(urljoin(page_url, raw_href))
        if is_candidate_article_url(absolute_url, language):
            candidate_urls.append(absolute_url)

    candidate_urls = unique_preserve_order(candidate_urls)
    if not candidate_urls:
        return []

    preferred_prefixes = {section_prefix(page_url), section_prefix(section_url)}
    filtered = [
        url
        for url in candidate_urls
        if any(urlsplit(url).path.startswith(prefix) for prefix in preferred_prefixes if prefix != "/")
    ]
    if filtered:
        return filtered

    key_counts = Counter(group_key(url, language) for url in candidate_urls)
    if key_counts:
        dominant_key, dominant_count = key_counts.most_common(1)[0]
        if dominant_count >= max(2, len(candidate_urls) // 3):
            return [url for url in candidate_urls if group_key(url, language) == dominant_key]

    return candidate_urls


def extract_pagination_links(
    soup: BeautifulSoup,
    page_url: str,
    section_url: str,
    language: str,
) -> list[str]:
    pagination_links: list[str] = []

    # VOV occasionally changes pagination markup. If the newsroom switches to a
    # new query or path pattern, update the checks below instead of changing the
    # article scraping logic.
    for anchor in soup.select("a[href]"):
        raw_href = anchor.get("href", "")
        if not raw_href or raw_href.startswith(("javascript:", "mailto:", "tel:")):
            continue

        absolute_url = normalize_url(urljoin(page_url, raw_href), drop_query=False)
        if not is_supported_language_url(absolute_url, language):
            continue
        parsed = urlsplit(absolute_url)
        if is_candidate_article_url(absolute_url, language):
            continue

        anchor_text = clean_text(anchor.get_text(" ", strip=True)).lower()
        anchor_markers = f"{' '.join(anchor.get('class', []))} {' '.join(anchor.get('rel', []))}".lower()

        looks_like_pagination = any(
            condition
            for condition in (
                "next" in anchor_text,
                "older" in anchor_text,
                "trang sau" in anchor_text,
                "tiep" in anchor_text,
                "pagination" in anchor_markers,
                "pager" in anchor_markers,
                bool(re.search(r"(?:page|trang)=\d+", parsed.query, re.IGNORECASE)),
                bool(re.search(r"/(?:page|trang)[/-]?\d+", parsed.path, re.IGNORECASE)),
            )
        )
        if looks_like_pagination:
            pagination_links.append(absolute_url)

    pagination_links = unique_preserve_order(pagination_links)
    preferred_prefixes = {section_prefix(page_url), section_prefix(section_url)}
    filtered = [
        url
        for url in pagination_links
        if any(urlsplit(url).path.startswith(prefix) for prefix in preferred_prefixes if prefix != "/")
    ]
    return filtered or pagination_links


class VOVParallelScraper:
    def __init__(self, config: ScraperConfig) -> None:
        self.config = config
        self.semaphore = asyncio.Semaphore(config.concurrency)
        self.client = httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(config.request_timeout),
            limits=httpx.Limits(
                max_connections=config.max_connections,
                max_keepalive_connections=config.max_connections,
            ),
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def fetch_html(self, url: str) -> tuple[str, str] | None:
        last_error: Exception | None = None
        request_url = normalize_url(url, drop_query=False)

        for attempt in range(1, self.config.retries + 1):
            await asyncio.sleep(random.uniform(0.05, 0.2))
            try:
                async with self.semaphore:
                    response = await self.client.get(
                        request_url,
                        headers={**DEFAULT_HEADERS, "User-Agent": random.choice(USER_AGENTS)},
                    )
                response.raise_for_status()
                return normalize_url(str(response.url), drop_query=False), response.text
            except httpx.HTTPStatusError as exc:
                last_error = exc
                status_code = exc.response.status_code
                if status_code not in {429, 500, 502, 503, 504}:
                    break
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                last_error = exc

            backoff_seconds = min(2.0 ** attempt, 8.0) + random.uniform(0.1, 0.4)
            LOGGER.warning("Retrying %s after attempt %s (%s)", request_url, attempt, last_error)
            await asyncio.sleep(backoff_seconds)

        LOGGER.error("Failed to fetch %s: %s", request_url, last_error)
        return None

    async def discover_article_urls(self, section_url: str, language: str) -> list[str]:
        queue: list[str] = [normalize_url(section_url, drop_query=False)]
        visited_pages: set[str] = set()
        collected_articles: list[str] = []

        while queue and len(visited_pages) < self.config.max_list_pages:
            page_url = queue.pop(0)
            normalized_page = normalize_url(page_url, drop_query=False)
            if normalized_page in visited_pages:
                continue
            visited_pages.add(normalized_page)

            fetched = await self.fetch_html(page_url)
            if fetched is None:
                continue

            final_page_url, html = fetched
            soup = BeautifulSoup(html, "html.parser")

            discovered_articles = extract_article_links(soup, final_page_url, section_url, language)
            for article_url in discovered_articles:
                if article_url in collected_articles:
                    continue
                collected_articles.append(article_url)
                if len(collected_articles) >= self.config.max_articles_per_section:
                    return collected_articles

            pagination_links = extract_pagination_links(soup, final_page_url, section_url, language)
            for pagination_url in pagination_links:
                normalized_pagination = normalize_url(pagination_url, drop_query=False)
                if normalized_pagination not in visited_pages and normalized_pagination not in queue:
                    queue.append(normalized_pagination)

        return collected_articles

    async def scrape_article(self, article_url: str, language: str) -> ScrapedArticle | None:
        fetched = await self.fetch_html(article_url)
        if fetched is None:
            return None
        final_url, html = fetched

        try:
            article = extract_metadata(normalize_article_url(final_url), language, html)
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Failed to parse %s: %s", article_url, exc)
            return None

        if article is None:
            LOGGER.warning("Skipped article with incomplete content: %s", article_url)
        return article

    async def scrape_language(self, language: str, section_urls: Sequence[str]) -> list[ScrapedArticle]:
        LOGGER.info("Discovering %s article URLs from %s sections", language, len(section_urls))
        section_tasks = [self.discover_article_urls(section_url, language) for section_url in section_urls]
        section_results = await asyncio.gather(*section_tasks)

        article_urls = unique_preserve_order(
            article_url for section_urls in section_results for article_url in section_urls
        )
        LOGGER.info("Discovered %s candidate %s articles", len(article_urls), language)

        scrape_tasks = [self.scrape_article(article_url, language) for article_url in article_urls]
        scraped = await asyncio.gather(*scrape_tasks)
        records = [article for article in scraped if article is not None]
        LOGGER.info("Parsed %s %s articles", len(records), language)
        return records


def slim_article(article: ArticleRecord) -> dict[str, Any]:
    return {
        "url": article.url,
        "title": article.title,
        "published_date": article.published_date,
        "images": article.images,
        "content": article.content,
    }


def build_match_key_map(article: ScrapedArticle) -> dict[str, str]:
    key_map: dict[str, str] = {}
    for file_name in article.record.image_filenames:
        key_map[f"filename:{file_name}"] = file_name
    for source_path in article.alignment.source_image_paths:
        key_map[f"path:{source_path}"] = source_path.rsplit("/", 1)[-1]
    for media_uuid in article.alignment.media_uuids:
        key_map[f"uuid:{media_uuid}"] = ""
    return key_map


def align_corpus(
    vi_articles: Sequence[ScrapedArticle],
    km_articles: Sequence[ScrapedArticle],
    date_window_days: int,
    semantic_model_name: str,
    min_alignment_score: float,
    min_alignment_margin: float,
) -> list[dict[str, Any]]:
    vi_by_id = {article.record.id: article for article in vi_articles}
    km_by_id = {article.record.id: article for article in km_articles}
    vi_key_maps = {article.record.id: build_match_key_map(article) for article in vi_articles}
    km_key_maps = {article.record.id: build_match_key_map(article) for article in km_articles}

    anchor_map = {
        article.record.id: build_anchor_tokens(article)
        for article in [*vi_articles, *km_articles]
    }
    anchor_weights = build_anchor_weights(anchor_map)
    embeddings = build_semantic_embeddings([*vi_articles, *km_articles], semantic_model_name)
    semantic_enabled = bool(embeddings)

    candidate_lists: dict[str, list[AlignmentCandidate]] = defaultdict(list)

    for km_article in km_articles:
        km_record = km_article.record
        km_id = km_record.id
        km_date = parse_iso_date(km_record.published_date)
        if km_date is None:
            continue

        km_key_map = km_key_maps[km_id]
        km_anchor_tokens = anchor_map.get(km_id, set())
        km_embedding = embeddings.get(km_id)

        for vi_article in vi_articles:
            vi_record = vi_article.record
            vi_id = vi_record.id
            vi_date = parse_iso_date(vi_record.published_date)
            if vi_date is None:
                continue

            date_diff = abs((vi_date - km_date).days)
            if date_diff > date_window_days:
                continue

            vi_key_map = vi_key_maps[vi_id]
            shared_keys = set(km_key_map) & set(vi_key_map)
            matching_images = sorted(
                {
                    km_key_map[key] or vi_key_map[key]
                    for key in shared_keys
                    if (km_key_map[key] or vi_key_map[key])
                }
            )
            media_weight = sum(
                4 if key.startswith("filename:") else 3 if key.startswith("path:") else 1
                for key in shared_keys
            )
            media_score = min(1.0, media_weight / 4.0)

            shared_anchors = sorted(
                km_anchor_tokens & anchor_map.get(vi_id, set()),
                key=lambda token: (-anchor_weights.get(token, 0.0), token),
            )
            anchor_weight = sum(anchor_weights.get(token, 0.0) for token in shared_anchors[:12])
            anchor_score = min(1.0, anchor_weight / 6.0)

            semantic_score = 0.0
            vi_embedding = embeddings.get(vi_id)
            if km_embedding is not None and vi_embedding is not None:
                semantic_score = cosine_similarity(vi_embedding, km_embedding)

            length_score = content_length_similarity(vi_record.content, km_record.content)
            if semantic_enabled:
                final_score = min(
                    1.0,
                    semantic_score + 0.08 * anchor_score + 0.05 * media_score + 0.02 * length_score,
                )
                if semantic_score < 0.52 and anchor_score < 0.2 and media_score == 0.0:
                    continue
            else:
                final_score = 0.75 * anchor_score + 0.2 * media_score + 0.05 * length_score
                if anchor_score < 0.72 and media_score == 0.0:
                    continue

            candidate_lists[km_id].append(
                AlignmentCandidate(
                    vi_id=vi_id,
                    km_id=km_id,
                    final_score=final_score,
                    semantic_score=semantic_score,
                    anchor_score=anchor_score,
                    media_score=media_score,
                    date_diff=date_diff,
                    matching_images=matching_images,
                    shared_anchors=shared_anchors[:12],
                )
            )

    accepted_candidates: list[tuple[float, AlignmentCandidate]] = []
    for km_id, candidates in candidate_lists.items():
        candidates.sort(
            key=lambda candidate: (
                candidate.final_score,
                candidate.semantic_score,
                candidate.anchor_score,
                candidate.media_score,
                -candidate.date_diff,
                candidate.vi_id,
            ),
            reverse=True,
        )
        best_candidate = candidates[0]
        second_score = candidates[1].final_score if len(candidates) > 1 else 0.0
        score_margin = best_candidate.final_score - second_score
        strong_support = (
            best_candidate.media_score >= 0.75
            or (
                best_candidate.anchor_score >= 0.45
                and best_candidate.date_diff <= 1
                and len(best_candidate.shared_anchors) >= 2
            )
        )
        if best_candidate.final_score < min_alignment_score:
            continue
        if best_candidate.date_diff > 1 and best_candidate.media_score == 0.0 and best_candidate.anchor_score < 0.65:
            continue
        if score_margin < min_alignment_margin and not strong_support:
            continue
        accepted_candidates.append((score_margin, best_candidate))

    accepted_candidates.sort(
        key=lambda item: (
            item[1].final_score,
            item[0],
            item[1].semantic_score,
            item[1].anchor_score,
            item[1].media_score,
            -item[1].date_diff,
            item[1].vi_id,
        ),
        reverse=True,
    )

    aligned_pairs: list[dict[str, Any]] = []
    used_vi_ids: set[str] = set()
    used_km_ids: set[str] = set()

    for score_margin, candidate in accepted_candidates:
        if candidate.vi_id in used_vi_ids or candidate.km_id in used_km_ids:
            continue

        vi_record = vi_by_id[candidate.vi_id].record
        km_record = km_by_id[candidate.km_id].record
        used_vi_ids.add(candidate.vi_id)
        used_km_ids.add(candidate.km_id)

        aligned_pairs.append(
            {
                "pair_id": stable_hash(f"{vi_record.url}|{km_record.url}", prefix="pair_"),
                "vi_article": slim_article(vi_record),
                "km_article": slim_article(km_record),
                "matching_images": candidate.matching_images,
                "alignment_score": round(candidate.final_score, 4),
                "semantic_score": round(candidate.semantic_score, 4) if semantic_enabled else None,
                "alignment_signals": {
                    "candidate_margin": round(score_margin, 4),
                    "date_diff_days": candidate.date_diff,
                    "media_score": round(candidate.media_score, 4),
                    "anchor_score": round(candidate.anchor_score, 4),
                    "shared_anchors": candidate.shared_anchors,
                },
            }
        )

    return aligned_pairs


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file_handle:
        json.dump(payload, file_handle, ensure_ascii=False, indent=2)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Scrape Vietnamese and Khmer VOV articles, then align likely parallel pairs "
            "using multilingual semantic similarity, anchor overlap, and publication dates."
        )
    )
    parser.add_argument(
        "--vi-section",
        dest="vi_sections",
        action="append",
        help="Vietnamese section URL to scrape. Repeat for multiple section seeds.",
    )
    parser.add_argument(
        "--km-section",
        dest="km_sections",
        action="append",
        help="Khmer section URL to scrape. Repeat for multiple section seeds.",
    )
    parser.add_argument(
        "--max-list-pages",
        type=int,
        default=2,
        help="Maximum listing or pagination pages to crawl per section seed.",
    )
    parser.add_argument(
        "--max-articles-per-section",
        type=int,
        default=25,
        help="Maximum article URLs collected per section before moving on.",
    )
    parser.add_argument(
        "--request-timeout",
        type=float,
        default=20.0,
        help="Per-request timeout in seconds.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Retry count for transient HTTP or timeout failures.",
    )
    parser.add_argument(
        "--max-connections",
        type=int,
        default=12,
        help="Maximum pooled HTTP connections.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=6,
        help="Maximum concurrent requests across listing and article fetches.",
    )
    parser.add_argument(
        "--date-window-days",
        type=int,
        default=3,
        help="Allowed date gap in days when aligning VI and KM articles.",
    )
    parser.add_argument(
        "--semantic-model",
        default="intfloat/multilingual-e5-small",
        help="Multilingual embedding model used to mine parallel VI-KM pairs.",
    )
    parser.add_argument(
        "--min-alignment-score",
        type=float,
        default=0.7,
        help="Minimum score for accepting a VI-KM article pair.",
    )
    parser.add_argument(
        "--min-alignment-margin",
        type=float,
        default=0.04,
        help="Minimum gap over the next-best candidate for the same KM article.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Folder that receives unaligned_articles.json and aligned_parallel_corpus.json.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )
    return parser


async def run_scraper(config: ScraperConfig) -> None:
    scraper = VOVParallelScraper(config)
    try:
        vi_articles, km_articles = await asyncio.gather(
            scraper.scrape_language("vi", config.vi_sections),
            scraper.scrape_language("km", config.km_sections),
        )
    finally:
        await scraper.close()

    unaligned_payload = {
        "vi": [asdict(article.record) for article in vi_articles],
        "km": [asdict(article.record) for article in km_articles],
    }
    aligned_payload = align_corpus(
        vi_articles,
        km_articles,
        config.date_window_days,
        config.semantic_model_name,
        config.min_alignment_score,
        config.min_alignment_margin,
    )

    unaligned_path = config.output_dir / "unaligned_articles.json"
    aligned_path = config.output_dir / "aligned_parallel_corpus.json"
    save_json(unaligned_path, unaligned_payload)
    save_json(aligned_path, aligned_payload)

    LOGGER.info("Saved %s VI and %s KM articles", len(vi_articles), len(km_articles))
    LOGGER.info("Saved %s aligned article pairs", len(aligned_payload))
    LOGGER.info("Wrote %s", unaligned_path)
    LOGGER.info("Wrote %s", aligned_path)


def parse_args() -> ScraperConfig:
    parser = build_argument_parser()
    args = parser.parse_args()

    vi_sections = args.vi_sections or list(DEFAULT_VI_SECTION_URLS)
    km_sections = args.km_sections or list(DEFAULT_KM_SECTION_URLS)

    return ScraperConfig(
        vi_sections=vi_sections,
        km_sections=km_sections,
        output_dir=args.output_dir,
        log_level=args.log_level,
        max_list_pages=args.max_list_pages,
        max_articles_per_section=args.max_articles_per_section,
        request_timeout=args.request_timeout,
        retries=args.retries,
        max_connections=args.max_connections,
        concurrency=args.concurrency,
        date_window_days=args.date_window_days,
        semantic_model_name=args.semantic_model,
        min_alignment_score=args.min_alignment_score,
        min_alignment_margin=args.min_alignment_margin,
    )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    config = parse_args()
    configure_logging(config.log_level)
    asyncio.run(run_scraper(config))


if __name__ == "__main__":
    main()