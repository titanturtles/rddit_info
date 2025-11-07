"""
LLM processor for stock symbol extraction and sentiment analysis
Uses Deepseek or other LLM providers
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import httpx
from config_loader import get_config

logger = logging.getLogger(__name__)


class LLMProcessor:
    """Handles LLM operations for stock symbol extraction and sentiment analysis"""

    # Common stock symbols (can be expanded)
    COMMON_SYMBOLS = {
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'JNJ', 'V',
        'WMT', 'PG', 'MA', 'INTC', 'CSCO', 'AMD', 'NFLX', 'PYPL', 'CRM', 'ADBE',
        'GME', 'AMC', 'PLTR', 'BB', 'COIN', 'RIOT', 'MARA', 'SENS', 'PROG', 'CLOV',
        'NIO', 'SOFI', 'F', 'GM', 'LCID', 'RIVN', 'SPY', 'QQQ', 'IWM', 'DIA',
        'BRK.B', 'BRK.A', 'GOOG', 'COST', 'AMZN', 'TSLA', 'UBER', 'LYFT', 'SQ',
        'DISH', 'NKLA', 'WISH', 'CLNE', 'TLRY', 'SNDL', 'MSTR', 'CORZ'
    }

    FAKE_SYMBOLS = {
        'THE', 'AND', 'FOR', 'ARE', 'YOU', 'THIS', 'THAT', 'IS', 'WITH', 'ON', 'AT', 'BY',
        'FROM', 'OF', 'IN', 'TO', 'AS', 'IT', 'BE', 'AN', 'OR', 'IF', 'BUT', 'NOT', 'ALL',
        'I', 'S', 'A', 'P', 'CEO', 'CFO', 'IPO', 'ETF', 'SEC', 'FDA', 'IRS', 'U', 'AI'
    }

    def __init__(self):
        """Initialize LLM processor"""
        self.config = get_config()
        self.llm_config = self.config.get_section('llm')
        self.api_key = self.llm_config.get('api_key')
        self.base_url = self.llm_config.get('base_url', 'https://api.deepseek.com/v1')
        self.model = self.llm_config.get('model', 'deepseek-chat')
        self.temperature = self.llm_config.get('temperature', 0.3)
        self.max_tokens = self.llm_config.get('max_tokens', 500)
        self.timeout = self.llm_config.get('timeout', 30)

        # Initialize database connection
        try:
            from database import MongoDBConnection
            self.db = MongoDBConnection()
        except Exception as e:
            logger.warning(f"Could not initialize database connection: {e}")
            self.db = None

    def _call_llm(self, prompt: str) -> Optional[str]:
        """
        Call the LLM API and store raw response in database

        Args:
            prompt: Input prompt

        Returns:
            LLM response or None if error
        """
        try:
            logger.info("=" * 80)
            logger.info(f"[DEEPSEEK REQUEST] Calling {self.model}")
            logger.info(f"[ENDPOINT] {self.base_url}/chat/completions")
            logger.info(f"[PARAMS] temperature={self.temperature}, max_tokens={self.max_tokens}, timeout={self.timeout}s")
            logger.info(f"[PROMPT] {prompt[:100]}..." if len(prompt) > 100 else f"[PROMPT] {prompt}")
            logger.info(f"[PROMPT_LENGTH] {len(prompt)} characters")
            logger.info("=" * 80)

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': 'You are a financial analyst assistant.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': self.temperature,
                'max_tokens': self.max_tokens
            }

            logger.debug(f"[DEEPSEEK] Request payload: {payload}")
            logger.debug(f"[DEEPSEEK] Headers (masked): Authorization=Bearer ***{self.api_key[-10:]}, Content-Type=application/json")

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f'{self.base_url}/chat/completions',
                    headers=headers,
                    json=payload
                )

                logger.debug(f"[DEEPSEEK] Response status: {response.status_code}")
                logger.debug(f"[DEEPSEEK] Response headers: {dict(response.headers)}")

                if response.status_code == 200:
                    result = response.json()
                    response_text = result['choices'][0]['message']['content']

                    logger.info("=" * 80)
                    logger.info(f"[DEEPSEEK RESPONSE] Status: 200 OK")
                    logger.info(f"[MODEL] {result.get('model', 'unknown')}")
                    logger.info(f"[TOKENS_USED] Prompt: {result['usage']['prompt_tokens']}, Completion: {result['usage']['completion_tokens']}, Total: {result['usage']['total_tokens']}")
                    logger.info(f"[FINISH_REASON] {result['choices'][0].get('finish_reason', 'unknown')}")
                    logger.info(f"[RESPONSE] {response_text[:150]}..." if len(response_text) > 150 else f"[RESPONSE] {response_text}")
                    logger.info(f"[RESPONSE_LENGTH] {len(response_text)} characters")
                    logger.info("=" * 80)

                    # Store raw LLM response to database
                    self._store_llm_response(prompt, response_text, result, status='success')

                    return response_text
                else:
                    error_msg = f"Status {response.status_code}: {response.text}"
                    logger.error("=" * 80)
                    logger.error(f"[DEEPSEEK ERROR] API request failed")
                    logger.error(f"[STATUS] {response.status_code}")
                    logger.error(f"[ERROR] {error_msg}")
                    logger.error(f"[RESPONSE_TEXT] {response.text[:200]}")
                    logger.error("=" * 80)

                    # Store error response to database
                    self._store_llm_response(prompt, None, response.text, status='error', error=error_msg)

                    return None

        except Exception as e:
            import traceback
            logger.error("=" * 80)
            logger.error(f"[DEEPSEEK EXCEPTION] Error calling LLM")
            logger.error(f"[EXCEPTION_TYPE] {type(e).__name__}")
            logger.error(f"[EXCEPTION_MSG] {str(e)}")
            logger.error(f"[TRACEBACK]\n{traceback.format_exc()}")
            logger.error("=" * 80)

            # Store exception to database
            self._store_llm_response(prompt, None, None, status='exception', error=str(e))

            return None

    def _store_llm_response(self, prompt: str, response: Optional[str], raw_response: Any,
                           status: str = 'unknown', error: Optional[str] = None) -> None:
        """
        Store raw LLM request and response to database

        Args:
            prompt: Original prompt sent to LLM
            response: Parsed response text
            raw_response: Full raw response from API
            status: Status of the call (success, error, exception)
            error: Error message if applicable
        """
        try:
            if self.db is None:
                logger.debug("Database not available, skipping LLM response storage")
                return

            # Ensure llm_responses collection exists
            if 'llm_responses' not in self.db.collections:
                self.db.collections['llm_responses'] = self.db.db['llm_responses']

            llm_response_col = self.db.collections.get('llm_responses')
            if llm_response_col is None:
                logger.warning("Could not access llm_responses collection")
                return

            # Create document
            doc = {
                'timestamp': datetime.utcnow(),
                'model': self.model,
                'provider': self.llm_config.get('provider', 'unknown'),
                'prompt': prompt[:1000],  # Store first 1000 chars of prompt
                'response': response,
                'raw_response': str(raw_response)[:5000] if raw_response else None,  # Store raw response
                'status': status,
                'error': error,
                'prompt_length': len(prompt),
                'response_length': len(response) if response else 0,
                'temperature': self.temperature,
                'max_tokens': self.max_tokens,
            }

            # Insert into database
            result = llm_response_col.insert_one(doc)
            logger.debug(f"Stored LLM response: {result.inserted_id}")

        except Exception as e:
            logger.warning(f"Could not store LLM response to database: {e}")

    def extract_stock_symbols(self, text: str) -> List[str]:
        """
        Extract stock symbols from text using pattern matching and LLM

        Args:
            text: Input text

        Returns:
            List of extracted stock symbols
        """
        symbols = set()

        # First, use pattern matching for common symbols
        for symbol in self.COMMON_SYMBOLS:
            # Match whole words only
            pattern = r'\b' + re.escape(symbol) + r'\b'
            if re.search(pattern, text.upper()):
                symbols.add(symbol)

        # Also look for ticker symbols (all caps followed by space or punctuation)
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        potential_tickers = re.findall(ticker_pattern, text)

        for ticker in potential_tickers:
            if ticker in self.COMMON_SYMBOLS:
                symbols.add(ticker)
            # Add common market related terms that look like symbols
            elif len(ticker) <= 5 and ticker not in FAKE_SYMBOLS:
                symbols.add(ticker)

        # Try LLM extraction for complex cases
        if not symbols and len(text) > 20:
            try:
                prompt = f"""Extract all stock ticker symbols from the following text. Return only the symbols as a comma-separated list.

Text: {text[:500]}

Symbols:"""
                response = self._call_llm(prompt)
                if response:
                    extracted = [s.strip().upper() for s in response.split(',')]
                    symbols.update([s for s in extracted if len(s) <= 5 and s.isalpha()])
            except Exception as e:
                logger.warning(f"LLM symbol extraction failed: {e}")

        return list(symbols)

    def analyze_sentiment(self, text: str, stock_symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze sentiment of text regarding stock symbols

        Args:
            text: Input text
            stock_symbols: Optional list of stock symbols mentioned

        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            symbols_str = ', '.join(stock_symbols) if stock_symbols else 'general market'

            prompt = f"""Analyze the sentiment of the following text regarding {symbols_str}.
Provide sentiment as one of: BULLISH, NEUTRAL, or BEARISH.
Also provide a sentiment score from -1 (very bearish) to +1 (very bullish).
Explain the reasoning in 1-2 sentences.

Text: {text[:1000]}

Response format:
SENTIMENT: [BULLISH/NEUTRAL/BEARISH]
SCORE: [number between -1 and 1]
REASONING: [explanation]"""

            response = self._call_llm(prompt)

            if response:
                result = self._parse_sentiment_response(response)
                return result
            else:
                # Fallback to simple keyword-based analysis
                return self._simple_sentiment_analysis(text)

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return self._simple_sentiment_analysis(text)

    def _parse_sentiment_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM sentiment response"""
        result = {
            'sentiment': 'NEUTRAL',
            'score': 0.0,
            'reasoning': ''
        }

        try:
            lines = response.strip().split('\n')
            for line in lines:
                if 'SENTIMENT:' in line:
                    sentiment = line.split(':', 1)[1].strip().upper()
                    result['sentiment'] = sentiment if sentiment in ['BULLISH', 'BEARISH', 'NEUTRAL'] else 'NEUTRAL'

                elif 'SCORE:' in line:
                    try:
                        score = float(line.split(':', 1)[1].strip())
                        result['score'] = max(-1.0, min(1.0, score))
                    except ValueError:
                        pass

                elif 'REASONING:' in line:
                    result['reasoning'] = line.split(':', 1)[1].strip()

        except Exception as e:
            logger.warning(f"Error parsing sentiment response: {e}")

        return result

    def _simple_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """
        Simple keyword-based sentiment analysis fallback

        Args:
            text: Input text

        Returns:
            Sentiment analysis result
        """
        text_lower = text.lower()

        bullish_keywords = [
            'buy', 'bullish', 'moon', 'rocket', 'diamond hands', 'to the moon',
            'undervalued', 'strong', 'growth', 'profit', 'earnings beat', 'upgrade',
            'good news', 'soaring', 'surge', 'pump', 'squeeze', 'boom'
        ]

        bearish_keywords = [
            'sell', 'bearish', 'crash', 'dump', 'dump it', 'paper hands', 'rekt',
            'overvalued', 'weak', 'decline', 'loss', 'miss', 'downgrade', 'bad news',
            'plunge', 'tank', 'collapse', 'bankrupt'
        ]

        bullish_count = sum(1 for keyword in bullish_keywords if keyword in text_lower)
        bearish_count = sum(1 for keyword in bearish_keywords if keyword in text_lower)

        if bullish_count > bearish_count:
            sentiment = 'BULLISH'
            score = min(1.0, bullish_count / 5)
        elif bearish_count > bullish_count:
            sentiment = 'BEARISH'
            score = max(-1.0, -bearish_count / 5)
        else:
            sentiment = 'NEUTRAL'
            score = 0.0

        return {
            'sentiment': sentiment,
            'score': score,
            'reasoning': f'Keyword-based analysis: {bullish_count} bullish, {bearish_count} bearish keywords'
        }

    def batch_analyze_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple posts for stock symbols and sentiment

        Args:
            posts: List of post dictionaries

        Returns:
            List of posts with analysis results
        """
        analyzed_posts = []

        for i, post in enumerate(posts):
            try:
                text = f"{post.get('title', '')} {post.get('content', '')}"

                # Extract stock symbols
                symbols = self.extract_stock_symbols(text)

                # Analyze sentiment
                sentiments = {}
                if symbols:
                    for symbol in symbols:
                        sentiment = self.analyze_sentiment(text, [symbol])
                        sentiments[symbol] = sentiment
                else:
                    # General sentiment
                    general_sentiment = self.analyze_sentiment(text)
                    sentiments['GENERAL'] = general_sentiment

                post['stock_mentions'] = symbols
                post['sentiments'] = sentiments

                analyzed_posts.append(post)

                if (i + 1) % 10 == 0:
                    logger.info(f"Analyzed {i + 1}/{len(posts)} posts")

            except Exception as e:
                logger.error(f"Error analyzing post: {e}")
                continue

        logger.info(f"Completed analysis of {len(analyzed_posts)} posts")
        return analyzed_posts

    def batch_analyze_comments(self, comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple comments for stock symbols and sentiment

        Args:
            comments: List of comment dictionaries

        Returns:
            List of comments with analysis results
        """
        analyzed_comments = []

        for comment in comments:
            try:
                text = comment.get('content', '')

                if not text or len(text) < 5:
                    continue

                # Extract stock symbols
                symbols = self.extract_stock_symbols(text)

                # Analyze sentiment
                sentiments = {}
                if symbols:
                    for symbol in symbols:
                        sentiment = self.analyze_sentiment(text, [symbol])
                        sentiments[symbol] = sentiment

                if symbols:
                    comment['stock_mentions'] = symbols
                    comment['sentiments'] = sentiments
                    analyzed_comments.append(comment)

            except Exception as e:
                logger.warning(f"Error analyzing comment: {e}")
                continue

        logger.info(f"Analyzed {len(analyzed_comments)} comments with stock mentions")
        return analyzed_comments
