import datetime
import functools
import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Optional

import requests
import tqdm
from pydantic import BaseModel
from tqdm.contrib.concurrent import thread_map

from clonr.utils.formatting import bytes_to_human_readable


def sanitize_branch_name(branch: str | None = None) -> str:
    if branch is None or not branch:
        return "main"
    if not re.search(r"^[a-zA-Z0-9._-]+$", branch):
        raise ValueError(
            "Invalid branch name. Only alphanumeric characters, period, underscore and dash are allowed."
        )
    return branch


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class LFSResource(BaseModel):
    oid: str
    size: int
    pointerSize: int


class HFResource(BaseModel):
    type: str
    oid: str
    size: int
    path: str
    url: str
    lfs: Optional[LFSResource]


class HFDownloader:
    hf_base_url: str = "https://huggingface.co"

    def __init__(
        self,
        hf_user: str | None = None,
        hf_password: str | None = None,
        timeout: int = 10,
    ):
        self.hf_user = hf_user or os.environ.get("HF_USER")
        self.hf_password = hf_password or os.environ.get("HF_PASSWORD")
        self.timeout = timeout

    def _get_repo_url(self, model_name: str, branch: str | None = None):
        branch = sanitize_branch_name(branch)
        if model_name.endswith("/"):
            model_name = model_name[:-1]
        route = f"api/models/{model_name}/tree/{branch}"
        return os.path.join(self.hf_base_url, route)

    def _get_download_url(
        self, model_name, fname: str, branch: str | None = None
    ) -> str:
        branch = sanitize_branch_name(branch)
        return f"{self.hf_base_url}/{model_name}/resolve/{branch}/{fname}"

    def _gather_repo_resources(
        self, model_name: str, branch: str | None = None
    ) -> list[HFResource]:
        repo_url = self._get_repo_url(model_name, branch)
        with requests.Session() as sess:
            if self.hf_user and self.hf_password:
                sess.auth = (self.hf_user, self.hf_password)
            r = sess.get(repo_url, timeout=self.timeout)
            r.raise_for_status()
        resources = r.json()
        for i, r in enumerate(resources):
            fname = r["path"]
            resources[i]["url"] = self._get_download_url(model_name, fname, branch)
        return [HFResource(**r) for r in resources]

    def _download_resource(
        self,
        resource: HFResource,
        output_dir: str | Path,
        resume_download: bool,
        block_size: int = 1024,
    ):
        output_dir = Path(output_dir)
        url = resource.url
        filename = Path(url).name
        output_path = output_dir / filename
        with requests.Session() as sess:
            if self.hf_user and self.hf_password:
                sess.auth = (self.hf_user, self.hf_password)

            # if download exists and is already completed, do nothing.
            if output_path.exists() and resume_download:
                print(f"Resuming Download for: {filename}")
                r = sess.get(url, stream=True, timeout=10)
                r.raise_for_status()
                total_size = int(r.headers.get("content-length", 0))
                if output_path.stat().st_size >= total_size:
                    return
                headers: dict[str, str] = {
                    "Range": f"bytes={output_path.stat().st_size}-"
                }
                mode = "ab"
            else:
                headers: dict[str, str] = {}
                mode = "wb"

            r = sess.get(url, stream=True, headers=headers, timeout=10)
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            data_itr = r.iter_content(block_size)

            with open(output_path, mode) as f:
                with tqdm.tqdm(
                    total=total_size,
                    unit="iB",
                    unit_scale=True,
                    bar_format="{l_bar}{bar}| {n_fmt:6}/{total_fmt:6} {rate_fmt:6}",
                ) as pbar:
                    for data in data_itr:
                        pbar.update(len(data))
                        f.write(data)
            if resource.lfs:
                with open(output_path, mode="rb") as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                if not file_hash == resource.lfs.oid:
                    msg = f"{bcolors.FAIL}Checksum failed{bcolors.ENDC}"
                    msg += f"\nExpected: {resource.lfs.oid}\nReceived: {file_hash}"
                else:
                    msg = f"{bcolors.OKGREEN}Checksum passed{bcolors.ENDC}"
                print(f"Checking SHA256 of {Path(resource.url).name}: {msg}")

    def preview_download(
        self,
        model_name: str,
        branch: str | None = None,
        regex_filter: str | None = None,
    ) -> None:
        resources = self._gather_repo_resources(model_name=model_name, branch=branch)
        if not resources:
            raise ValueError("Failed to find resources")

        if regex_filter:
            resources = [r for r in resources if re.search(regex_filter, r.path)]
            if not resources:
                raise ValueError(
                    (
                        f"The requested repository {model_name} was found, but after "
                        f"filtering on {regex_filter} returned no results!"
                    )
                )

        total_gb = bytes_to_human_readable(sum(r.size for r in resources))

        print(f"Total data to download: {total_gb}")
        print("-" * 10)
        print("Files to download:")
        for resource in resources:
            size = bytes_to_human_readable(resource.size)
            print(f"{Path(resource.url).name + ':':<30} {size}")

    def download(
        self,
        model_name: str,
        output_dir: str | Path | None = None,
        branch: str | None = None,
        resume_download: bool = True,
        n_threads: int | None = None,
        regex_filter: str | None = None,
    ):
        output_dir = output_dir / model_name.split("/")[-1]
        output_dir = Path(output_dir)
        n_threads = n_threads or 8
        resources = self._gather_repo_resources(model_name=model_name, branch=branch)

        if not resources:
            raise ValueError(f"The requested repository {model_name} is empty!")

        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        if regex_filter:
            resources = [r for r in resources if re.search(regex_filter, r.path)]
            if not resources:
                raise ValueError(
                    (
                        f"The requested repository {model_name} was found, "
                        f"but after filtering on {regex_filter} returned no results!"
                    )
                )

        total_size = bytes_to_human_readable(sum(r.size for r in resources))

        metadata = {
            "url": os.path.join(self.hf_base_url, model_name),
            "branch": branch,
            "download_date": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "n_files": len(resources),
            "total_size": total_size,
            "checksums": [f"{r.url}: {r.lfs.oid}" for r in resources if r.lfs],
        }

        with open(output_dir / "hf-metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"Total data to download: {total_size}. Output dir: {output_dir}")
        print("-" * 10)
        print("Preparing to download:")
        for resource in resources:
            size = bytes_to_human_readable(resource.size)
            print(f"{Path(resource.url).name + ':':<30} {size}")

        dl_func = functools.partial(
            self._download_resource,
            output_dir=Path(output_dir),
            resume_download=resume_download,
        )

        start = time.time()
        thread_map(dl_func, resources, max_workers=n_threads, disable=True)
        print("-" * 10)
        time_str = time.strftime("%H:%M:%S", time.gmtime(time.time() - start))
        print(
            f"{bcolors.UNDERLINE}Summary{bcolors.ENDC}: Time: {bcolors.BOLD}{time_str}{bcolors.ENDC}. Size: {bcolors.BOLD}{total_size}{bcolors.ENDC}"
        )
