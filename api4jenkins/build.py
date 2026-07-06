# encoding: utf-8

import asyncio
import re
import time
import urllib.parse
from typing import Any, Dict, Iterator, AsyncIterator, Optional, List
from httpx import Response

from .artifact import Artifact, async_save_response_to, save_response_to
from .input import PendingInputAction
from .item import AsyncItem, Item
from .mix import (ActionsMixIn, AsyncActionsMixIn, AsyncDeletionMixIn,
                  AsyncDescriptionMixIn, AsyncRawJsonMixIn, DeletionMixIn,
                  DescriptionMixIn, RawJsonMixIn)
from .report import (AsyncCoverageReport, AsyncCoverageResult,
                     AsyncCoverageTrends, AsyncTestReport, CoverageReport,
                     CoverageResult, CoverageTrends, TestReport)


class Step(RawJsonMixIn, Item):

    def __init__(self, jenkins: Any, raw: Dict[str, Any]) -> None:
        url = _make_full_url(jenkins.url, raw['_links']['self']['href'])
        super().__init__(jenkins, url)
        self.raw = raw
        self.raw['_class'] = 'Step'

    def get_log(self) -> Optional[Dict[str, Any]]:
        log_link = self.raw.get('_links', {}).get('log')
        if not log_link:
            return None
        url = _make_full_url(self.jenkins.url, log_link['href'])
        return self._request('GET', url).json()


class Stage(RawJsonMixIn, Item):

    def __init__(self, jenkins: Any, raw: Dict[str, Any]) -> None:
        url = _make_full_url(jenkins.url, raw['_links']['self']['href'])
        super().__init__(jenkins, url)
        self.raw = raw
        self.raw['_class'] = 'Stage'

    def iter(self) -> Iterator[Step]:
        for step in self.raw.get('stageFlowNodes', []):
            yield Step(self.jenkins, step)

    def __iter__(self) -> Iterator[Step]:
        yield from self.iter()


class AsyncStep(AsyncRawJsonMixIn, AsyncItem):

    def __init__(self, jenkins: Any, raw: Dict[str, Any]) -> None:
        url = _make_full_url(jenkins.url, raw['_links']['self']['href'])
        super().__init__(jenkins, url)
        self.raw = raw
        self.raw['_class'] = 'AsyncStep'

    async def get_log(self) -> Optional[Dict[str, Any]]:
        log_link = self.raw.get('_links', {}).get('log')
        if not log_link:
            return None
        url = _make_full_url(self.jenkins.url, log_link['href'])
        resp = await self._request('GET', url)
        return resp.json()


class AsyncStage(AsyncRawJsonMixIn, AsyncItem):

    def __init__(self, jenkins: Any, raw: Dict[str, Any]) -> None:
        url = _make_full_url(jenkins.url, raw['_links']['self']['href'])
        super().__init__(jenkins, url)
        self.raw = raw
        self.raw['_class'] = 'AsyncStage'

    async def aiter(self) -> AsyncIterator[AsyncStep]:
        for step in self.raw.get('stageFlowNodes', []):
            yield AsyncStep(self.jenkins, step)

    async def __aiter__(self) -> AsyncIterator[AsyncStep]:
        async for step in self.aiter():
            yield step


def _make_full_url(base_url: str, href: str) -> str:
    '''Convert a HAL href (which may be absolute) to a full URL.'''
    base_url = base_url.rstrip('/')
    parsed = urllib.parse.urlparse(base_url)
    return f"{parsed.scheme}://{parsed.netloc}{href}"


class Build(Item, DescriptionMixIn, DeletionMixIn, ActionsMixIn):

    def console_text(self) -> Iterator[str]:
        with self.handle_stream('GET', 'consoleText') as resp:
            yield from resp.iter_lines()

    def progressive_output(self, html: bool = False) -> Iterator[str]:
        url = 'logText/progressiveHtml' if html else 'logText/progressiveText'
        start = 0
        while True:
            resp = self.handle_req('GET', url, params={'start': start})
            time.sleep(1)
            if start == resp.headers.get('X-Text-Size'):
                continue
            yield from resp.iter_lines()
            if not resp.headers.get('X-More-Data'):
                break
            start = resp.headers['X-Text-Size']

    def stop(self) -> Response:
        return self.handle_req('POST', 'stop')

    def term(self) -> Response:
        return self.handle_req('POST', 'term')

    def kill(self) -> Response:
        return self.handle_req('POST', 'kill')

    def get_next_build(self) -> Optional['Build']:
        if item := self.api_json(tree='nextBuild[url]')['nextBuild']:
            return self.__class__(self.jenkins, item['url'])
        return None

    def get_previous_build(self) -> Optional['Build']:
        if item := self.api_json(tree='previousBuild[url]')['previousBuild']:
            return self.__class__(self.jenkins, item['url'])
        return None

    @property
    def project(self) -> Any:
        job_name = self.jenkins._url2name(re.sub(r'\w+[/]?$', '', self.url))
        return self.jenkins.get_job(job_name)

    def get_test_report(self) -> Optional[TestReport]:
        tr = TestReport(self.jenkins, f'{self.url}testReport/')
        return tr if tr.exists() else None

    def get_coverage_report(self) -> Optional[CoverageReport]:
        '''Access coverage report generated by `JaCoCo <https://plugins.jenkins.io/jacoco/>`_'''
        cr = CoverageReport(self.jenkins, f'{self.url}jacoco/')
        return cr if cr.exists() else None

    def get_coverage_result(self) -> Optional[CoverageResult]:
        '''Access coverage result generated by `Code Coverage API <https://plugins.jenkins.io/code-coverage-api/>`_'''
        cr = CoverageResult(self.jenkins, f'{self.url}coverage/result/')
        return cr if cr.exists() else None

    def get_coverage_trends(self) -> Optional[CoverageTrends]:
        ct = CoverageTrends(self.jenkins, f'{self.url}coverage/trend/')
        return ct if ct.exists() else None


class WorkflowRun(Build):

    def get_pending_input(self) -> Optional[PendingInputAction]:
        '''get current pending input step'''
        data = self.handle_req('GET', 'wfapi/describe').json()
        if not data['_links'].get('pendingInputActions'):
            return None
        action = self.handle_req('GET', 'wfapi/pendingInputActions').json()[0]
        action["abortUrl"] = action["abortUrl"][action["abortUrl"].index(
            "/job/"):]
        return PendingInputAction(self.jenkins, action)

    @property
    def artifacts(self) -> List[Artifact]:
        artifacts = self.handle_req('GET', 'wfapi/artifacts').json()
        return [Artifact(self.jenkins, art) for art in artifacts]

    def iter(self) -> Iterator[Stage]:
        '''iterate pipeline stages'''
        data = self.handle_req('GET', 'wfapi/describe').json()
        for stage in data.get('stages', []):
            yield Stage(self.jenkins, stage)

    def save_artifacts(self, filename: str = 'archive.zip') -> None:
        with self.handle_stream('GET', 'artifact/*zip*/archive.zip') as resp:
            save_response_to(resp, filename)


class FreeStyleBuild(Build):
    pass  # Inherits all type annotations from Build


class MatrixBuild(Build):
    pass  # Inherits all type annotations from Build

# async class


class AsyncBuild(AsyncItem, AsyncDescriptionMixIn, AsyncDeletionMixIn, AsyncActionsMixIn):

    async def console_text(self) -> AsyncIterator[str]:
        async with self.handle_stream('GET', 'consoleText') as resp:
            async for line in resp.aiter_lines():
                yield line

    async def progressive_output(self, html: bool = False) -> AsyncIterator[str]:
        url = 'logText/progressiveHtml' if html else 'logText/progressiveText'
        start = 0
        while True:
            resp = await self.handle_req('GET', url, params={'start': start})
            await asyncio.sleep(1)
            if start == resp.headers.get('X-Text-Size'):
                continue
            async for line in resp.aiter_lines():
                yield line
            if not resp.headers.get('X-More-Data'):
                break
            start = resp.headers['X-Text-Size']

    async def stop(self) -> Response:
        return await self.handle_req('POST', 'stop')

    async def term(self) -> Response:
        return await self.handle_req('POST', 'term')

    async def kill(self) -> Response:
        return await self.handle_req('POST', 'kill')

    async def get_next_build(self) -> Optional['AsyncBuild']:
        data = await self.api_json(tree='nextBuild[url]')
        return self.__class__(self.jenkins, data['nextBuild']['url']) if data['nextBuild'] else None

    async def get_previous_build(self) -> Optional['AsyncBuild']:
        data = await self.api_json(tree='previousBuild[url]')
        return self.__class__(self.jenkins, data['previousBuild']['url']) if data['previousBuild'] else None

    @property
    async def project(self) -> Any:
        job_name = self.jenkins._url2name(re.sub(r'\w+[/]?$', '', self.url))
        return await self.jenkins.get_job(job_name)

    async def get_test_report(self) -> Optional[AsyncTestReport]:
        tr = AsyncTestReport(self.jenkins, f'{self.url}testReport/')
        return tr if await tr.exists() else None

    async def get_coverage_report(self) -> Optional[AsyncCoverageReport]:
        '''Access coverage report generated by `JaCoCo <https://plugins.jenkins.io/jacoco/>`_'''
        cr = AsyncCoverageReport(self.jenkins, f'{self.url}jacoco/')
        return cr if await cr.exists() else None

    async def get_coverage_result(self) -> Optional[AsyncCoverageResult]:
        '''Access coverage result generated by `Code Coverage API <https://plugins.jenkins.io/code-coverage-api/>`_'''
        cr = AsyncCoverageResult(self.jenkins, f'{self.url}coverage/result/')
        return cr if await cr.exists() else None

    async def get_coverage_trends(self) -> Optional[AsyncCoverageTrends]:
        ct = AsyncCoverageTrends(self.jenkins, f'{self.url}coverage/trend/')
        return ct if await ct.exists() else None


class AsyncWorkflowRun(AsyncBuild):

    async def get_pending_input(self) -> Optional[PendingInputAction]:
        '''get current pending input step'''
        data = (await self.handle_req('GET', 'wfapi/describe')).json()
        if not data['_links'].get('pendingInputActions'):
            return None
        action = (await self.handle_req('GET', 'wfapi/pendingInputActions')).json()[0]
        action["abortUrl"] = action["abortUrl"][action["abortUrl"].index(
            "/job/"):]
        return PendingInputAction(self.jenkins, action)

    @property
    async def artifacts(self) -> List[Artifact]:
        artifacts = (await self.handle_req('GET', 'wfapi/artifacts')).json()
        return [Artifact(self.jenkins, art) for art in artifacts]

    async def aiter(self) -> AsyncIterator[AsyncStage]:
        '''async iterate pipeline stages'''
        data = (await self.handle_req('GET', 'wfapi/describe')).json()
        for stage in data.get('stages', []):
            yield AsyncStage(self.jenkins, stage)

    async def save_artifacts(self, filename: str = 'archive.zip') -> None:
        async with self.handle_stream('GET', 'artifact/*zip*/archive.zip') as resp:
            await async_save_response_to(resp, filename)


class AsyncFreeStyleBuild(AsyncBuild):
    pass  # Inherits all type annotations from AsyncBuild


class AsyncMatrixBuild(AsyncBuild):
    pass  # Inherits all type annotations from AsyncBuild
